"""
FunctionCallMapper - Extracts function definitions and call graph across the project.

Builds a call graph showing which functions call which other functions,
including cross-file resolution using the file dependency map.
Marks entry points (API routes, scheduled tasks, etc.).
"""

import os
import re
import json
from typing import Dict, List, Set, Optional, Tuple
import ast

# Import from parent package (relative import for package usage)
from ..redis_client import redis_client, REDIS_AVAILABLE
from ..config import SCAN_TTL, logger


class FunctionCallMapper:
    """Maps function definitions and call relationships across the project."""

    # Entry point decorators to detect
    ENTRY_POINT_PATTERNS = [
        r"@app\.(route|get|post|put|delete|patch|head|options)",
        r"@router\.(get|post|put|delete|patch|head|options)",
        r"@blueprint\.(route|get|post|put|delete|patch)",
        r"@api_view",
        r"@action",
        r"@click\.command",
        r"@click\.(argument|option)",
        r"@app\.command",
        r"@typer\.(command|callback)",
        r"@celery\.task",
        r"@app\.on_event",
        r"@app\.websocket",
        r"@periodic_task",
        r"@background_task",
        r"@job",
        r"@task",
        r"@socketio\.on",
        r"ipcMain\.handle",
        r"ipcMain\.on",
    ]

    ENTRY_POINT_REGEX = re.compile("|".join(ENTRY_POINT_PATTERNS))

    # Patterns for extracting function calls (language specific)
    CALL_PATTERNS = {
        "python": {
            "function_def": re.compile(r"^def\s+(\w+)\s*\(", re.MULTILINE),
            "class_method": re.compile(r"^\s+def\s+(\w+)\s*\(", re.MULTILINE),
            "function_call": re.compile(r"(\w+)\s*\("),
            "method_call": re.compile(r"(\w+)\.(\w+)\s*\("),
        },
        "javascript": {
            "function_def": re.compile(r"(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:function|.*?=>))\s*[\({]"),
            "arrow_function": re.compile(r"(?:const|let|var)\s+(\w+)\s*=\s*.*?=>"),
            "method_def": re.compile(r"(\w+)\s*\([^)]*\)\s*\{"),
            "function_call": re.compile(r"(\w+)\s*\("),
            "method_call": re.compile(r"(\w+)\.(\w+)\s*\("),
        },
        "typescript": {
            "function_def": re.compile(r"(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:function|.*?=>))\s*[\({]"),
            "arrow_function": re.compile(r"(?:const|let|var)\s+(\w+)\s*=\s*.*?=>"),
            "method_def": re.compile(r"(\w+)\s*\([^)]*\)\s*\{"),
            "function_call": re.compile(r"(\w+)\s*\("),
            "method_call": re.compile(r"(\w+)\.(\w+)\s*\("),
        },
    }

    def __init__(self):
        self.call_graph: Dict[str, Dict] = {}
        self.function_locations: Dict[str, Tuple[str, int, int]] = {}  # func_key -> (file, start_line, end_line)

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

    def _extract_function_defs_python(self, content: str, filepath: str) -> List[Dict]:
        """Extract function definitions from Python using AST for accuracy."""
        functions = []
        try:
            tree = ast.parse(content)
            lines = content.splitlines()

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_name = node.name
                    start_line = node.lineno
                    end_line = node.end_lineno if hasattr(node, "end_lineno") else start_line

                    # Check if this is a method (inside a class)
                    is_method = False
                    for parent in ast.walk(tree):
                        if isinstance(parent, ast.ClassDef):
                            for child in ast.walk(parent):
                                if child is node:
                                    is_method = True
                                    func_name = f"{parent.name}.{func_name}"
                                    break

                    is_entry_point = self._infer_entry_point(
                        filepath=filepath,
                        func_name=func_name,
                        decorator_list=node.decorator_list,
                        lines=lines,
                        lineno=node.lineno,
                    )

                    functions.append({
                        "name": func_name,
                        "file": filepath,
                        "start_line": start_line,
                        "end_line": end_line,
                        "is_method": is_method,
                        "is_entry_point": is_entry_point,
                    })

        except SyntaxError as e:
            logger.warning(f"Python parse error in {filepath}: {e}")
            # Fallback to regex
            return self._extract_function_defs_regex(content, filepath, "python")

        return functions

    def _extract_function_defs_regex(self, content: str, filepath: str, language: str) -> List[Dict]:
        """Extract function definitions using regex (fallback for non-Python)."""
        functions = []
        lines = content.splitlines()
        patterns = self.CALL_PATTERNS.get(language, {})

        func_def_pattern = patterns.get("function_def", re.compile("$^"))

        for match in func_def_pattern.finditer(content):
            # Get line number
            line_num = content[:match.start()].count("\n") + 1
            func_name = match.group(1) or match.group(2) if match.lastindex and match.lastindex > 1 else match.group(1)
            if func_name:
                functions.append({
                    "name": func_name,
                    "file": filepath,
                    "start_line": line_num,
                    "end_line": line_num,
                    "is_method": False,
                    "is_entry_point": self._infer_entry_point(
                        filepath=filepath,
                        func_name=func_name,
                        content=content,
                        lineno=line_num,
                    ),
                })

        return functions

    def _extract_function_defs(self, content: str, filepath: str, language: str) -> List[Dict]:
        """Extract function definitions from file content."""
        if language == "python":
            return self._extract_function_defs_python(content, filepath)
        else:
            return self._extract_function_defs_regex(content, filepath, language)

    def _extract_function_calls(
        self, content: str, filepath: str, language: str
    ) -> List[Tuple[str, int]]:
        """
        Extract function calls from content.
        Returns list of (function_name_or_pattern, line_number).
        """
        calls = []
        lines = content.splitlines()
        patterns = self.CALL_PATTERNS.get(language, {})

        # Simple function calls: funcname(
        call_pattern = patterns.get("function_call", re.compile(r"(\w+)\s*\("))

        line_offset = 0
        for line_num, line in enumerate(lines, 1):
            for match in call_pattern.finditer(line):
                func_name = match.group(1)
                # Skip common non-function patterns
                if func_name not in {"if", "while", "for", "switch", "catch", "return", "yield", "await", "sizeof", "typeof"}:
                    calls.append((func_name, line_num))

        return calls

    def _resolve_call_to_definition(
        self,
        call_name: str,
        caller_file: str,
        all_functions: Dict[str, Dict],
        file_dep_map: Dict,
    ) -> Optional[str]:
        """
        Resolve a function call to its definition key.
        Returns the function key (filepath::function_name) or None.
        """
        # Check if function is defined in the same file
        same_file_key = f"{caller_file}::{call_name}"
        if same_file_key in all_functions:
            return same_file_key

        # Check imported files
        if caller_file in file_dep_map:
            for imported_file in file_dep_map[caller_file].get("imports", []):
                import_key = f"{imported_file}::{call_name}"
                if import_key in all_functions:
                    return import_key

        # Check external packages (we can't resolve these)
        # Try common patterns for builtins/frameworks
        if call_name in {"print", "len", "range", "str", "int", "list", "dict", "set", "tuple",
                         "open", "os.path.join", "json.dumps", "json.loads", "requests.get",
                         "requests.post", "flask.jsonify", "redirect", "render_template",
                         "abort", "url_for", "session.get", "session.setdefault"}:
            return None  # Built-in or framework function

        # Could not resolve - might be dynamic or from unindexed file
        return None

    def build(self, project_path: str, scan_id: str, file_dep_map: Dict) -> Dict:
        """
        Build the function call graph for the project.

        Args:
            project_path: Path to the project root directory
            scan_id: Unique scan identifier for Redis storage
            file_dep_map: File dependency map from FileDependencyMapper

        Returns:
            Dictionary mapping each function to its call relationships
        """
        logger.info(f"[{scan_id}] Building function call graph...")

        # Get source files from file_dep_map keys
        source_files = list(file_dep_map.keys())
        logger.info(f"[{scan_id}] Analyzing {len(source_files)} files for call graph")

        # First pass: collect all function definitions
        all_functions: Dict[str, Dict] = {}  # key: filepath::function_name
        file_functions: Dict[str, List[str]] = {}  # file -> list of function keys

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

            functions = self._extract_function_defs(content, rel_path, language)
            file_functions[rel_path] = []

            for func in functions:
                func_key = f"{rel_path}::{func['name']}"
                all_functions[func_key] = func
                file_functions[rel_path].append(func_key)
                self.function_locations[func_key] = (
                    rel_path,
                    func["start_line"],
                    func["end_line"],
                )

        logger.info(f"[{scan_id}] Found {len(all_functions)} function definitions")

        # Second pass: extract call sites and resolve
        for rel_path in source_files:
            language = self._detect_language(rel_path)
            if not language:
                continue

            full_path = os.path.join(project_path, rel_path)
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except Exception as e:
                continue

            calls = self._extract_function_calls(content, rel_path, language)

            # For each function in this file, find which calls are inside it
            func_keys = file_functions.get(rel_path, [])

            for func_key in func_keys:
                if func_key not in all_functions:
                    continue

                func = all_functions[func_key]
                start_line = func["start_line"]
                end_line = func.get("end_line", start_line + 100)

                func_calls = []
                for call_name, call_line in calls:
                    if start_line <= call_line <= end_line:
                        resolved = self._resolve_call_to_definition(
                            call_name, rel_path, all_functions, file_dep_map
                        )
                        if resolved and resolved != func_key:  # Don't count self-calls
                            func_calls.append(resolved)

                # Remove duplicates
                func_calls = list(set(func_calls))
                all_functions[func_key]["calls"] = func_calls

        # Third pass: build called_by relationships
        for func_key, func_data in all_functions.items():
            all_functions[func_key]["called_by"] = []

        for func_key, func_data in all_functions.items():
            for called_func in func_data.get("calls", []):
                if called_func in all_functions:
                    if func_key not in all_functions[called_func]["called_by"]:
                        all_functions[called_func]["called_by"].append(func_key)

        # Fourth pass: detect test files
        for func_key, func_data in all_functions.items():
            func_data["is_test"] = self._is_test_function(func_key, func_data)

        self.call_graph = all_functions

        # Store in Redis
        if REDIS_AVAILABLE:
            try:
                redis_client.setex(f"{scan_id}:call_graph", SCAN_TTL, json.dumps(self.call_graph))
                logger.info(f"[{scan_id}] Call graph stored in Redis")
            except Exception as e:
                logger.error(f"[{scan_id}] Failed to store call_graph in Redis: {e}")
        else:
            logger.warning(f"[{scan_id}] Redis not available, call_graph not persisted")

        logger.info(f"[{scan_id}] FunctionCallMapper complete: {len(self.call_graph)} functions mapped")
        return self.call_graph

    def _infer_entry_point(
        self,
        filepath: str,
        func_name: str,
        decorator_list=None,
        lines: Optional[List[str]] = None,
        lineno: int = 1,
        content: str = "",
    ) -> bool:
        lines = lines or content.splitlines()
        if decorator_list:
            for decorator in decorator_list:
                decorator_str = ast.unparse(decorator) if hasattr(ast, "unparse") else ""
                if decorator_str and self.ENTRY_POINT_REGEX.search(decorator_str):
                    return True

        nearby = "\n".join(lines[max(0, lineno - 4):min(len(lines), lineno + 3)])
        if nearby and self.ENTRY_POINT_REGEX.search(nearby):
            return True

        path_lower = filepath.lower()
        name_lower = func_name.lower()
        if path_lower.endswith("/route.py") or "/routes/" in path_lower or path_lower.endswith("/route.ts"):
            return True
        if any(token in path_lower for token in ("/commands/", "/cli/", "/ipc/", "/jobs/", "/tasks/")):
            return True
        if name_lower in {"main", "handler", "serve", "run", "cli", "command"}:
            return True
        return False

    def _is_test_function(self, func_key: str, func_data: Dict) -> bool:
        """Detect if a function is a test function."""
        func_name = func_data.get("name", "")
        filepath = func_data.get("file", "")

        # Check if file is a test file
        test_patterns = [
            r"test_", r"_test\.", r"\.test\.", r"\.spec\.",
            r"tests?/", r"__tests__/", r"spec/",
        ]
        for pattern in test_patterns:
            if re.search(pattern, filepath):
                return True

        # Check if function name indicates test
        if func_name.startswith("test_") or func_name.endswith("_test"):
            return True

        return False
