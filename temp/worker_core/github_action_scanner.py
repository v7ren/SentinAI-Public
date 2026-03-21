#!/usr/bin/env python3
"""
GitHub Action wrapper for SentinAI.
Combines SentinAI's multi-tier scanning with PR-focused workflow.
"""

import os
import sys
import json
import argparse
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
import requests

# Import SentinAI components
from backend.worker.core.config import CHEAP_MODEL, WORKER_SECRET
from backend.worker.core.findings_filter import FindingsFilter


class GitHubActionScanner:
    """
    GitHub Action scanner that wraps SentinAI's multi-tier system.
    """

    def __init__(self, scan_type: str = "3", comment_pr: bool = True):
        self.scan_type = scan_type
        self.comment_pr = comment_pr
        self.github_token = os.environ.get('GITHUB_TOKEN')
        self.pr_number = os.environ.get('PR_NUMBER')
        self.repo = os.environ.get('GITHUB_REPOSITORY')

        # Initialize filter
        # Claude/Anthropic integration removed.
        api_key = None
        self.filter = FindingsFilter(
            use_hard_exclusions=True,
            use_claude_filtering=api_key is not None,
            api_key=api_key
        )

    def get_changed_files(self) -> List[Dict[str, Any]]:
        """Get list of changed files in PR using git."""
        files = []

        try:
            # Get changed files from git diff
            result = subprocess.run(
                ['git', 'diff', '--name-only', 'HEAD^', 'HEAD'],
                capture_output=True,
                text=True
            )
            changed = result.stdout.strip().split('\n')

            for filepath in changed:
                if not filepath or not Path(filepath).exists():
                    continue

                # Skip binary files and common ignore patterns
                if self._should_skip(filepath):
                    continue

                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    files.append({
                        'filename': filepath,
                        'content': content,
                        'status': 'modified'
                    })
                except Exception as e:
                    print(f"[WARN] Could not read {filepath}: {e}", file=sys.stderr)

        except Exception as e:
            print(f"[WARN] Git diff failed: {e}", file=sys.stderr)
            # Fallback: scan all files
            return self._get_all_files()

        return files

    def _should_skip(self, filepath: str) -> bool:
        """Check if file should be skipped."""
        skip_patterns = [
            'node_modules/', '__pycache__/', '.git/',
            'dist/', 'build/', '.next/', '.nuxt/',
            'vendor/', 'coverage/', '.coverage',
            'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
            '.min.js', '.min.css', '.map',
            '.png', '.jpg', '.jpeg', '.gif', '.svg',
            '.woff', '.woff2', '.ttf', '.eot',
            '.zip', '.tar', '.gz', '.rar',
            '.exe', '.dll', '.so', '.dylib'
        ]

        for pattern in skip_patterns:
            if pattern in filepath:
                return True
        return False

    def _get_all_files(self) -> List[Dict[str, Any]]:
        """Get all valid source files (fallback)."""
        files = []
        valid_extensions = {
            '.py', '.js', '.ts', '.tsx', '.jsx', '.html',
            '.php', '.java', '.c', '.cpp', '.go', '.rb',
            '.vue', '.rs', '.kt', '.swift', '.sol',
            '.yaml', '.yml', '.json', '.sql'
        }

        for ext in valid_extensions:
            for filepath in Path('.').rglob(f'*{ext}'):
                if self._should_skip(str(filepath)):
                    continue

                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    if len(content) > 1_000_000:  # Skip files > 1MB
                        continue

                    files.append({
                        'filename': str(filepath),
                        'content': content,
                        'status': 'existing'
                    })
                except Exception:
                    continue

        return files

    def scan_file(self, file_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Scan a single file through SentinAI pipeline."""
        from backend.worker.core.ai_tier1 import scan_tier_1_basic
        from backend.worker.core.ai_tier2 import scan_tier_2_standard
        from backend.worker.core.ai_tier3 import scan_tier_3_advanced
        from backend.worker.core.utils import (
            get_code_context_and_fingerprint,
            find_keywords_with_lines
        )

        import aiohttp
        import asyncio

        async def run_scan():
            async with aiohttp.ClientSession() as session:
                filename = file_data['filename']
                content = file_data['content']

                print(f"[SCAN] Scanning {filename}...", file=sys.stderr)

                # Tier 1: Quick triage (CHEAP_MODEL)
                tier1_result = await scan_tier_1_basic(
                    session, filename, content, ""  # No context for speed
                )

                status = tier1_result.get("status", "UNKNOWN")

                # If safe and Tier 1 requested, return early
                if self.scan_type == "1":
                    return tier1_result

                # If safe, skip expensive tiers
                if status == "SAFE":
                    tier1_result["scan_type"] = f"{self.scan_type} (Optimized)"
                    return tier1_result

                # Tier 2/3: Deep analysis
                if status == "VULNERABLE":
                    if self.scan_type == "2":
                        result = await scan_tier_2_standard(
                            session, filename, content, "", tier1_result
                        )
                    else:
                        result = await scan_tier_3_advanced(
                            session, filename, content, "", tier1_result
                        )

                    # Apply false positive filtering
                    if result.get("status") == "VULNERABLE":
                        findings = result.get("findings", [])
                        filtered_findings, summary = self.filter.filter_findings(
                            findings, {"filename": filename}
                        )[:2]

                        if filtered_findings:
                            result["findings"] = filtered_findings
                            result["_filter_summary"] = summary
                        else:
                            # All findings filtered out - mark as safe
                            result["status"] = "SAFE"
                            result["findings"] = []
                            result["note"] = "Findings filtered as likely false positives"

                    return result

                return tier1_result

        return asyncio.run(run_scan())

    def run(self) -> Dict[str, Any]:
        """Run the complete scan pipeline."""
        print("[INFO] Starting SentinAI Security Scan...", file=sys.stderr)
        print(f"[INFO] Scan Type: Tier {self.scan_type}", file=sys.stderr)

        # Get files to scan
        files = self.get_changed_files()
        print(f"[INFO] Found {len(files)} files to scan", file=sys.stderr)

        if not files:
            return {
                "status": "SUCCESS",
                "findings": [],
                "stats": {"files_scanned": 0, "vulnerabilities": 0}
            }

        # Scan each file
        all_findings = []
        files_scanned = 0

        for file_data in files:
            result = self.scan_file(file_data)
            files_scanned += 1

            if result and result.get("status") == "VULNERABLE":
                for finding in result.get("findings", []):
                    finding["file"] = file_data['filename']
                    all_findings.append(finding)

        # Final filtering pass across all findings
        if all_findings:
            filtered_findings, summary = self.filter.filter_findings(
                all_findings,
                {"repo": self.repo, "pr_number": self.pr_number}
            )[:2]

            all_findings = filtered_findings

        # Build results
        results = {
            "status": "SUCCESS",
            "scan_type": self.scan_type,
            "findings": all_findings,
            "findings_count": len(all_findings),
            "stats": {
                "files_scanned": files_scanned,
                "vulnerabilities": len(all_findings),
                "high_severity": len([f for f in all_findings if f.get("severity") == "HIGH"]),
                "medium_severity": len([f for f in all_findings if f.get("severity") == "MEDIUM"]),
                "low_severity": len([f for f in all_findings if f.get("severity") == "LOW"])
            }
        }

        # Save results
        with open('sentinai-results.json', 'w') as f:
            json.dump(results, f, indent=2)

        print(f"[INFO] Scan complete: {len(all_findings)} findings", file=sys.stderr)

        return results


def main():
    parser = argparse.ArgumentParser(description='SentinAI GitHub Action Scanner')
    parser.add_argument('--scan-type', default='3', choices=['1', '2', '3'],
                        help='Scan tier (1=Basic, 2=Standard, 3=Advanced)')
    parser.add_argument('--comment-pr', type=lambda x: x.lower() == 'true',
                        default=True, help='Comment on PR with results')
    parser.add_argument('--output-format', default='github',
                        choices=['github', 'json', 'sarif'],
                        help='Output format')

    args = parser.parse_args()

    scanner = GitHubActionScanner(
        scan_type=args.scan_type,
        comment_pr=args.comment_pr
    )

    results = scanner.run()

    # Output for GitHub Actions
    if args.output_format == 'github':
        # Set outputs for subsequent steps
        print(f"findings_count={results['findings_count']}")

        # Fail if high severity findings
        high_count = results['stats']['high_severity']
        if high_count > 0:
            print(f"::error::{high_count} HIGH severity vulnerabilities found!")
            sys.exit(1)

    elif args.output_format == 'json':
        print(json.dumps(results, indent=2))

    sys.exit(0)


if __name__ == '__main__':
    main()
