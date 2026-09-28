# backend/worker/core/dependency_scanner.py
"""
Dependency Scanner — Parses package manifests and correlates with OSV (CVE) data.

Supported: package.json (+ lock), requirements.txt, Pipfile.lock, go.mod, Cargo.toml.
Finds which files in the codebase import vulnerable packages so findings can be
prioritized by actual exposure.
"""

import json
import logging
import re
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

OSV_API_URL = "https://api.osv.dev/v1/query"


@dataclass
class DependencyFinding:
    """A vulnerable dependency with optional correlation to source files."""

    package_name: str
    version_installed: str
    version_constraint: str | None  # e.g. ">=1.0,<2"
    ecosystem: str  # "npm", "pypi", "go", "crates.io"
    cve_ids: list[str] = field(default_factory=list)
    severity: str = "UNKNOWN"
    summary: str = ""
    affected_files: list[str] = field(default_factory=list)
    manifest_path: str = ""


def _parse_package_json(manifest_path: str, content: str) -> list[tuple[str, str, str]]:
    """Returns list of (package_name, version_or_range, ecosystem)."""
    try:
        data = json.loads(content)
        deps = list(data.get("dependencies", {}).items()) + list(data.get("devDependencies", {}).items())
        out = []
        for name, ver in deps:
            if isinstance(ver, str) and not ver.startswith("file:"):
                out.append((name, ver.strip(), "npm"))
        return out
    except json.JSONDecodeError:
        return []


def _parse_requirements_txt(content: str) -> list[tuple[str, str, str]]:
    """Returns list of (package_name, version_or_spec, ecosystem)."""
    out = []
    for line in content.splitlines():
        line = line.strip().split("#")[0].strip()
        if not line or line.startswith("-"):
            continue
        # name==1.0, name>=1.0, name~=1.0
        m = re.match(r"([a-zA-Z0-9_-]+)\s*([=<>!~]+.*)?", line)
        if m:
            name, spec = m.group(1), (m.group(2) or "").strip()
            out.append((name, spec or "any", "pypi"))
    return out


def _parse_go_mod(content: str) -> list[tuple[str, str, str]]:
    """Returns list of (module_path, version, ecosystem)."""
    out = []
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("require ("):
            continue
        if line.startswith("require "):
            parts = line.split()
            if len(parts) >= 2:
                out.append((parts[1], parts[2] if len(parts) > 2 else "any", "go"))
        if " " in line and not line.startswith("//") and not line.startswith(")"):
            parts = line.split()
            if len(parts) >= 2:
                out.append((parts[0], parts[1], "go"))
    return out


def _parse_cargo_toml(content: str) -> list[tuple[str, str, str]]:
    """Returns list of (crate_name, version_or_wildcard, ecosystem)."""
    out = []
    in_deps = False
    for line in content.splitlines():
        line = line.strip()
        if line == "[dependencies]" or line == "[dev-dependencies]":
            in_deps = True
            continue
        if in_deps and line.startswith("["):
            in_deps = False
        if in_deps and "=" in line and not line.startswith("#"):
            key, _, rest = line.partition("=")
            key = key.strip().strip('"')
            if key.startswith("["):
                continue
            ver = "any"
            if '"' in rest:
                m = re.search(r'"([^"]*)"', rest)
                if m:
                    ver = m.group(1)
            out.append((key, ver, "crates.io"))
    return out


def query_osv(package_name: str, version: str, ecosystem: str, api_url: str = OSV_API_URL) -> list[dict]:
    """Query OSV API for vulnerabilities affecting this package/version."""
    if version in ("any", "", "*"):
        return []
    payload = {
        "package": {"name": package_name, "ecosystem": ecosystem},
        "version": version.split(",")[0].strip().strip("=<>!~"),
    }
    try:
        req = urllib.request.Request(
            api_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data.get("vulns", [])
    except Exception as e:
        logger.debug("OSV query failed for %s %s: %s", package_name, version, e)
        return []


def find_import_sites(package_name: str, file_contents: dict[str, str], ecosystem: str) -> list[str]:
    """Find file paths that import/require the given package."""
    out = []
    pats = []
    if ecosystem == "npm":
        pats = [
            re.compile(rf'require\s*\(\s*["\'](?:{re.escape(package_name)}|@[^/]+/{re.escape(package_name)})["\']\s*\)', re.I),
            re.compile(rf'from\s+["\'](?:{re.escape(package_name)}|@[^/]+/{re.escape(package_name)})["\']', re.I),
            re.compile(rf'import\s+.*from\s+["\'](?:{re.escape(package_name)}|@[^/]+/{re.escape(package_name)})["\']', re.I),
        ]
    elif ecosystem == "pypi":
        pats = [
            re.compile(rf'import\s+{re.escape(package_name)}\b', re.I),
            re.compile(rf'from\s+{re.escape(package_name)}\s+import', re.I),
        ]
    elif ecosystem == "go":
        pats = [re.compile(rf'["\'](?:.*/)?{re.escape(package_name)}["\']', re.I)]
    elif ecosystem == "crates.io":
        pats = [re.compile(rf'use\s+{re.escape(package_name)}\b', re.I),
                re.compile(rf'extern\s+crate\s+{re.escape(package_name)}\b', re.I)]
    for path, content in file_contents.items():
        for p in pats:
            if p.search(content):
                out.append(path)
                break
    return out


class DependencyScanner:
    """
    Scans manifest files and optionally correlates with OSV and source files.
    """

    def __init__(self, osv_api_url: str = OSV_API_URL):
        self.osv_api_url = osv_api_url

    def parse_manifest(self, manifest_path: str, content: str) -> list[tuple[str, str, str]]:
        """Parse manifest content; return list of (name, version, ecosystem)."""
        path = Path(manifest_path)
        name_lower = path.name.lower()
        if "package.json" in name_lower:
            return _parse_package_json(manifest_path, content)
        if "requirements" in name_lower and (path.suffix == ".txt" or "requirements" in name_lower):
            return _parse_requirements_txt(content)
        if "go.mod" in name_lower:
            return _parse_go_mod(content)
        if "cargo.toml" in name_lower:
            return _parse_cargo_toml(content)
        if "pipfile" in name_lower:
            try:
                data = json.loads(content) if content.strip().startswith("{") else {}
                deps = {**data.get("default", {}), **data.get("develop", {})}
                return [(k, v.get("version", "any") if isinstance(v, dict) else str(v), "pypi") for k, v in deps.items()]
            except Exception:
                return []
        return []

    def scan(
        self,
        manifest_path: str,
        manifest_content: str,
        file_contents: dict[str, str] | None = None,
        query_osv_enabled: bool = True,
    ) -> list[DependencyFinding]:
        """
        Parse manifest, optionally query OSV for each dependency, and optionally
        correlate with file_contents to list affected files.
        """
        file_contents = file_contents or {}
        tuples = self.parse_manifest(manifest_path, manifest_content)
        findings: list[DependencyFinding] = []
        for pkg, ver, eco in tuples:
            vulns = query_osv(pkg, ver, eco, self.osv_api_url) if query_osv_enabled else []
            if not vulns:
                continue
            cve_ids = []
            severity = "UNKNOWN"
            summary = ""
            for v in vulns:
                for ref in v.get("references", []) or []:
                    if "CVE-" in str(ref.get("url", "")):
                        cve_ids.append(ref.get("url", "").split("CVE-")[-1].split("/")[0].split("?")[0])
                if not cve_ids and v.get("id"):
                    cve_ids.append(v["id"])
                if not summary and v.get("summary"):
                    summary = v["summary"][:500]
                db = v.get("database_specific") or {}
                if isinstance(db, dict) and db.get("severity"):
                    severity = str(db["severity"]).upper()
                for sev in (v.get("severity") or []):
                    if isinstance(sev, dict) and sev.get("severity"):
                        severity = str(sev["severity"]).upper()
                        break
            affected = find_import_sites(pkg, file_contents, eco) if file_contents else []
            findings.append(
                DependencyFinding(
                    package_name=pkg,
                    version_installed=ver,
                    version_constraint=ver,
                    ecosystem=eco,
                    cve_ids=list(dict.fromkeys(cve_ids)),
                    severity=severity,
                    summary=summary,
                    affected_files=affected,
                    manifest_path=manifest_path,
                )
            )
        return findings
