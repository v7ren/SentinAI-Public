"""
False Positive Filtering System (deterministic + confidence-based)
Integrates with SentinAI's multi-tier scanning pipeline.

Also includes HARD DETECTION RULES for deterministic vulnerability detection
that doesn't require AI analysis (secrets, SQLi patterns, XSS patterns, etc.)
"""

import os
import re
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
import json

from .config import PHASE1_CONFIDENCE_THRESHOLD, HIGH_RECALL_MODE, FP_FILTER_STRICTNESS, logger

# =============================================================================
# HARD DETECTION RULES (Deterministic vulnerability detection)
# These rules generate findings without requiring AI analysis
# =============================================================================

HARD_DETECTION_PATTERNS = {
    # SQL Injection patterns (MISS 3 fix)
    "SQL_INJECTION": [
        # % string formatting with SQL keywords
        {
            "pattern": r'["\']\s*(?:SELECT|INSERT|UPDATE|DELETE)\s+.*%\s*\(',
            "confidence": 90,  # 0-100 scale
            "severity": "HIGH",
            "cwe": "CWE-89",
            "description": "SQL query constructed with % string formatting - vulnerable to SQL injection",
        },
        # f-string with SQL keywords
        {
            "pattern": r'f["\'][^"\']*(?:SELECT|INSERT|UPDATE|DELETE)\s+[^"\']*\{[^}]+\}',
            "confidence": 90,  # 0-100 scale
            "severity": "HIGH",
            "cwe": "CWE-89",
            "description": "SQL query constructed with f-string - vulnerable to SQL injection",
        },
        # .format() with SQL keywords
        {
            "pattern": r'["\'][^"\']*(?:SELECT|INSERT|UPDATE|DELETE)\s+[^"\']*["\']\.format\(',
            "confidence": 90,  # 0-100 scale
            "severity": "HIGH",
            "cwe": "CWE-89",
            "description": "SQL query constructed with .format() - vulnerable to SQL injection",
        },
        # String concatenation with SQL keywords and variables
        {
            "pattern": r'["\'][^"\']*(?:SELECT|INSERT|UPDATE|DELETE|WHERE)\s+[^"\']*["\']\s*\+\s*\w+',
            "confidence": 85,  # 0-100 scale
            "severity": "HIGH",
            "cwe": "CWE-89",
            "description": "SQL query constructed with string concatenation - vulnerable to SQL injection",
        },
    ],

    # Hardcoded Secrets patterns (MISS 1 fix)
    "HARDCODED_SECRET": [
        # SECRET_KEY assignment with hardcoded string
        {
            "pattern": r'^\s*SECRET_KEY\s*=\s*["\'][^"\']+["\']\s*$',
            "confidence": 95,  # 0-100 scale
            "severity": "HIGH",
            "cwe": "CWE-798",
            "description": "Hardcoded SECRET_KEY detected in configuration file",
        },
        # API_KEY assignment with hardcoded string
        {
            "pattern": r'^\s*\w*API_KEY\w*\s*=\s*["\'][^"\']{8,}["\']\s*$',
            "confidence": 90,  # 0-100 scale
            "severity": "HIGH",
            "cwe": "CWE-798",
            "description": "Hardcoded API key detected",
        },
        # PASSWORD assignment (not env vars)
        {
            "pattern": r'^\s*\w*(?:PASSWORD|PASSWD|PWD)\w*\s*=\s*["\'][^"\']{4,}["\']\s*$',
            "confidence": 85,  # 0-100 scale
            "severity": "HIGH",
            "cwe": "CWE-798",
            "description": "Hardcoded password detected",
            "exclusions": ["os.environ", "getenv", "config(", "request."],
        },
        # TOKEN assignment
        {
            "pattern": r'^\s*\w*(?:TOKEN|AUTH_TOKEN|ACCESS_TOKEN)\w*\s*=\s*["\'][^"\']{8,}["\']\s*$',
            "confidence": 90,  # 0-100 scale
            "severity": "HIGH",
            "cwe": "CWE-798",
            "description": "Hardcoded authentication token detected",
        },
    ],

    # XSS patterns (MISS 2 fix)
    "REFLECTED_XSS": [
        # request parameter concatenated into HTML string
        {
            "pattern": r'request\.(?:args|form|json|data)\.(?:get|\[)[^)]+\].*\+.*["\']<\w+',
            "confidence": 85,  # 0-100 scale
            "severity": "HIGH",
            "cwe": "CWE-79",
            "description": "User input from request parameters concatenated into HTML output - reflected XSS vulnerability",
        },
        # render_template_string with request data
        {
            "pattern": r'render_template_string\s*\([^)]*request\.(?:args|form|json|data)',
            "confidence": 90,  # 0-100 scale
            "severity": "HIGH",
            "cwe": "CWE-79",
            "description": "User input passed directly to render_template_string - SSTI/XSS vulnerability",
        },
        # make_response with HTML and request data
        {
            "pattern": r'make_response\s*\([^)]*["\']<[^"\']+[\"\'][^)]*request\.(?:args|form|json|data)',
            "confidence": 85,  # 0-100 scale
            "severity": "HIGH",
            "cwe": "CWE-79",
            "description": "User input in HTML response construction - reflected XSS vulnerability",
        },
    ],

    # Command Injection patterns (MISS 4 fix)
    "COMMAND_INJECTION": [
        # subprocess with request data
        {
            "pattern": r'subprocess\.(?:getoutput|call|run|Popen)\s*\([^)]*request\.(?:args|form|json|data|get_json)',
            "confidence": 95,  # 0-100 scale
            "severity": "CRITICAL",
            "cwe": "CWE-78",
            "description": "User input passed directly to subprocess - command injection vulnerability",
        },
        # os.system with request data
        {
            "pattern": r'os\.(?:system|popen)\s*\([^)]*request\.(?:args|form|json|data|get_json)',
            "confidence": 95,  # 0-100 scale
            "severity": "CRITICAL",
            "cwe": "CWE-78",
            "description": "User input passed directly to os.system/os.popen - command injection vulnerability",
        },
    ],
}

# Config file patterns where hardcoded secrets are most critical
CONFIG_FILE_PATTERNS = [
    r"config\.py$",
    r"settings\.py$",
    r"local_settings\.py$",
    r"production_settings\.py$",
    r"constants\.py$",
    r"secrets\.py$",
    r"\.env",
]


def apply_hard_detection_rules(filepath: str, content: str, language: str = "python") -> List[Dict[str, Any]]:
    """
    Apply hard detection rules to find vulnerabilities without AI analysis.

    This is a deterministic pre-scan pass that catches common vulnerability patterns
    with high confidence. These findings bypass AI detection and go straight to
    the validation phase.

    Args:
        filepath: Relative path to the file being scanned
        content: File content as string
        language: Programming language of the file

    Returns:
        List of findings generated by hard detection rules
    """
    findings = []
    lines = content.splitlines()
    basename = os.path.basename(filepath).lower()
    is_config_file = any(re.search(pattern, filepath, re.IGNORECASE) for pattern in CONFIG_FILE_PATTERNS)

    for vuln_type, patterns in HARD_DETECTION_PATTERNS.items():
        for pattern_def in patterns:
            pattern = pattern_def["pattern"]
            confidence = pattern_def["confidence"]
            severity = pattern_def["severity"]
            cwe = pattern_def["cwe"]
            description = pattern_def["description"]
            exclusions = pattern_def.get("exclusions", [])

            # For secrets, only check config-like files
            if vuln_type == "HARDCODED_SECRET" and not is_config_file:
                # Also check if file contains "config" or "settings" in path
                if "config" not in filepath.lower() and "settings" not in filepath.lower():
                    continue

            for line_num, line in enumerate(lines, 1):
                line_stripped = line.strip()

                # Skip comments
                if line_stripped.startswith("#") or line_stripped.startswith("//"):
                    continue

                # Check for pattern match
                if re.search(pattern, line, re.IGNORECASE):
                    # Check exclusions
                    should_exclude = False
                    for exclusion in exclusions:
                        if exclusion in line:
                            should_exclude = True
                            break

                    if should_exclude:
                        continue

                    # Extract the vulnerable code snippet
                    vulnerable_code = line.strip()[:200]  # Limit length

                    # Create finding
                    finding = {
                        "type": vuln_type,
                        "subtype": cwe,
                        "cwe_id": cwe,
                        "description": description,
                        "severity": severity,
                        "confidence_score": confidence,
                        "line": line_num,
                        "file": filepath,
                        "vulnerable_code": vulnerable_code,
                        "function_name": _extract_function_name(lines, line_num),
                        "is_hard_rule_finding": True,  # Mark as from hard detection
                        "_detection_rule": pattern_def,
                    }
                    findings.append(finding)

    return findings


def _extract_function_name(lines: List[str], line_num: int) -> Optional[str]:
    """Extract the function name that contains the given line."""
    # Search backwards from line_num to find function definition
    for i in range(line_num - 1, -1, -1):
        if i >= len(lines):
            continue
        line = lines[i]
        # Python function
        match = re.match(r'^\s*def\s+(\w+)\s*\(', line)
        if match:
            return match.group(1)
        # JavaScript/TypeScript function
        match = re.match(r'^\s*(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\()', line)
        if match:
            return match.group(1) or match.group(2)
    return None


# =============================================================================
# HARD EXCLUSION RULES (adapted from a conservative SAST baseline)
# =============================================================================
#
# These patterns are categorized into:
# 1. HARD_PATTERNS (structurally impossible) - always excluded regardless of mode
# 2. SOFT_PATTERNS (high uncertainty categories) - marked with reduced confidence in high-recall mode
#
# In default mode: soft patterns typically exclude findings
# In HIGH_RECALL_MODE: soft patterns mark findings with "_fp_soft_flag" and reduced confidence
#

# HARD_PATTERNS: These are structurally impossible or provably non-applicable
# category patterns that should ALWAYS be excluded
HARD_FALSE_POSITIVE_PATTERNS = {
    # Memory safety in non-C/C++ (impossible in Python/JS)
    "MEMORY_SAFETY_NON_C": [
        r"(?i)(buffer.overflow|stack.overflow|heap.overflow)",
        r"(?i)(oob)\s+(read|write|access)",
        r"(?i)(out.?of.?bounds?)",
        r"(?i)(memory.safety|memory.corruption)",
        r"(?i)(use.?after.?free|double.?free|null.?pointer.?dereference)",
        r"(?i)(segmentation.fault|segfault|memory.violation)",
        r"(?i)(bounds.check|boundary.check|array.bounds)",
        r"(?i)(integer.overflow|integer.underflow|integer.conversion)",
        r"(?i)arbitrary.?(memory.read|pointer.dereference|memory.address|memory.pointer)",
    ],
    
    # Very narrow, proven hallucinations - patterns that are known false mappings
    "PROVEN_HALLUCINATION": [
        # JSON.parse is NEVER insecure deserialization in standard usage
        r"(?i)(json\.parse|response\.json|JSON\.parse).*insecure.deserialization",
        # React setState without dangerouslySetInnerHTML is not XSS
        r"(?i)(setState|useState).*xss(?!.*dangerouslySetInnerHTML)",
    ],
}

# SOFT_PATTERNS: These are high-uncertainty categories that become "informational" 
# in high-recall mode instead of being hard-dropped
SOFT_FALSE_POSITIVE_PATTERNS = {
    # DoS / Resource exhaustion - often valid but low practical impact
    "DOS": [
        r"(?i)(denial.of.service|dos\.attack|resource.exhaustion|memory.exhaustion|cpu.exhaustion)",
        r"(?i)(rate.limit|rate.limiting|throttling)",
        r"(?i)(slowloris|infinite.loop|billion.laughs)",
        r"(?i)(exhaust|overwhelm|overload).*?(resource|memory|cpu)",
        r"(?i)(infinite|unbounded).*?(loop|recursion)",
    ],
    
    # Secrets on disk - may be valid, context-dependent
    "SECRETS_ON_DISK": [
        r"(?i)(secret|password|credential|token|api.key).*stored.*(?:file|disk|filesystem)",
    ],
    
    # Low impact / Informational - often valid but low priority
    "LOW_IMPACT": [
        r"(?i)(information.disclosure|information.leak).*version",
        r"(?i)(information.disclosure|information.leak).*path",
        r"(?i)(clickjacking|x.frame.options)",
        r"(?i)(verbose.error|error.disclosure)",
        r"(?i)(cors|cross.origin).*?misconfiguration",
    ],
    
    # Test files - valid code paths, not necessarily safe
    "TEST_CODE": [
        r"(?i)(test.*file|spec.*file|__tests__|\.test\.|\.spec\.)",
        r"(?i)(mock|stub|fixture|test.data)",
        r"(?i)test.*\.py$",
        r"(?i).*_test\.py$",
        r"(?i).*\.test\.ts$",
        r"(?i).*\.test\.tsx$",
    ],
    
    # Regex injection / ReDoS - valid but often low practical impact in modern engines
    "REGEX_INJECTION": [
        r"(?i)(regex|regular.expression).*injection",
        r"(?i)(regex|regular.expression).*denial.of.service",
        r"(?i)(regex|regular.expression).*flooding",
        r"(?i)(redos|catastrophic.backtracking)",
    ],
    
    # Open redirect - can be valid depending on context
    "OPEN_REDIRECT": [
        r"(?i)(open.redirect|unvalidated.redirect)",
        r"(?i)(redirect.(attack|exploit|vulnerability))",
        r"(?i)(malicious.redirect)",
    ],
    
    # Log injection / Log spoofing - valid but often low impact
    "LOG_SPOOFING": [
        r"(?i)(log.*injection|log.*spoofing|log.*forging)",
        r"(?i)(newline.*log|log.*newline|inject.*log)",
    ],
    
    # SSRF in client-side code - may be SSRF if server initiates request
    "SSRF_CLIENTSIDE": [
        r"(?i)(ssrf|server.?side.?request.?forgery)",
    ],
}

# Backwards compatibility: merge both for legacy code paths
HARDCODED_FALSE_POSITIVE_PATTERNS = {**HARD_FALSE_POSITIVE_PATTERNS, **SOFT_FALSE_POSITIVE_PATTERNS}

# =============================================================================
# SPECIFIC FALSE POSITIVE RULES (Pattern matching for common LLM hallucinations)
# =============================================================================

FRONTEND_FALSE_POSITIVE_RULES = [
    {
        "name": "json_parse_not_deser",
        "description_pattern": r"(?i)(json\.parse|response\.json|JSON\.parse)",
        "vuln_code_pattern": r"(?i)(JSON\.parse|response\.json\(\)|\.json\(\))",
        "type_match": r"(?i)(insecure.deserialization|deserialization)",
        "reason": "JSON.parse/response.json() is safe standard JSON parsing, not insecure deserialization (baseline precedent #1)",
    },
    {
        "name": "localstorage_not_deser",
        "description_pattern": r"(?i)(localStorage\.(setItem|getItem)|sessionStorage)",
        "vuln_code_pattern": r"(?i)(localStorage\.(setItem|getItem)|JSON\.stringify.*localStorage)",
        "type_match": r"(?i)(insecure.deserialization|deserialization)",
        "reason": "localStorage with JSON.stringify/parse is standard browser storage, not deserialization (baseline precedent #1)",
    },
    {
        "name": "hardcoded_localhost_url",
        "description_pattern": r"(?i)(localhost|127\.0\.0\.1).*?(hardcoded|url|endpoint)",
        "vuln_code_pattern": r"(?i)(http://localhost|http://127\.0\.0\.1)",
        "type_match": r"(?i)(hardcoded.secret|hardcoded.credential|secret)",
        "reason": "Hardcoded localhost/dev URLs are not secrets (baseline precedent #2)",
    },
    {
        "name": "react_setstate_not_xss",
        "description_pattern": r"(?i)(set\w+\(.*?\)|setState).*?(xss|cross.site)",
        "vuln_code_pattern": r"(?i)(set\w+\(data\.|setError\(|setQuery|setResult|setState)",
        "type_match": r"(?i)(xss|cross.site.scripting)",
        "extra_check": "no_dangerous_html",
        "reason": "React auto-escapes rendered values by default; setState is not XSS unless dangerouslySetInnerHTML is used (baseline precedent #6)",
    },
    {
        "name": "router_push_not_access_control",
        "description_pattern": r"(?i)(router\.push|redirect|navigate).*?(access.control|unauthorized|without.*check)",
        "vuln_code_pattern": r"(?i)(router\.push|router\.replace|navigate\(|redirect\()",
        "type_match": r"(?i)(access.control|authorization|broken.access)",
        "reason": "Client-side navigation after auth is normal pattern, not an access control vulnerability (baseline precedent #8)",
    },
    {
        "name": "window_open_not_crypto",
        "description_pattern": r"(?i)(window\.open)",
        "vuln_code_pattern": r"(?i)(window\.open)",
        "type_match": r"(?i)(insecure.crypto|weak.crypto|cryptograph)",
        "reason": "window.open() is not related to cryptography",
    },
    {
        "name": "fetch_api_call_not_vuln",
        "description_pattern": r"(?i)(fetch|axios).*?(insecure|vulnerable)",
        "vuln_code_pattern": r"(?i)(await\s+fetch\(|axios\.(get|post))",
        "type_match": r"(?i)(insecure.deserialization)",
        "reason": "Making HTTP requests with fetch/axios is standard, not insecure deserialization",
    },
    {
        "name": "anonymous_fallback_not_access_control",
        "description_pattern": r"(?i)(anonymous|default.*value).*?(access|unauthorized)",
        "vuln_code_pattern": r"(?i)(\|\|\s*['\"]anonymous['\"]|\?\?\s*['\"]anonymous['\"])",
        "type_match": r"(?i)(access.control)",
        "reason": "Fallback values for optional fields are not access control vulnerabilities on the client side (baseline precedent #8)",
    },
    {
        "name": "uuid_not_need_validation",
        "description_pattern": r"(?i)(uuid|guid).*?(validation|verify|check)",
        "vuln_code_pattern": r"(?i)(uuid|UUID|guid|GUID)",
        "type_match": r"(?i)(input.validation|missing.validation)",
        "reason": "UUIDs can be assumed to be unguessable and do not need to be validated (baseline precedent #2)",
    },
    {
        "name": "env_var_trusted",
        "description_pattern": r"(?i)(environment.variable|env\.var|process\.env|os\.environ)",
        "vuln_code_pattern": r"(?i)(process\.env\.|os\.environ|os\.getenv)",
        "type_match": r"(?i)(injection|tainted|untrusted)",
        "reason": "Environment variables and CLI flags are trusted values in secure environments (baseline precedent #3)",
    },
    {
        "name": "react_xss_without_dangerous",
        "description_pattern": r"(?i)(xss|cross.site.scripting).*react",
        "vuln_code_pattern": r"(?i)(react|jsx|tsx)(?!.*dangerouslySetInnerHTML)(?!.*bypassSecurityTrustHtml)",
        "type_match": r"(?i)(xss|cross.site.scripting)",
        "reason": "React and Angular are generally secure against XSS unless using dangerouslySetInnerHTML or similar bypass methods (baseline precedent #6)",
    },
    {
        "name": "clientside_auth_not_vuln",
        "description_pattern": r"(?i)(client.?side|frontend).*?(auth|authentication|permission)",
        "vuln_code_pattern": r"(?i)(localStorage.*role|sessionStorage.*role|client.*admin)",
        "type_match": r"(?i)(access.control|authentication|authorization)",
        "reason": "A lack of permission checking in client-side code is not a vulnerability - backend must validate (baseline precedent #8)",
    },
    {
        "name": "non_pii_logging_not_vuln",
        "description_pattern": r"(?i)(logging|log).*?(data|info|input)",
        "vuln_code_pattern": r"(?i)(console\.log|logger\.|log\.|print\()",
        "type_match": r"(?i)(information.disclosure|data.exposure|sensitive.data)",
        "reason": "Logging non-PII data is not a vulnerability. Only secrets, passwords, or PII in logs is a concern (baseline precedent #11)",
    },
    {
        "name": "client_fetch_not_ssrf",
        "description_pattern": r"(?i)(fetch|axios|xmlhttprequest|http.request).*?(ssrf|server.side.request)",
        "vuln_code_pattern": r"(?i)(fetch\(|axios\.(get|post|put|delete|patch)|XMLHttpRequest|\.open\()",
        "type_match": r"(?i)(ssrf|server.?side.?request.?forgery)",
        "reason": "fetch()/axios/XMLHttpRequest in client-side code is a browser HTTP call, NOT SSRF. SSRF only applies to server-side HTTP requests.",
    },
    {
        "name": "nextjs_public_env_not_secret",
        "description_pattern": r"(?i)(next_public|NEXT_PUBLIC).*?(secret|exposed|leak)",
        "vuln_code_pattern": r"(?i)NEXT_PUBLIC_\w+",
        "type_match": r"(?i)(hardcoded.secret|information.disclosure|sensitive.data)",
        "reason": "NEXT_PUBLIC_ environment variables are intentionally exposed to the client in Next.js - this is by design, not a vulnerability.",
    },
    {
        "name": "react_usestate_not_xss",
        "description_pattern": r"(?i)(useState|useEffect|useMemo|useCallback).*?(xss|cross.site)",
        "vuln_code_pattern": r"(?i)(useState|useEffect|useMemo|useCallback|useRef)\s*\(",
        "type_match": r"(?i)(xss|cross.site.scripting)",
        "reason": "React hooks (useState, useEffect, etc.) rendering data are NOT XSS. React auto-escapes output unless dangerouslySetInnerHTML is used.",
    },
    {
        "name": "map_filter_not_vuln",
        "description_pattern": r"(?i)(\.map\(|\.filter\(|\.reduce\().*?(injection|xss)",
        "vuln_code_pattern": r"(?i)\.(map|filter|reduce|forEach)\s*\(",
        "type_match": r"(?i)(injection|xss|cross.site.scripting)",
        "reason": "Array methods (.map, .filter, .reduce) are safe functional operations, not injection vectors in React/JSX.",
    },
]

# =============================================================================
# CRITICAL VULNERABILITY PATTERNS (Should NEVER be filtered)
# =============================================================================

CRITICAL_VULNERABILITY_PATTERNS = [
    r"(?i)(remote.code.execution|rce|arbitrary.code.execution)",
    r"(?i)(sql.injection|sqli)",
    r"(?i)(command.injection|os.command)",
    r"(?i)(deserialization|unserialize|pickle\.loads|yaml\.load\([^)]*Loader)",
    r"(?i)(authentication.bypass|privilege.escalation)",
    r"(?i)(ssrf|server.side.request.forgery)",
    r"(?i)(path.traversal|directory.traversal|lfi|local.file.inclusion)",
    r"(?i)(render_template_string|dangerouslySetInnerHTML)",
    r"(?i)(eval\(|exec\(|Function\()",
    r"(?i)(subprocess.*shell\s*=\s*True|os\.system|os\.popen)",
    r"(?i)(hardcoded.*secret.*key|app\.secret_key|SECRET_KEY.*=)",
    r"(?i)(jwt.*none.algorithm|algorithm.confusion)",
    r"(?i)(xxe|xml.external.entity)",
    r"(?i)(ssti|template.injection)",
    r"(?i)(nosql.injection|mongodb.injection)",
    r"(?i)(ldap.injection)",
    r"(?i)(xpath.injection)",
    r"(?i)(csv.injection|formula.injection)",
    r"(?i)(redos|regex.dos|catastrophic.backtracking)",
]

# Patterns in vulnerable_code that confirm a REAL vulnerability
CRITICAL_CODE_PATTERNS = [
    r"cursor\.execute\(f[\"']",
    r"cursor\.execute\(.*?format\(",
    r"cursor\.execute\(.*?\+.*?\+",
    r"cursor\.execute\(.*?%.*?%",
    r"pickle\.loads?\(",
    r"yaml\.load\([^)]*(?<!Safe)Loader",
    r"eval\(",
    r"exec\(",
    r"subprocess\.\w+\(.*shell\s*=\s*True",
    r"render_template_string\(",
    r"requests\.(get|post|put|delete)\([^)]*\+",
    r"requests\.(get|post|put|delete)\([^)]*f[\"']",
    r"os\.path\.join\(.*?\+.*?\+",
    r"\.execute\(\s*query\s*\)",
    r"dangerouslySetInnerHTML\s*=\s*\{",
    r"dangerouslySetInnerHTML.*__html",
    r"\.innerHTML\s*=",
    r"hashlib\.md5\(",
    r"hashlib\.sha1\(",
    r"app\.secret_key\s*=",
    r"SECRET_KEY\s*=",
    r"jwt\.decode\([^)]*algorithms?\s*=",
    r"ET\.fromstring\(",
    r"xml\..*\.parse\(",
    r"Template\([^)]*render",
    r"jinja2\.Template\(",
    r"db\.\w+\.find\([^)]*\+",
    r"db\.\w+\.find\([^)]*f[\"']",
    r"\.aggregate\(\[",
    r"ldap.*filter.*=.*f[\"']",
    r"\.search\([^)]*\+",
    r"\.search\([^)]*%",
]

# File extensions for memory safety exclusions
C_CPP_EXTENSIONS = {'.c', '.cc', '.cpp', '.h', '.hpp'}
HTML_EXTENSIONS = {'.html', '.htm'}
# All client-side / frontend extensions — SSRF and certain backend vulns don't apply here
FRONTEND_EXTENSIONS = {'.html', '.htm', '.tsx', '.jsx', '.ts', '.js', '.vue', '.svelte'}


@dataclass
class FilterResult:
    """Result of filtering a finding."""
    keep: bool
    reason: str
    category: str
    confidence_adjustment: float


class FindingsFilter:
    """
    Multi-layer false positive filter.
    Combines hard rules with confidence thresholding.
    """

    def __init__(
        self,
        use_hard_exclusions: bool = True,
        use_llm_filtering: bool = False,
        confidence_threshold: float = PHASE1_CONFIDENCE_THRESHOLD,
    ):
        self.use_hard_exclusions = use_hard_exclusions
        self.use_llm_filtering = use_llm_filtering
        self.confidence_threshold = confidence_threshold

    def filter_findings(
        self,
        findings: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Dict[str, Any], Dict[str, int]]:
        """
        Filter findings through multiple layers.

        Args:
            findings: Raw findings from scanner
            context: PR/repo context for better filtering

        Returns:
            Tuple of (success, filtered_results, stats)
        """
        if not findings:
            return True, {"filtered_findings": [], "excluded_findings": []}, {"total": 0, "kept": 0}

        kept_findings = []
        excluded_findings = []

        # Layer 1: Hard exclusions (fast, rule-based)
        if self.use_hard_exclusions:
            for finding in findings:
                result = self._apply_hard_rules(finding)
                if result.keep:
                    kept_findings.append(finding)
                else:
                    excluded_findings.append({
                        **finding,
                        "_exclusion_reason": result.reason,
                        "_exclusion_category": result.category
                    })
        else:
            kept_findings = findings

        # Layer 2: Confidence threshold filtering
        final_kept = []
        for finding in kept_findings:
            confidence = self._get_confidence_score(finding)
            if confidence >= self.confidence_threshold:
                finding["_confidence_score"] = confidence
                final_kept.append(finding)
            else:
                excluded_findings.append({
                    **finding,
                    "_exclusion_reason": f"Confidence {confidence} below threshold {self.confidence_threshold}",
                    "_exclusion_category": "LOW_CONFIDENCE"
                })

        # Build stats
        stats = {
            "total": len(findings),
            "hard_excluded": len([e for e in excluded_findings if e.get("_exclusion_category") != "LOW_CONFIDENCE"]),
            "confidence_filtered": len([e for e in excluded_findings if e.get("_exclusion_category") == "LOW_CONFIDENCE"]),
            "kept": len(final_kept)
        }

        return True, {
            "filtered_findings": final_kept,
            "excluded_findings": excluded_findings,
            "analysis_summary": self._generate_summary(final_kept, excluded_findings)
        }, stats

    def _get_confidence_score(self, finding: Dict[str, Any]) -> float:
        """Extract and normalize confidence score from finding to 0-10 scale for threshold comparison."""
        # Try different confidence fields
        confidence = finding.get("confidence_score", finding.get("confidence", 0))

        if isinstance(confidence, (int, float)):
            # Handle different scales:
            # 0-1 scale: multiply by 10 -> 0-10
            # 0-100 scale: divide by 10 -> 0-10
            # 0-10 scale: keep as is
            if 0 < confidence <= 1.0:
                return confidence * 10  # Convert 0-1 to 0-10
            elif confidence > 10:
                return confidence / 10  # Convert 0-100 to 0-10
            else:
                return float(confidence)  # Already 0-10

        # Default to high confidence if not specified (conservative approach)
        return 10.0

    def _apply_hard_rules(self, finding: Dict[str, Any]) -> FilterResult:
        """Apply fast, hardcoded exclusion rules (baseline policy)."""

        description = finding.get("description", "")
        finding_type = finding.get("type", "")
        finding_subtype = finding.get("subtype", "")
        severity = finding.get("severity", "").upper()
        file_path = finding.get("file", "")
        vuln_code = finding.get("vulnerable_code", "")

        combined_text = f"{description} {finding_type} {finding_subtype}"
        
        # Get file extension
        file_ext = ""
        if "." in file_path:
            file_ext = f".{file_path.lower().split('.')[-1]}"

        # =========================================================================
        # RULE 0: Critical code patterns override - NEVER filter these
        # =========================================================================
        for code_pattern in CRITICAL_CODE_PATTERNS:
            if re.search(code_pattern, vuln_code):
                return FilterResult(
                    keep=True,
                    reason="Critical code pattern detected in vulnerable_code",
                    category="CRITICAL_CODE_OVERRIDE",
                    confidence_adjustment=0.0
                )

        # =========================================================================
        # RULE 1: Critical vulnerability descriptions - NEVER filter these
        # =========================================================================
        for critical_pattern in CRITICAL_VULNERABILITY_PATTERNS:
            if re.search(critical_pattern, combined_text):
                return FilterResult(
                    keep=True,
                    reason="Critical vulnerability pattern - bypasses all filters",
                    category="CRITICAL_OVERRIDE",
                    confidence_adjustment=0.0
                )

        # =========================================================================
        # RULE 2: Markdowndocumentation files - always exclude
        # =========================================================================
        if file_path.lower().endswith('.md'):
            return FilterResult(
                keep=False,
                reason="Finding in Markdown documentation file",
                category="DOCUMENTATION_EXCLUSION",
                confidence_adjustment=0.0
            )

        # =========================================================================
        # RULE 3: Frontend/React specific false positives
        # =========================================================================
        for fp_rule in FRONTEND_FALSE_POSITIVE_RULES:
            type_matches = re.search(fp_rule["type_match"], finding_type)
            if not type_matches:
                continue

            desc_matches = re.search(fp_rule["description_pattern"], combined_text) if fp_rule.get("description_pattern") else False
            code_matches = re.search(fp_rule["vuln_code_pattern"], vuln_code) if fp_rule.get("vuln_code_pattern") else False

            if desc_matches or code_matches:
                extra = fp_rule.get("extra_check")
                if extra == "no_dangerous_html":
                    if "dangerouslySetInnerHTML" in vuln_code or "dangerouslySetInnerHTML" in description:
                        continue
                    if "__html" in vuln_code:
                        continue

                return FilterResult(
                    keep=False,
                    reason=fp_rule["reason"],
                    category=f"FP_FILTER_{fp_rule['name'].upper()}",
                    confidence_adjustment=-0.5
                )

        # =========================================================================
        # RULE 4: DoS / Rate Limiting / Resource exhaustion (baseline policy)
        # =========================================================================
        for pattern in HARDCODED_FALSE_POSITIVE_PATTERNS["DOS"]:
            if re.search(pattern, combined_text):
                return FilterResult(
                    keep=False,
                    reason="DoS/rate limiting/resource exhaustion excluded by baseline policy",
                    category="DOS_EXCLUSION",
                    confidence_adjustment=-0.3
                )

        # =========================================================================
        # RULE 5: Regex injection only (exclude generic "regex injection" FP; keep ReDoS when pattern is user-controlled)
        # =========================================================================
        for pattern in HARDCODED_FALSE_POSITIVE_PATTERNS["REGEX_INJECTION"]:
            if re.search(pattern, combined_text):
                # Allow ReDoS / catastrophic backtracking through for recall (user-controlled pattern = real finding)
                if re.search(r"(?i)(redos|catastrophic\.backtracking|user.?controlled\.?pattern)", combined_text):
                    break
                return FilterResult(
                    keep=False,
                    reason="Regex injection (non-ReDoS) excluded by policy",
                    category="REGEX_INJECTION_EXCLUSION",
                    confidence_adjustment=-0.3
                )

        # =========================================================================
        # RULE 6: Open redirect (allow MEDIUM/HIGH; only exclude LOW severity with low confidence)
        # =========================================================================
        for pattern in HARDCODED_FALSE_POSITIVE_PATTERNS["OPEN_REDIRECT"]:
            if re.search(pattern, combined_text):
                confidence = self._get_confidence_score(finding)
                if severity == "LOW" and confidence < 7.0:
                    return FilterResult(
                        keep=False,
                        reason="Open redirect (low impact, low confidence) excluded",
                        category="OPEN_REDIRECT_EXCLUSION",
                        confidence_adjustment=-0.2
                    )
                # Allow MEDIUM/HIGH or high-confidence LOW through for better recall
                break

        # =========================================================================
        # RULE 7: Log spoofing (baseline excludes)
        # =========================================================================
        for pattern in HARDCODED_FALSE_POSITIVE_PATTERNS["LOG_SPOOFING"]:
            if re.search(pattern, combined_text):
                return FilterResult(
                    keep=False,
                    reason="Log spoofing/injection excluded by baseline policy",
                    category="LOG_SPOOFING_EXCLUSION",
                    confidence_adjustment=-0.2
                )

        # =========================================================================
        # RULE 8: Memory safety in non-C/C++ code (impossible in Python/JS/TS)
        # =========================================================================
        if file_ext not in C_CPP_EXTENSIONS:
            for pattern in HARDCODED_FALSE_POSITIVE_PATTERNS["MEMORY_SAFETY_NON_C"]:
                if re.search(pattern, combined_text):
                    return FilterResult(
                        keep=False,
                        reason=f"Memory safety finding in {file_ext} file (not C/C++ - impossible)",
                        category="MEMORY_SAFETY_NON_C",
                        confidence_adjustment=-0.3
                    )

        # =========================================================================
        # RULE 9: SSRF in frontend/client-side files (HTML, TSX, JSX, TS, JS, Vue, Svelte)
        # fetch()/axios in browser-side code is NOT SSRF — server can't be hijacked from client
        # =========================================================================
        if file_ext in FRONTEND_EXTENSIONS:
            for pattern in HARDCODED_FALSE_POSITIVE_PATTERNS["SSRF_CLIENTSIDE"]:
                if re.search(pattern, combined_text):
                    return FilterResult(
                        keep=False,
                        reason=f"SSRF finding in frontend {file_ext} file (client-side HTTP calls are not SSRF)",
                        category="SSRF_CLIENTSIDE_EXCLUSION",
                        confidence_adjustment=-0.3
                    )

        # =========================================================================
        # RULE 10: Secrets on disk (handled by secret scanners)
        # =========================================================================
        for pattern in HARDCODED_FALSE_POSITIVE_PATTERNS["SECRETS_ON_DISK"]:
            if re.search(pattern, combined_text):
                return FilterResult(
                    keep=False,
                    reason="Secrets on disk handled by separate scanner",
                    category="SECRETS_EXCLUSION",
                    confidence_adjustment=-0.2
                )

        # =========================================================================
        # RULE 11: Test files
        # =========================================================================
        for pattern in HARDCODED_FALSE_POSITIVE_PATTERNS["TEST_CODE"]:
            if re.search(pattern, file_path):
                return FilterResult(
                    keep=False,
                    reason="Finding in test file",
                    category="TEST_FILE_EXCLUSION",
                    confidence_adjustment=0.0
                )

        # =========================================================================
        # RULE 12: Low impact informational findings (only if low confidence)
        # =========================================================================
        for pattern in HARDCODED_FALSE_POSITIVE_PATTERNS["LOW_IMPACT"]:
            if re.search(pattern, combined_text):
                confidence = self._get_confidence_score(finding)
                if confidence < 7.0:
                    return FilterResult(
                        keep=False,
                        reason="Low-impact informational finding with insufficient confidence",
                        category="LOW_IMPACT_EXCLUSION",
                        confidence_adjustment=-0.1
                    )

        return FilterResult(
            keep=True,
            reason="Passed hard exclusion rules",
            category="PASSED",
            confidence_adjustment=0.0
        )

    def _generate_summary(
        self,
        kept: List[Dict[str, Any]],
        excluded: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate analysis summary."""

        # Count by category
        category_counts = {}
        for f in excluded:
            cat = f.get("_exclusion_category", "UNKNOWN")
            category_counts[cat] = category_counts.get(cat, 0) + 1

        # Severity breakdown for kept findings
        severity_breakdown = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "CRITICAL": 0}
        confidence_distribution = {"high (8-10)": 0, "medium (5-7)": 0, "low (<5)": 0}
        
        for f in kept:
            sev = f.get("severity", "MEDIUM").upper()
            severity_breakdown[sev] = severity_breakdown.get(sev, 0) + 1
            
            conf = f.get("_confidence_score", 10)
            if conf >= 8:
                confidence_distribution["high (8-10)"] += 1
            elif conf >= 5:
                confidence_distribution["medium (5-7)"] += 1
            else:
                confidence_distribution["low (<5)"] += 1

        total = len(kept) + len(excluded)
        
        return {
            "total_findings": total,
            "excluded_count": len(excluded),
            "kept_count": len(kept),
            "reduction_percentage": round((len(excluded) / max(1, total)) * 100, 1),
            "exclusion_breakdown": category_counts,
            "severity_breakdown": severity_breakdown,
            "confidence_distribution": confidence_distribution,
            "confidence_threshold": self.confidence_threshold,
        }


def apply_filtering_to_results(
    findings: List[Dict[str, Any]],
    scan_type: str,
    confidence_threshold: float = PHASE1_CONFIDENCE_THRESHOLD,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Convenience function to apply filtering to scan results.

    Args:
        findings: Raw findings from Tier 1/2/3
        scan_type: "1", "2", or "3"
        confidence_threshold: Minimum confidence to keep a finding

    Returns:
        Tuple of (filtered_findings, filtering_summary)
    """
    filter_instance = FindingsFilter(
        use_hard_exclusions=True,
        confidence_threshold=confidence_threshold,
    )

    success, results, stats = filter_instance.filter_findings(findings)

    if success:
        return results["filtered_findings"], results["analysis_summary"]
    else:
        # If filtering fails, return original findings
        return findings, {"error": "Filtering failed", "kept_count": len(findings)}
