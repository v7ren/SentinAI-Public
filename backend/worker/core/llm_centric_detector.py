"""
LLM-Centric Detection System

Philosophy: Use LLM as the primary security analyst, not just a pattern matcher.
- Minimal hard-coded rules (only clear policy decisions like "no DoS")
- LLM reasons about vulnerability exploitability
- LLM self-filters false positives during detection
- Single intelligent pass instead of multiple filters
"""

import re
from typing import Dict, Any, List, Tuple, Optional
import aiohttp

from .config import CHEAP_MODEL, SMART_MODEL, DETECTOR_MIN_CONFIDENCE, logger
from .deepseek_client import bridge_healthy, complete_json, llm_configured


class LLMCentricDetector:
    """
    Single-pass LLM detection with built-in false positive reasoning.
    
    Instead of:
      1. Detect with keywords → 2. Filter with regex → 3. Validate with LLM
    
    We do:
      1. Analyze with LLM (includes detection + false positive reasoning in one pass)
    
    The LLM is instructed to think like a security engineer and exclude obvious false positives.
    """

    def __init__(
        self,
        model: str = SMART_MODEL,  # Use smart model for primary detection
        confidence_threshold: float = DETECTOR_MIN_CONFIDENCE,
    ):
        self.model = model
        self.confidence_threshold = confidence_threshold

    async def detect_and_filter(
        self,
        session: aiohttp.ClientSession,
        filename: str,
        content: str,
        context_info: str = "",
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Single-pass LLM detection with integrated false positive filtering.
        
        The LLM is asked to:
        1. Identify vulnerabilities
        2. Score confidence (1-10)
        3. Provide reasoning for exploitability
        4. Self-filter obvious false positives
        
        Returns:
            (findings, detection_metadata)
        """
        
        system_prompt = self._build_detection_prompt()
        
        user_content = self._build_user_content(filename, content, context_info)
        timeout_seconds = 180

        if not (llm_configured() and await bridge_healthy(session)):
            return [], {"error": "bridge unavailable"}

        try:
            data = await complete_json(
                session,
                filename,
                system_prompt,
                user_content,
                timeout_seconds=timeout_seconds,
            )
            if not isinstance(data, dict) or data.get("status") == "UNKNOWN":
                return [], {"error": "invalid bridge response"}

            findings = data.get("findings") or []
            reasoning = data.get("analysis_reasoning", {})

            def _confidence(f: dict) -> float:
                v = f.get("confidence_score", f.get("confidence", None))
                if v is None:
                    return 8.0
                try:
                    return float(v)
                except (TypeError, ValueError):
                    return 8.0

            high_confidence_findings = [
                f for f in findings
                if _confidence(f) >= self.confidence_threshold
            ]
            if findings and not high_confidence_findings:
                high_confidence_findings = findings

            filtered_findings = self._apply_policy_exclusions(high_confidence_findings)
            metadata = {
                "total_detected": len(findings),
                "high_confidence": len(high_confidence_findings),
                "after_policy_filter": len(filtered_findings),
                "confidence_threshold": self.confidence_threshold,
                "llm_reasoning": reasoning,
                "excluded_count": len(findings) - len(filtered_findings),
                "source": "opencode-go",
            }
            logger.info(
                f"[LLM-CENTRIC] Detected {len(findings)}, "
                f"kept {len(filtered_findings)} after LLM self-filtering"
            )
            return filtered_findings, metadata
        except Exception as e:
            logger.warning("[LLM-CENTRIC] bridge failed: %s", e)
            return [], {"error": str(e)}

    def _build_detection_prompt(self) -> str:
        """
        Build the LLM-centric detection prompt.
        
        The key insight: Ask the LLM to THINK like a security engineer.
        Don't just pattern match - reason about exploitability.
        """
        prompt = """You are an expert security engineer performing code review. Analyze the code for security vulnerabilities.

YOUR TASK:
1. Identify security vulnerabilities in the code
2. For each finding, assess confidence (1-10) based on exploitability certainty
3. Reason about whether this is a true vulnerability or false positive
4. Report findings where confidence is >= __MIN_CONF__ and exploitability is plausible.
5. Actively look for chained attack paths, not just isolated bugs.

SECURITY ANALYSIS FRAMEWORK:

When analyzing, consider:
- Is there a concrete attack path? (Not theoretical)
- Can an attacker actually exploit this? (Not just "best practice")
- Is this a real security boundary violation?
- Would you raise this in a production code review?
- Does this combine with another weakness into a chain (for example IDOR -> privilege escalation -> RCE)?

VULNERABILITY CATEGORIES TO DETECT:
- Injection: SQLi, Command Injection, NoSQLi, LDAPi, XPathi, SSTI, XXE
- Authentication: Auth bypass, session fixation, weak password hashing
- Authorization: IDOR, privilege escalation, broken access control  
- Cryptography: Hardcoded secrets, weak algorithms (MD5/SHA1), JWT issues
- Data Exposure: Sensitive data logging, PII leaks, debug info exposure
- Code Execution: RCE via eval/exec, deserialization, unsafe reflection
- Input Validation: Path traversal, file upload, unsafe redirects

AUTOMATIC EXCLUSIONS (Policy - do NOT report these):
1. Denial of Service (DoS) or resource exhaustion attacks
2. Rate limiting concerns or throttling
3. Memory/CPU consumption issues
4. Log spoofing / log injection (outputting user input to logs)
5. Memory safety issues in Python/JavaScript (impossible)
6. Race conditions that are purely theoretical (no clear TOCTOU)
Report with MEDIUM/LOW when clearly exploitable: ReDoS (regex with user input and catastrophic backtracking), open redirects (user-controlled redirect URL), prototype pollution (merge with __proto__ affecting security checks), information disclosure (debug endpoints exposing secrets/tracebacks).

REASONING GUIDELINES:

Confidence Scoring (1-10):
- 10: Certain exploit, can write PoC immediately
- 8-9: Clear vulnerable pattern, proven attack path exists
- 7: Likely vulnerable, needs specific conditions but exploitable
- 5-6: Suspicious but might be false positive (DON'T REPORT)
- Below 5: Almost certainly false positive (DON'T REPORT)

When in doubt, EXCLUDE:
- "Better to miss a theoretical issue than flood with false positives"
- Only report what you'd confidently flag in a PR review

Common False Positives to EXCLUDE:
- JSON.parse() or response.json() → Safe standard parsing, NOT deserialization
- Hardcoded localhost URLs → Dev endpoints, NOT secrets
- React setState with server data → Auto-escaped by React, NOT XSS
- router.push() after login → Normal auth flow, NOT access control issue
- Client-side permission checks → Backend must validate, NOT a vuln
- Environment variables → Trusted in secure environments
- UUID validation → UUIDs are unguessable, don't need validation
- Plaintext passwords in seed data → "Hardcoded Credentials", NOT "Deserialization"

RESPONSE FORMAT:
{
    "findings": [
        {
            "type": "Vulnerability Type (e.g., SQL Injection)",
            "severity": "HIGH/MEDIUM/LOW",
            "confidence_score": 1-10,
            "line": 42,
            "function_name": "vulnerable_function",
            "vulnerable_code": "exact code snippet",
            "reasoning": "Why this is exploitable (attack path)",
            "false_positive_check": "Why this is NOT a false positive",
            "exploit_scenario": "How attacker would exploit this",
            "attack_scenario": {
                "attacker_profile": "who the attacker is",
                "preconditions": "what they need first",
                "actions": "what they do",
                "outcome": "what they gain"
            },
            "is_chain": true,
            "chain_summary": "short description of the multi-step attack path",
            "chain_components": ["step 1", "step 2", "step 3"],
            "cwe_id": "CWE-89"
        }
    ],
    "analysis_reasoning": {
        "total_scanned": "number of functions/patterns examined",
        "excluded_count": "how many potential findings were excluded as false positives",
        "exclusion_reasons": ["list of main reasons for exclusions"],
        "confidence_distribution": {"high": X, "medium": Y, "low": Z}
    }
}

IMPORTANT:
- Return EMPTY findings array if no plausible vulnerabilities are found
- Prefer precision, but keep borderline plausible findings for downstream validation
- Focus on exploitability and actionable signal
- Think like a pentester - would you actually exploit this?
- Use adversarial framing: assume the attacker is actively trying to break the code, chain weaknesses together, and move from entry point to impact."""
        return prompt.replace("__MIN_CONF__", str(int(DETECTOR_MIN_CONFIDENCE)))

    def _build_user_content(
        self,
        filename: str,
        content: str,
        context_info: str,
    ) -> str:
        """Build user content with code and context."""
        # Add line numbers
        numbered_lines = []
        for i, line in enumerate(content.splitlines(), 1):
            numbered_lines.append(f"{i:4}| {line}")
        numbered_code = "\n".join(numbered_lines)
        
        return f"""Analyze this code for security vulnerabilities:

File: {filename}

Project Context:
{context_info[:2000]}

Code to Analyze:
```
{numbered_code[:32000]}
```

Provide your analysis in the specified JSON format. Think carefully about each potential finding - is it really exploitable or just a pattern match?"""

    def _apply_policy_exclusions(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Only apply hard policy exclusions (not pattern matching).
        These are organizational policy decisions, not detection logic.
        """
        # Only exclude clear policy violations
        policy_exclusions = [
            r"(?i)(denial.of.service|dos.attack|resource.exhaustion)",
            r"(?i)(rate.limit|throttling)",  # Policy: we don't require rate limiting
            r"(?i)(redos|regex.dos)",  # Policy: regex dos not in scope
        ]
        
        kept = []
        for finding in findings:
            finding_type = finding.get("type", "")
            # Check if it matches policy exclusions
            should_exclude = False
            for pattern in policy_exclusions:
                if re.search(pattern, finding_type):
                    should_exclude = True
                    break
            
            if not should_exclude:
                kept.append(finding)
            else:
                logger.debug(f"[LLM-CENTRIC] Policy exclusion: {finding_type}")
        
        return kept


class SmartLLMFilter:
    """
    LLM-based filtering for already-detected findings.
    
    Instead of regex patterns, use LLM to judge each finding.
    More nuanced than hard rules, catches edge cases.
    """

    def __init__(
        self,
        model: str = CHEAP_MODEL,  # Use cheap model for filtering to save costs
        confidence_boost: bool = True,  # Ask LLM to re-evaluate confidence
    ):
        self.model = model
        self.confidence_boost = confidence_boost

    async def filter_findings_batch(
        self,
        session: aiohttp.ClientSession,
        findings: List[Dict[str, Any]],
        filename: str,
        file_content: str,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
        """
        Filter findings using LLM judgment (batch approach for efficiency).
        
        Instead of one LLM call per finding (expensive), send a batch
        and let the LLM judge them all together.
        """
        if not findings:
            return [], [], {"total": 0, "kept": 0, "excluded": 0}
        
        # For large batches, process in chunks
        if len(findings) > 10:
            return await self._filter_large_batch(session, findings, filename, file_content)
        
        system_prompt = """You are a senior security engineer reviewing vulnerability findings.

Your task: Judge each finding as TRUE POSITIVE or FALSE POSITIVE.

For each finding, evaluate:
1. Is there a concrete exploit path? (Not just a pattern match)
2. Would this actually be exploitable in production?
3. Is this a real security issue vs theoretical concern?

Confidence Guidelines:
- Keep findings with confidence >= 7 (true vulnerabilities)
- Exclude findings with confidence < 7 (likely false positives)

Common False Positive Patterns:
- React setState flagged as XSS (React auto-escapes)
- JSON.parse flagged as deserialization (it's safe)
- localhost URLs flagged as secrets (dev endpoints)
- Client-side auth checks (backend must validate)

Response format:
{
    "judgments": [
        {
            "finding_index": 0,
            "keep": true/false,
            "confidence": 1-10,
            "reasoning": "brief explanation",
            "false_positive_reason": "if excluding, explain why"
        }
    ]
}"""

        # Build findings list
        findings_text = []
        for i, f in enumerate(findings):
            findings_text.append(
                f"Finding {i}:\n"
                f"  Type: {f.get('type', 'Unknown')}\n"
                f"  Severity: {f.get('severity', 'MEDIUM')}\n"
                f"  Line: {f.get('line', 0)}\n"
                f"  Code: {f.get('vulnerable_code', 'N/A')[:100]}\n"
                f"  Description: {f.get('description', 'N/A')[:150]}\n"
            )
        
        user_content = f"""Review these {len(findings)} vulnerability findings from {filename}:

{chr(10).join(findings_text)}

Judge each finding. Return JSON with your judgments."""

        if not (llm_configured() and await bridge_healthy(session)):
            return findings, [], {"error": "bridge unavailable", "kept": len(findings)}

        try:
            data = await complete_json(
                session,
                f"filter:{filename}",
                system_prompt,
                user_content,
                timeout_seconds=180,
            )
            if not isinstance(data, dict) or data.get("status") == "UNKNOWN":
                return findings, [], {"error": "invalid filter response", "kept": len(findings)}
            return self._apply_judgments(findings, data.get("judgments") or [])
        except Exception as e:
            logger.exception("[SMART-FILTER] Batch filtering failed: %s", e)
            return findings, [], {"error": str(e), "kept": len(findings)}

    def _apply_judgments(
        self,
        findings: List[Dict[str, Any]],
        judgments: List[Dict[str, Any]],
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
        kept: List[Dict[str, Any]] = []
        excluded: List[Dict[str, Any]] = []

        for judgment in judgments:
            idx = judgment.get("finding_index", 0)
            if idx >= len(findings):
                continue

            finding = findings[idx]

            if judgment.get("keep", True):
                finding["_llm_judgment"] = {
                    "confidence": judgment.get("confidence", 7),
                    "reasoning": judgment.get("reasoning", ""),
                }
                kept.append(finding)
            else:
                finding["_llm_judgment"] = {
                    "excluded": True,
                    "reason": judgment.get("false_positive_reason", "Filtered by LLM"),
                }
                excluded.append(finding)

        judged_indices = {j.get("finding_index", 0) for j in judgments}
        for i, finding in enumerate(findings):
            if i not in judged_indices:
                kept.append(finding)

        metadata = {
            "total": len(findings),
            "kept": len(kept),
            "excluded": len(excluded),
            "reduction_rate": round(len(excluded) / max(1, len(findings)) * 100, 1),
        }
        return kept, excluded, metadata

    async def _filter_large_batch(
        self,
        session: aiohttp.ClientSession,
        findings: List[Dict[str, Any]],
        filename: str,
        file_content: str,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
        """Process large batches in chunks."""
        all_kept = []
        all_excluded = []
        
        chunk_size = 10
        for i in range(0, len(findings), chunk_size):
            chunk = findings[i:i + chunk_size]
            kept, excluded, _ = await self.filter_findings_batch(
                session, chunk, filename, file_content
            )
            all_kept.extend(kept)
            all_excluded.extend(excluded)
        
        metadata = {
            "total": len(findings),
            "kept": len(all_kept),
            "excluded": len(all_excluded),
            "chunks": (len(findings) + chunk_size - 1) // chunk_size,
        }
        
        return all_kept, all_excluded, metadata


# Convenience function for the main scanner
async def llm_centric_scan(
    session: aiohttp.ClientSession,
    filename: str,
    content: str,
    context_info: str = "",
    use_smart_filter: bool = True,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Perform LLM-centric detection and filtering.
    
    Flow:
    1. LLM Detection (with self-filtering)
    2. Optional: Smart LLM Filter (batch validation)
    3. Return high-confidence findings
    """
    # Phase 1: LLM Detection with self-filtering
    detector = LLMCentricDetector()
    findings, detection_meta = await detector.detect_and_filter(
        session, filename, content, context_info
    )
    
    if not findings or not use_smart_filter:
        return findings, detection_meta
    
    # Phase 2: Smart batch filtering (optional, for extra validation)
    smart_filter = SmartLLMFilter()
    kept, excluded, filter_meta = await smart_filter.filter_findings_batch(
        session, findings, filename, content
    )
    # Fail-open: if smart filter kept 0 but we had findings, use pre-filter list
    if findings and not kept:
        logger.warning(
            f"[LLM-CENTRIC] Smart filter kept 0 of {len(findings)}; using pre-filter findings (fail-open)"
        )
        kept = findings

    combined_meta = {
        "detection": detection_meta,
        "filtering": filter_meta,
        "final_count": len(kept),
    }
    
    return kept, combined_meta
