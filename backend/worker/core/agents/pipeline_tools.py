"""
Pipeline agent tools — fetch code on demand instead of sending full files.

Agents receive metadata (file list, call graph, entry points, sanitizers) and
use these tools to request only the code they need.
"""

import ast
import re
from typing import Any, Optional

from .models import AgentContext, DeadCodeRegion, SanitizerInfo

PIPELINE_AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "fetch_file",
            "description": "Fetch source code of a file. Pass start_line and end_line (1-indexed) to get only that range and save tokens. Otherwise returns the full file (may be truncated).",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative file path as in the project, e.g. 'src/auth.py'"},
                    "start_line": {"type": "integer", "description": "Optional. First line (1-indexed). Use with end_line for a range."},
                    "end_line": {"type": "integer", "description": "Optional. Last line (1-indexed). Use with start_line for a range."},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_context_slice",
            "description": "Get ±N lines around a specific line in a file. Use when you need surrounding context (e.g. around a sink or entry point).",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative file path"},
                    "line": {"type": "integer", "description": "Center line (1-indexed)"},
                    "window": {"type": "integer", "description": "Lines above and below. Default 30.", "default": 30},
                },
                "required": ["path", "line"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_function",
            "description": "Get the source of a single function in a file. Use when you only need one function body.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative file path"},
                    "function_name": {"type": "string", "description": "Exact function name"},
                },
                "required": ["path", "function_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trace_callers",
            "description": "List functions that call the given function (from the call graph). Use to see who can reach a dangerous sink.",
            "parameters": {
                "type": "object",
                "properties": {
                    "function_name": {"type": "string", "description": "Function to look up callers for"},
                },
                "required": ["function_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trace_callees",
            "description": "List functions called by the given function. Use to follow data flow from a source.",
            "parameters": {
                "type": "object",
                "properties": {
                    "function_name": {"type": "string", "description": "Function to look up callees for"},
                },
                "required": ["function_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "lookup_sanitizers",
            "description": "Return the sanitizer registry. Use to check if data is sanitized before a sink.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_dead_code",
            "description": "Check if a function is marked as dead/unreachable. Do not report findings in dead code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative file path"},
                    "function_name": {"type": "string", "description": "Function name to check"},
                },
                "required": ["path", "function_name"],
            },
        },
    },
]


class PipelineToolExecutor:
    """
    Runs pipeline agent tools using AgentContext only (no Redis).
    Use so the agent can request code on demand instead of receiving full files.
    """

    def __init__(self, context: AgentContext):
        self.context = context
        self._file_contents = getattr(context, "file_contents", None) or {}

    def execute(self, tool_name: str, tool_args: dict[str, Any]) -> str:
        try:
            if tool_name == "fetch_file":
                return self._fetch_file(
                    tool_args["path"],
                    start_line=tool_args.get("start_line"),
                    end_line=tool_args.get("end_line"),
                )
            if tool_name == "fetch_context_slice":
                return self._fetch_context_slice(
                    tool_args["path"],
                    tool_args["line"],
                    tool_args.get("window", 30),
                )
            if tool_name == "fetch_function":
                return self._fetch_function(tool_args["path"], tool_args["function_name"])
            if tool_name == "trace_callers":
                return self._trace_callers(tool_args["function_name"])
            if tool_name == "trace_callees":
                return self._trace_callees(tool_args["function_name"])
            if tool_name == "lookup_sanitizers":
                return self._lookup_sanitizers()
            if tool_name == "check_dead_code":
                return self._check_dead_code(tool_args["path"], tool_args["function_name"])
            return f"Unknown tool: {tool_name}. Available: fetch_file, fetch_context_slice, fetch_function, trace_callers, trace_callees, lookup_sanitizers, check_dead_code."
        except Exception as e:
            return f"Tool error ({tool_name}): {type(e).__name__}: {e}"

    def _normalize_path(self, path: str) -> Optional[str]:
        normalized = path.lstrip("./").replace("\\", "/").lstrip("/")
        if normalized in self._file_contents:
            return normalized
        for k in self._file_contents:
            if k.endswith(normalized) or normalized.endswith(k):
                return k
        return None

    def _fetch_file(
        self,
        path: str,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None,
    ) -> str:
        key = self._normalize_path(path)
        if not key:
            available = list(self._file_contents.keys())[:15]
            return f"File not found: {path}. Available (first 15): {available}"
        content = self._file_contents[key]
        lines = content.splitlines()
        total = len(lines)
        if start_line is not None and end_line is not None and start_line >= 1 and end_line >= start_line:
            s = max(0, start_line - 1)
            e = min(total, end_line)
            if s >= total:
                return f"File has {total} lines; start_line {start_line} is out of range."
            result = [f"{i+1:4}| {lines[i]}" for i in range(s, e)]
            return f"[Lines {s+1}-{e} of {total}]\n" + "\n".join(result)
        if len(content) > 8000:
            return content[:8000] + f"\n\n[TRUNCATED — full file {len(content)} chars]"
        return content

    def _fetch_context_slice(self, path: str, line: int, window: int) -> str:
        key = self._normalize_path(path)
        if not key:
            return f"File not found: {path}."
        content = self._file_contents[key]
        lines = content.splitlines()
        line_idx = max(0, min(line - 1, len(lines) - 1))
        start = max(0, line_idx - window)
        end = min(len(lines), line_idx + window + 1)
        result = []
        for i in range(start, end):
            prefix = ">>> " if i == line_idx else "    "
            result.append(f"{prefix}{i+1:4}| {lines[i]}")
        return "\n".join(result)

    def _fetch_function(self, path: str, function_name: str) -> str:
        key = self._normalize_path(path)
        if not key:
            return f"File not found: {path}."
        content = self._file_contents[key]
        # Python
        if key.endswith(".py"):
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name:
                        lines = content.splitlines()
                        start = node.lineno - 1
                        end = node.end_lineno
                        return "\n".join(f"{i+1:4}| {lines[i]}" for i in range(start, end))
            except SyntaxError:
                pass
        # Fallback: simple line search
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if re.search(rf"\bdef\s+{re.escape(function_name)}\s*\(", line) or re.search(
                rf"\basync\s+def\s+{re.escape(function_name)}\s*\(", line
            ):
                end = min(i + 60, len(lines))
                return "\n".join(f"{j+1:4}| {lines[j]}" for j in range(i, end)) + "\n[may be truncated]"
        return f"Function '{function_name}' not found in {path}."

    def _trace_callers(self, function_name: str) -> str:
        cg = getattr(self.context, "call_graph", None) or {}
        if not cg:
            return "Call graph not available."
        # call_graph: caller -> list of callees (may be "path::callee" or just "callee")
        callers = []
        for caller, callees in cg.items():
            for callee in callees if isinstance(callees, list) else [callees]:
                if function_name in str(callee) or (isinstance(callee, str) and callee.endswith(f"::{function_name}")):
                    callers.append(caller)
                    break
        if not callers:
            return f"No callers found for '{function_name}' in call graph."
        return "Functions that call '{function_name}':\n" + "\n".join(f"  - {c}" for c in callers[:50])

    def _trace_callees(self, function_name: str) -> str:
        cg = getattr(self.context, "call_graph", None) or {}
        if not cg:
            return "Call graph not available."
        # Try exact key then suffix match
        callees = cg.get(function_name)
        if callees is None:
            for k, v in cg.items():
                if k == function_name or k.endswith(f"::{function_name}"):
                    callees = v
                    break
        if not callees:
            return f"'{function_name}' not in call graph or calls no tracked functions."
        callees = callees if isinstance(callees, list) else [callees]
        return "Functions called by '{function_name}':\n" + "\n".join(f"  - {c}" for c in callees[:50])

    def _lookup_sanitizers(self) -> str:
        reg = getattr(self.context, "sanitizer_registry", None) or {}
        if not reg:
            return "No sanitizers in registry."
        lines = []
        for name, info in reg.items():
            if isinstance(info, SanitizerInfo):
                lines.append(f"  - {name}: file={info.file_path} sanitizes={info.sanitizes}")
            else:
                lines.append(f"  - {name}: {info}")
        return "Sanitizer registry:\n" + "\n".join(lines[:30])

    def _check_dead_code(self, path: str, function_name: str) -> str:
        dead = getattr(self.context, "dead_code_map", None) or {}
        key = f"{path}::{function_name}"
        if key in dead:
            return f"'{function_name}' in {path} is marked as dead/unreachable code."
        for k, v in dead.items():
            if isinstance(v, DeadCodeRegion) and v.file_path == path and function_name in k:
                return f"'{function_name}' in {path} is in a dead code region."
        return f"'{function_name}' in {path} is not marked as dead code."
