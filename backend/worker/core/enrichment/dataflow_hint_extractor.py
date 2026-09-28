"""
DataflowHintExtractor - Detects taint sources, user input entry points,
and dangerous sinks including hardcoded secrets and XSS-prone HTML output.

Identifies variables that receive user-controlled input from various
sources (request parameters, environment variables, CLI args, etc.)
for each supported language. Also detects:
- Hardcoded secrets in config files
- Taint flows to dangerous sinks (HTML output, subprocess, eval, etc.)
"""

import os
import re
from typing import Dict, List, Optional, Tuple

from ..config import logger


class DataflowHintExtractor:
    """Extracts taint sources, dataflow hints, secrets, and dangerous sinks from code."""

    # =========================================================================
    # SECRETS DETECTION PATTERNS
    # =========================================================================
    # Variable names that suggest secret values
    SECRET_VAR_PATTERNS = [
        r"SECRET_KEY",
        r"SECRET",
        r"API_KEY",
        r"APIKEY",
        r"API_SECRET",
        r"PASSWORD",
        r"PASSWD",
        r"PASS",
        r"TOKEN",
        r"AUTH_TOKEN",
        r"ACCESS_TOKEN",
        r"REFRESH_TOKEN",
        r"PRIVATE_KEY",
        r"PRIVATEKEY",
        r"ADMIN_KEY",
        r"SERVICE_TOKEN",
        r"INTERNAL_TOKEN",
        r"DB_PASSWORD",
        r"DATABASE_PASSWORD",
        r"REDIS_PASSWORD",
        r"CONN_STRING",
        r"CONNECTION_STRING",
    ]
    SECRET_VAR_REGEX = re.compile(
        r"^\s*(\w*(?:" + "|".join(SECRET_VAR_PATTERNS) + r")\w*)\s*=\s*([\"'])(.+?)\2",
        re.IGNORECASE | re.MULTILINE
    )

    # Config file patterns that should be checked for secrets
    CONFIG_FILE_PATTERNS = [
        r"config\.py",
        r"settings\.py",
        r"constants\.py",
        r"config\.js",
        r"config\.ts",
        r"\.env\.",
        r"local_settings",
        r"production_settings",
        r"secrets\.",
        r"credentials",
    ]
    CONFIG_FILE_REGEX = re.compile("|".join(CONFIG_FILE_PATTERNS), re.IGNORECASE)

    # =========================================================================
    # TAINT SOURCE PATTERNS
    # =========================================================================
    TAINT_PATTERNS = {
        "python": {
            "request.args": re.compile(r"request\.args(?:\.get|\[)"),
            "request.form": re.compile(r"request\.form(?:\.get|\[)"),
            "request.json": re.compile(r"request\.json"),
            "request.data": re.compile(r"request\.data"),
            "request.files": re.compile(r"request\.files"),
            "request.headers": re.compile(r"request\.headers"),
            "request.cookies": re.compile(r"request\.cookies"),
            "request.stream": re.compile(r"request\.stream"),
            "os.environ": re.compile(r"os\.environ"),
            "sys.argv": re.compile(r"sys\.argv"),
            "input()": re.compile(r"\binput\s*\(\s*\)"),
            "argparse": re.compile(r"args\.\w+"),
            "click.argument": re.compile(r"@click\.(argument|option)"),
            "socket.recv": re.compile(r"\.recv\s*\("),
            "file.read": re.compile(r"\.read\s*\("),
        },
        "javascript": {
            "req.body": re.compile(r"req\.body"),
            "req.query": re.compile(r"req\.query"),
            "req.params": re.compile(r"req\.params"),
            "req.headers": re.compile(r"req\.headers"),
            "req.cookies": re.compile(r"req\.cookies"),
            "req.files": re.compile(r"req\.files"),
            "process.env": re.compile(r"process\.env"),
            "event.data": re.compile(r"event\.data"),
            "window.prompt": re.compile(r"window\.prompt|prompt\s*\("),
            "document.location": re.compile(r"document\.location|window\.location"),
            "URLSearchParams": re.compile(r"URLSearchParams"),
            "FormData": re.compile(r"FormData"),
        },
        "typescript": {
            "req.body": re.compile(r"req\.body"),
            "req.query": re.compile(r"req\.query"),
            "req.params": re.compile(r"req\.params"),
            "req.headers": re.compile(r"req\.headers"),
            "req.cookies": re.compile(r"req\.cookies"),
            "req.files": re.compile(r"req\.files"),
            "process.env": re.compile(r"process\.env"),
            "event.data": re.compile(r"event\.data"),
            "window.prompt": re.compile(r"window\.prompt|prompt\s*\("),
            "document.location": re.compile(r"document\.location|window\.location"),
            "URLSearchParams": re.compile(r"URLSearchParams"),
            "FormData": re.compile(r"FormData"),
        },
        "java": {
            "request.getParameter": re.compile(r"request\.getParameter"),
            "request.getHeader": re.compile(r"request\.getHeader"),
            "System.getenv": re.compile(r"System\.getenv"),
            "args[]": re.compile(r"\bargs\["),
            "Scanner": re.compile(r"Scanner\s*\(\s*System\.in\s*\)"),
            "BufferedReader": re.compile(r"BufferedReader.*System\.in"),
            "ServletInputStream": re.compile(r"ServletInputStream"),
            "MultipartFile": re.compile(r"MultipartFile"),
        },
        "go": {
            "r.URL.Query": re.compile(r"r\.URL\.Query\s*\(\s*\)"),
            "r.FormValue": re.compile(r"r\.FormValue\s*\("),
            "r.PostFormValue": re.compile(r"r\.PostFormValue\s*\("),
            "r.Header.Get": re.compile(r"r\.Header\.Get\s*\("),
            "r.Header.Values": re.compile(r"r\.Header\.Values\s*\("),
            "os.Getenv": re.compile(r"os\.Getenv\s*\("),
            "os.Args": re.compile(r"os\.Args"),
            "bufio.Scanner": re.compile(r"bufio\.NewScanner"),
            "flag.String": re.compile(r"flag\.\w+\s*\("),
        },
    }

    # Variable assignment patterns to extract the variable name
    VAR_ASSIGNMENT_PATTERNS = {
        "python": re.compile(
            r"(\w+)\s*=\s*(.+)",
            re.MULTILINE
        ),
        "javascript": re.compile(
            r"(?:const|let|var)?\s*(\w+)\s*=\s*(.+)",
            re.MULTILINE
        ),
        "typescript": re.compile(
            r"(?:const|let|var)?\s*(\w+)\s*=\s*(.+)",
            re.MULTILINE
        ),
        "java": re.compile(
            r"(?:\w+(?:<[^>]+>)?)\s+(\w+)\s*=\s*(.+);",
            re.MULTILINE
        ),
        "go": re.compile(
            r"(\w+)\s*(:?)=\s*(.+)",
            re.MULTILINE
        ),
    }

    # =========================================================================
    # DANGEROUS SINK PATTERNS (for XSS, Command Injection, SQLi detection)
    # =========================================================================
    DANGEROUS_SINKS = {
        "python": {
            # XSS sinks - HTML response construction
            "html_concat": re.compile(
                r"([\"']<\w+[^\"']*>[\"']\s*\+|f[\"'][^\"']*<\w+|\+\s*[\"'][^\"']*<\w+)"
            ),
            "render_template_string": re.compile(r"render_template_string\s*\("),
            "make_response_html": re.compile(
                r"make_response\s*\([^)]*\)\s*,\s*\d+\s*,\s*\{[^}]*text/html"
            ),
            "html_string_concat": re.compile(
                r"[\"']<!DOCTYPE\s+html|<html|<body|<div|<script|<p[^>]*>[\"']"
            ),
            # Command injection sinks
            "subprocess_shell": re.compile(
                r"subprocess\.(?:getoutput|call|run|Popen|check_output)\s*\(|os\.(?:system|popen)"
            ),
            # SQL injection sinks
            "sql_string_formatting": re.compile(
                r'(?:execute|query|raw)\s*\(\s*(?:f["\']|["\'][^"\']*%s|["\'][^"\']*\{)',
                re.IGNORECASE
            ),
            # Code injection sinks
            "eval_exec": re.compile(r"\b(?:eval|exec)\s*\("),
            "pickle_loads": re.compile(r"pickle\.loads?\s*\("),
            "yaml_load": re.compile(r"yaml\.load\s*\("),
        },
        "javascript": {
            "exec_shell": re.compile(
                r"(?:child_process\.(?:exec|execSync|spawn)|require\s*\(\s*[\"']child_process[\"']\s*\)\.exec)\s*\("
            ),
            "eval": re.compile(r"\beval\s*\("),
            "innerHTML": re.compile(r"\.innerHTML\s*="),
            "document_write": re.compile(r"document\.write\s*\("),
            "dangerouslySetInnerHTML": re.compile(r"dangerouslySetInnerHTML\s*=\s*\{\s*__html"),
            "window_location": re.compile(r"window\.location(?:\.href)?\s*="),
            "router_push_replace": re.compile(r"router\.(?:push|replace)\s*\("),
        },
        "typescript": {
            "exec_shell": re.compile(
                r"(?:child_process\.(?:exec|execSync|spawn)|require\s*\(\s*[\"']child_process[\"']\s*\)\.exec)\s*\("
            ),
            "eval": re.compile(r"\beval\s*\("),
            "innerHTML": re.compile(r"\.innerHTML\s*="),
            "document_write": re.compile(r"document\.write\s*\("),
            "dangerouslySetInnerHTML": re.compile(r"dangerouslySetInnerHTML\s*=\s*\{\s*__html"),
            "window_location": re.compile(r"window\.location(?:\.href)?\s*="),
            "router_push_replace": re.compile(r"router\.(?:push|replace)\s*\("),
        },
    }

    # HTML output indicators for XSS detection
    HTML_OUTPUT_INDICATORS = [
        r"<!DOCTYPE\s+html",
        r"<html",
        r"<body",
        r"<div",
        r"<p>",
        r"<script",
        r"<head",
        r"<title",
        r"Content-Type.*text/html",
    ]
    HTML_OUTPUT_REGEX = re.compile("|".join(HTML_OUTPUT_INDICATORS), re.IGNORECASE)

    # Known dangerous sink functions for cross-file taint tracking
    DANGEROUS_SINK_FUNCTIONS = {
        "subprocess.getoutput",
        "subprocess.call",
        "subprocess.run",
        "subprocess.Popen",
        "subprocess.check_output",
        "os.system",
        "os.popen",
        "os.execv",
        "commands.getoutput",
        "eval",
        "exec",
        "pickle.loads",
        "yaml.load",
        "render_template_string",
        "execute",
        "raw",
    }

    def _detect_language(self, filepath: str) -> Optional[str]:
        """Detect programming language from file extension."""
        ext = os.path.splitext(filepath)[1].lower()
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".java": "java",
            ".go": "go",
        }
        return language_map.get(ext)

    def _extract_variable_from_line(self, line: str, language: str) -> Optional[str]:
        """Extract the variable being assigned on a line."""
        pattern = self.VAR_ASSIGNMENT_PATTERNS.get(language)
        if not pattern:
            return None

        match = pattern.match(line.strip())
        if match:
            return match.group(1)
        return None

    def _extract_secrets(self, filepath: str, content: str, language: str, scan_id: Optional[str] = None) -> List[Dict]:
        """
        Extract hardcoded secrets from config files and Python files.

        Returns list of secret findings with variable name, line number, and type.
        """
        secrets = []

        # Only check config-like files for secrets
        is_config_file = self.CONFIG_FILE_REGEX.search(filepath) is not None
        is_python_config = language == "python" and (
            "config" in filepath.lower() or
            "settings" in filepath.lower() or
            "constants" in filepath.lower()
        )

        if not (is_config_file or is_python_config):
            return secrets

        lines = content.splitlines()

        # Check each line for secret patterns
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()

            # Skip comments
            if language == "python" and line_stripped.startswith("#"):
                continue

            # Check for secret variable assignments with hardcoded string values
            for pattern in self.SECRET_VAR_PATTERNS:
                # Match variable assignment with quoted string value
                # Defensive: treat pattern as literal to avoid regex injection / crashes (re.error).
                safe_pat = re.escape(pattern)
                try:
                    regex = re.compile(
                        rf"^\s*(\w*{safe_pat}\w*)\s*=\s*([\"'])(.+?)\2",
                        re.IGNORECASE
                    )
                except re.error as e:
                    # Don't let a single bad pattern crash enrichment for the entire file.
                    # This can happen if patterns are user-controlled or accidentally malformed.
                    logger.warning(
                        f"[ENRICHMENT] Bad regex pattern while scanning secrets. "
                        f"scan_id={scan_id!r} file={filepath!r} pattern={pattern!r} error={e}"
                    )
                    continue
                match = regex.search(line)
                if match:
                    var_name = match.group(1)
                    secret_value = match.group(3)

                    # Skip environment variable lookups and function calls
                    if any(skip in secret_value for skip in [
                        "os.environ", "getenv", "os.get", "config(",
                        "settings(", "request.", "self.", "args[",
                    ]):
                        continue

                    # Skip if it's a placeholder/template value
                    if any(placeholder in secret_value.lower() for placeholder in [
                        "your_", "placeholder", "<", ">", "{{", "}}",
                        "change_", "replace_", "todo", "fixme",
                    ]):
                        continue

                    secrets.append({
                        "variable": var_name,
                        "line": line_num,
                        "line_content": line.strip()[:100],  # Truncate for safety
                        "secret_type": self._classify_secret_type(var_name),
                    })
                    break  # Found a secret on this line, move to next

        return secrets

    def _classify_secret_type(self, var_name: str) -> str:
        """Classify the type of secret based on variable name."""
        name_upper = var_name.upper()
        if "SECRET_KEY" in name_upper:
            return "SECRET_KEY"
        elif "API_KEY" in name_upper or "APIKEY" in name_upper:
            return "API_KEY"
        elif "TOKEN" in name_upper:
            return "TOKEN"
        elif "PASSWORD" in name_upper or "PASSWD" in name_upper:
            return "PASSWORD"
        elif "PRIVATE_KEY" in name_upper:
            return "PRIVATE_KEY"
        else:
            return "GENERIC_SECRET"

    def _extract_sink_argument(self, line: str, sink_name: str, language: str) -> Optional[str]:
        """Extract the first argument/variable passed to a dangerous sink (e.g. exec(x) -> x)."""
        if language == "python":
            if sink_name == "subprocess_shell":
                m = re.search(r"(?:subprocess\.\w+|os\.(?:system|popen))\s*\(\s*([^),]+)", line)
                return m.group(1).strip().split(".")[-1] if m else None
            if sink_name == "eval_exec":
                m = re.search(r"\b(?:eval|exec)\s*\(\s*([^),]+)", line)
                return m.group(1).strip().split(".")[-1] if m else None
            if sink_name in ("pickle_loads", "yaml_load"):
                m = re.search(r"(?:pickle\.loads?|yaml\.load)\s*\(\s*([^),]+)", line)
                return m.group(1).strip().split(".")[-1] if m else None
        if language in ("javascript", "typescript"):
            if sink_name == "exec_shell":
                m = re.search(r"(?:exec|execSync|spawn)\s*\(\s*([^),]+)", line)
                return m.group(1).strip().split(".")[-1] if m else None
            if sink_name == "eval":
                m = re.search(r"eval\s*\(\s*([^)]+)\)", line)
                return m.group(1).strip().split(".")[-1] if m else None
            if sink_name in ("innerHTML", "document_write", "dangerouslySetInnerHTML"):
                m = re.search(r"(?:innerHTML|__html)\s*[=:]\s*([^;}\s]+)", line) or re.search(
                    r"document\.write\s*\(\s*([^)]+)\)", line
                )
                return m.group(1).strip().split(".")[-1] if m else None
            if sink_name in ("window_location", "router_push_replace"):
                m = re.search(r"(?:location\.href|location)\s*=\s*([^;]+)", line) or re.search(
                    r"router\.(?:push|replace)\s*\(\s*([^),]+)", line
                )
                return m.group(1).strip().split(".")[-1] if m else None
        return None

    def _sink_type_for_sink_name(self, sink_name: str, language: str) -> Optional[str]:
        """Map sink pattern name to vulnerability type."""
        if language == "python":
            if sink_name in ["html_concat", "render_template_string", "make_response_html"]:
                return "XSS_HTML_OUTPUT"
            if sink_name == "subprocess_shell":
                return "COMMAND_INJECTION"
            if sink_name == "sql_string_formatting":
                return "SQL_INJECTION"
            if sink_name in ["eval_exec", "pickle_loads", "yaml_load"]:
                return "CODE_INJECTION"
        if language in ("javascript", "typescript"):
            if sink_name == "exec_shell":
                return "COMMAND_INJECTION"
            if sink_name == "eval":
                return "CODE_INJECTION"
            if sink_name in ["innerHTML", "document_write", "dangerouslySetInnerHTML"]:
                return "XSS_HTML_OUTPUT"
            if sink_name in ["window_location", "router_push_replace"]:
                return "OPEN_REDIRECT"
        return None

    def _extract_taint_flows_to_sinks(self, filepath: str, content: str, language: str,
                                      tainted_variables: List[Dict]) -> List[Dict]:
        """
        Extract taint flows from sources to dangerous sinks.
        When the sink's input is not a local taint source, records parameter_source
        for cross-file resolution (call graph can fill traced_to / original_source later).
        """
        taint_flows = []
        tainted_var_names = {v["variable"] for v in tainted_variables}
        tainted_by_var = {v["variable"]: v.get("source", "unknown") for v in tainted_variables}

        lines = content.splitlines()
        sink_patterns = self.DANGEROUS_SINKS.get(language, {})

        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()

            if language == "python" and line_stripped.startswith("#"):
                continue
            if language in ("javascript", "typescript") and (
                line_stripped.startswith("//") or line_stripped.startswith("*")
            ):
                continue

            for sink_name, pattern in sink_patterns.items():
                if not pattern.search(line):
                    continue

                sink_type = self._sink_type_for_sink_name(sink_name, language)
                if not sink_type:
                    continue
                if language == "python" and sink_type == "XSS_HTML_OUTPUT":
                    if not self.HTML_OUTPUT_REGEX.search(line):
                        continue

                input_var = self._extract_sink_argument(line, sink_name, language)
                found_tainted = False

                for var_name in tainted_var_names:
                    if var_name in line:
                        found_tainted = True
                        param_source = {
                            "traced_to": None,
                            "original_source": tainted_by_var.get(var_name),
                            "sanitized": False,
                            "confidence": "high",
                        }
                        taint_flows.append({
                            "source_variable": var_name,
                            "sink_type": sink_type,
                            "sink_name": sink_name,
                            "line": line_num,
                            "line_content": line.strip()[:150],
                            "severity": "HIGH",
                            "parameter_source": param_source,
                        })

                if not found_tainted and input_var and input_var.isidentifier():
                    param_source = {
                        "traced_to": None,
                        "original_source": None,
                        "sanitized": False,
                        "confidence": "unknown",
                    }
                    taint_flows.append({
                        "source_variable": input_var,
                        "sink_type": sink_type,
                        "sink_name": sink_name,
                        "line": line_num,
                        "line_content": line.strip()[:150],
                        "severity": "HIGH",
                        "parameter_source": param_source,
                    })

        return taint_flows

    def _detect_cross_file_taint(self, filepath: str, content: str, language: str,
                                  tainted_variables: List[Dict]) -> List[Dict]:
        """
        Detect when tainted variables are passed to function calls that may lead to sinks.

        This is a shallow cross-file taint analysis (one to two hops).
        """
        cross_file_taints = []
        if not tainted_variables or language != "python":
            return cross_file_taints

        tainted_var_names = {v["variable"] for v in tainted_variables}
        lines = content.splitlines()

        # Pattern to match function calls with arguments
        # Matches: func_name(arg1, arg2) or obj.method(arg1, arg2)
        func_call_pattern = re.compile(
            r"(\w+)\s*\(([^)]*)\)"
        )

        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()

            # Skip comments and definitions
            if line_stripped.startswith("#") or line_stripped.startswith("def "):
                continue

            for match in func_call_pattern.finditer(line):
                func_name = match.group(1)
                args_str = match.group(2)

                # Check if any tainted variable is passed as argument
                tainted_args = []
                for var_name in tainted_var_names:
                    if var_name in args_str:
                        tainted_args.append(var_name)

                if tainted_args:
                    cross_file_taints.append({
                        "caller_function": None,  # Will be filled in by caller
                        "called_function": func_name,
                        "tainted_args": tainted_args,
                        "line": line_num,
                        "line_content": line.strip()[:100],
                    })

        return cross_file_taints

    def extract(self, filepath: str, content: str, language: Optional[str] = None, scan_id: Optional[str] = None) -> Dict:
        """
        Extract taint sources, secrets, and dangerous sinks from file content.

        Args:
            filepath: Relative path to the file
            content: File content as string
            language: Optional language override (auto-detected if not provided)

        Returns:
            Dictionary with tainted variables, entry points, secrets, taint flows, and cross-file taints
        """
        if language is None:
            language = self._detect_language(filepath)

        if not language or language not in self.TAINT_PATTERNS:
            # Even if we don't have taint patterns, we can still detect secrets
            secrets = self._extract_secrets(filepath, content, language or "python", scan_id=scan_id)
            return {
                "tainted_variables": [],
                "has_user_input": False,
                "entry_points": [],
                "secrets": secrets,
                "has_secrets": len(secrets) > 0,
                "taint_flows": [],
                "cross_file_taints": [],
            }

        patterns = self.TAINT_PATTERNS[language]
        tainted_variables = []
        lines = content.splitlines()

        # =====================================================================
        # STEP 1: Extract taint sources
        # =====================================================================
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()

            # Skip comments
            if language == "python" and line_stripped.startswith("#"):
                continue
            if language in ("javascript", "typescript", "java", "go"):
                if line_stripped.startswith("//") or line_stripped.startswith("*"):
                    continue

            for source_name, pattern in patterns.items():
                if pattern.search(line):
                    # Found a taint source - extract the variable
                    var_name = self._extract_variable_from_line(line, language)

                    if var_name:
                        tainted_variables.append({
                            "variable": var_name,
                            "source": source_name,
                            "line": line_num,
                            "line_content": line.strip(),
                        })

        # Determine if this file has user input
        has_user_input = len(tainted_variables) > 0

        # =====================================================================
        # STEP 2: Extract entry points
        # =====================================================================
        entry_points = []
        for var in tainted_variables:
            # Find the enclosing function (simple heuristic: look for def/function before this line)
            line_idx = var["line"] - 1
            for i in range(line_idx, -1, -1):
                line = lines[i] if i < len(lines) else ""
                if language == "python" and line.strip().startswith("def "):
                    func_match = re.match(r"def\s+(\w+)", line)
                    if func_match:
                        entry_points.append(func_match.group(1))
                        break
                elif language in ("javascript", "typescript"):
                    if re.match(r"(?:function\s+(\w+)|\s*(\w+)\s*[=:]\s*(?:async\s*)?\()", line):
                        func_match = re.search(r"(?:function\s+(\w+)|(\w+)\s*[=:])", line)
                        if func_match:
                            entry_points.append(func_match.group(1) or func_match.group(2))
                            break

        # =====================================================================
        # STEP 3: Extract hardcoded secrets (MISS 1 fix)
        # =====================================================================
        secrets = self._extract_secrets(filepath, content, language, scan_id=scan_id)

        # =====================================================================
        # STEP 4: Extract taint flows to dangerous sinks (MISS 2 fix)
        # =====================================================================
        taint_flows = self._extract_taint_flows_to_sinks(filepath, content, language, tainted_variables)

        # =====================================================================
        # STEP 5: Extract cross-file taint hints (MISS 4 fix)
        # =====================================================================
        cross_file_taints = self._detect_cross_file_taint(filepath, content, language, tainted_variables)

        return {
            "tainted_variables": tainted_variables,
            "has_user_input": has_user_input,
            "entry_points": list(set(entry_points)),
            "secrets": secrets,
            "has_secrets": len(secrets) > 0,
            "taint_flows": taint_flows,
            "has_taint_flows": len(taint_flows) > 0,
            "cross_file_taints": cross_file_taints,
            "has_cross_file_taints": len(cross_file_taints) > 0,
        }
