"""
SanitizerRegistry - Catalogs sanitizers, validators, and authentication guards in the project.

Detects functions that sanitize, validate, escape, or encode data, as well as
framework sanitizers (bleach, markupsafe, bcrypt) and auth guard decorators.
"""

import os
import re
import json
from typing import Dict, List, Set, Optional

# Import from parent package (relative import for package usage)
from ..redis_client import redis_client, REDIS_AVAILABLE
from ..config import SCAN_TTL, logger


class SanitizerRegistry:
    """Catalogs sanitizers, validators, and authentication guards."""

    # Name patterns for sanitizers/validators
    SANITIZER_NAME_PATTERNS = [
        r"^sanitize_",
        r"^validate_",
        r"^escape_",
        r"^encode_",
        r"^clean_",
        r"^strip_",
        r"^filter_",
        r"^purify_",
        r"^normalize_",
        r"^hash_",
        r"^encrypt_",
        r"^decrypt_",
        r"^verify_",
        r"^check_",
        r"^is_valid",
        r"_hash$",
        r"_escape$",
        r"_encode$",
        r"_sanitize$",
    ]

    # Auth guard decorator patterns
    AUTH_GUARD_PATTERNS = [
        r"@login_required",
        r"@requires_auth",
        r"@jwt_required",
        r"@permission_required",
        r"@authenticate",
        r"@auth_required",
        r"@login_protected",
        r"@admin_required",
        r"@staff_required",
        r"@roles_required",
        r"@fresh_login_required",
        r"@oidc_require_login",
    ]

    # Framework sanitizer usage patterns (detected in code)
    FRAMEWORK_SANITIZER_PATTERNS = {
        "bleach.clean": re.compile(r"bleach\.clean\s*\("),
        "bleach.linkify": re.compile(r"bleach\.linkify\s*\("),
        "markupsafe.escape": re.compile(r"(?:markupsafe\.)?escape\s*\("),
        "markupsafe.Markup": re.compile(r"Markup\s*\("),
        "html.escape": re.compile(r"html\.escape\s*\("),
        "cgi.escape": re.compile(r"cgi\.escape\s*\("),
        "urllib.parse.quote": re.compile(r"urllib\.parse\.quote\s*\("),
        "bcrypt.checkpw": re.compile(r"bcrypt\.checkpw\s*\("),
        "bcrypt.hashpw": re.compile(r"bcrypt\.hashpw\s*\("),
        "hashlib.sha256": re.compile(r"hashlib\.sha256\s*\("),
        "hashlib.sha512": re.compile(r"hashlib\.sha512\s*\("),
        "hashlib.pbkdf2_hmac": re.compile(r"hashlib\.pbkdf2_hmac\s*\("),
        "hmac.compare_digest": re.compile(r"hmac\.compare_digest\s*\("),
        "secrets.compare_digest": re.compile(r"secrets\.compare_digest\s*\("),
    }

    # ORM safe patterns (detect parameterized queries)
    PARAMETERIZED_QUERY_PATTERNS = {
        "sqlalchemy_execute": re.compile(r"(?:session|db|conn|connection)\.execute\s*\([^,]+,\s*[^)]+\)"),
        "django_raw": re.compile(r"\.raw\s*\([^,]+,\s*[^)]+\)"),
        "cursor_execute": re.compile(r"cursor\.execute\s*\([^,]+,\s*[^)]+\)"),
        "dbapi_execute": re.compile(r"\.execute\s*\([^,]+,\s*[^)]+\)"),
    }

    def __init__(self):
        self.registry = {
            "custom_sanitizers": [],
            "auth_guards": [],
            "framework_sanitizers": [],
            "parameterized_queries": [],
            "full_map": {},
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
        }
        return language_map.get(ext)

    def _is_sanitizer_by_name(self, func_name: str) -> bool:
        """Check if function name matches sanitizer patterns."""
        for pattern in self.SANITIZER_NAME_PATTERNS:
            if re.search(pattern, func_name, re.IGNORECASE):
                return True
        return False

    def _extract_function_defs(self, content: str, filepath: str, language: str) -> List[Dict]:
        """Extract function definitions with decorators for Python."""
        functions = []
        lines = content.splitlines()

        if language == "python":
            # Python: look for def statements and preceding decorators
            decorator_stack = []

            for line_num, line in enumerate(lines, 1):
                stripped = line.strip()

                # Check for decorators
                if stripped.startswith("@"):
                    decorator_stack.append(stripped)
                    continue

                # Check for function definition
                if stripped.startswith("def "):
                    match = re.match(r"def\s+(\w+)\s*\(", stripped)
                    if match:
                        func_name = match.group(1)
                        decorators = list(decorator_stack)

                        # Check for auth guards in decorators
                        is_auth_guard = False
                        for dec in decorators:
                            for pattern in self.AUTH_GUARD_PATTERNS:
                                if re.search(pattern, dec):
                                    is_auth_guard = True
                                    break

                        functions.append({
                            "name": func_name,
                            "line": line_num,
                            "decorators": decorators,
                            "is_auth_guard": is_auth_guard,
                        })

                    decorator_stack = []
                else:
                    # Reset decorator stack if we see a non-decorator, non-function line
                    if stripped and not stripped.startswith("#"):
                        decorator_stack = []

        else:
            # JavaScript/TypeScript
            for line_num, line in enumerate(lines, 1):
                stripped = line.strip()

                # function name(...) or const name = (...) =>
                patterns = [
                    r"function\s+(\w+)\s*\(",
                    r"(?:const|let|var)\s+(\w+)\s*=\s*function",
                    r"(?:const|let|var)\s+(\w+)\s*=\s*.*?=>",
                ]

                for pattern in patterns:
                    match = re.search(pattern, stripped)
                    if match:
                        func_name = match.group(1)
                        functions.append({
                            "name": func_name,
                            "line": line_num,
                            "decorators": [],
                            "is_auth_guard": False,
                        })
                        break

        return functions

    def _detect_framework_sanitizers(self, content: str, filepath: str) -> List[str]:
        """Detect usage of known framework sanitizers."""
        found = []
        for name, pattern in self.FRAMEWORK_SANITIZER_PATTERNS.items():
            if pattern.search(content):
                found.append(name)
        return list(set(found))

    def _detect_parameterized_queries(self, content: str, filepath: str) -> List[str]:
        """Detect parameterized query patterns."""
        found = []
        for name, pattern in self.PARAMETERIZED_QUERY_PATTERNS.items():
            if pattern.search(content):
                found.append(name)
        return list(set(found))

    def _get_source_files(self, project_path: str) -> List[str]:
        """Get all source files in the project."""
        source_files = []
        valid_extensions = {".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".go", ".mjs"}

        for root, dirs, files in os.walk(project_path):
            # Skip common non-source directories
            dirs[:] = [d for d in dirs if d not in {
                "node_modules", "venv", ".venv", "__pycache__", ".git",
                "dist", "build", ".next", "target", "vendor", "third_party"
            }]

            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in valid_extensions:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, project_path)
                    source_files.append(rel_path)

        return source_files

    def build(self, project_path: str, scan_id: str) -> Dict:
        """
        Build the sanitizer registry for the project.

        Args:
            project_path: Path to the project root directory
            scan_id: Unique scan identifier for Redis storage

        Returns:
            Dictionary containing categorized sanitizer information
        """
        logger.info(f"[{scan_id}] Building sanitizer registry...")

        source_files = self._get_source_files(project_path)
        logger.info(f"[{scan_id}] Scanning {len(source_files)} files for sanitizers")

        custom_sanitizers = []
        auth_guards = []
        framework_sanitizers = set()
        parameterized_queries = set()
        full_map = {}

        for rel_path in source_files:
            language = self._detect_language(rel_path)
            if not language:
                continue

            full_path = os.path.join(project_path, rel_path)
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except Exception as e:
                logger.warning(f"[{scan_id}] Failed to read {rel_path}: {e}")
                continue

            # Extract function definitions
            functions = self._extract_function_defs(content, rel_path, language)

            for func in functions:
                func_name = func["name"]
                is_sanitizer = self._is_sanitizer_by_name(func_name)

                if is_sanitizer:
                    entry = {
                        "name": func_name,
                        "file": rel_path,
                        "line": func["line"],
                        "role": "SANITIZER",
                    }
                    custom_sanitizers.append(func_name)
                    key = f"{rel_path}::{func_name}"
                    full_map[key] = entry

                if func.get("is_auth_guard"):
                    entry = {
                        "name": func_name,
                        "file": rel_path,
                        "line": func["line"],
                        "role": "AUTH_GUARD",
                    }
                    auth_guards.append(func_name)
                    key = f"{rel_path}::{func_name}"
                    full_map[key] = entry

            # Detect framework sanitizers
            fw_sanitizers = self._detect_framework_sanitizers(content, rel_path)
            framework_sanitizers.update(fw_sanitizers)

            # Detect parameterized queries
            param_queries = self._detect_parameterized_queries(content, rel_path)
            for pq in param_queries:
                parameterized_queries.add(f"{rel_path}:{pq}")

        self.registry = {
            "custom_sanitizers": list(set(custom_sanitizers)),
            "auth_guards": list(set(auth_guards)),
            "framework_sanitizers": list(framework_sanitizers),
            "parameterized_queries": list(parameterized_queries),
            "full_map": full_map,
        }

        # Store in Redis
        if REDIS_AVAILABLE:
            try:
                redis_client.setex(f"{scan_id}:sanitizer_registry", SCAN_TTL, json.dumps(self.registry))
                logger.info(f"[{scan_id}] Sanitizer registry stored in Redis")
            except Exception as e:
                logger.error(f"[{scan_id}] Failed to store sanitizer_registry in Redis: {e}")
        else:
            logger.warning(f"[{scan_id}] Redis not available, sanitizer_registry not persisted")

        logger.info(f"[{scan_id}] SanitizerRegistry complete: {len(custom_sanitizers)} sanitizers, "
                   f"{len(auth_guards)} auth guards, {len(framework_sanitizers)} framework sanitizers")
        return self.registry
