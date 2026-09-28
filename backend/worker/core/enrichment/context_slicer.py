"""
ContextSlicer - Builds minimal but complete context bundles for LLM prompts.

Reads the call graph, sanitizer registry, and dead code map from Redis,
then builds a targeted context slice for the function being scanned.
Includes full source for security-relevant callees, signatures for others.
"""

import os
import re
import json
from typing import Dict, List, Set, Optional, Tuple

# Import from parent package (relative import for package usage)
from ..redis_client import redis_client, REDIS_AVAILABLE
from ..config import logger


class ContextSlicer:
    """Slices the call graph to build targeted context for LLM prompts.

    Enhanced with cross-file taint propagation to track when user input
    flows through function calls to dangerous sinks in other files.
    """

    # Sink patterns - functions that should show full source
    SINK_PATTERNS = [
        r"execute\s*\(",
        r"query\s*\(",
        r"raw\s*\(",
        r"eval\s*\(",
        r"exec\s*\(",
        r"render\s*\(",
        r"innerHTML\s*=",
        r"system\s*\(",
        r"popen\s*\(",
        r"call\s*\(",
        r"check_output\s*\(",
        r"deserializ",
        r"loads?\s*\(",
        r"unpickle",
        r"send_mail",
        r"smtp",
        r"request\.get\s*\(",
        r"request\.post\s*\(",
        r"subprocess",
        r"open\s*\(",
        r"\.write\s*\(",
    ]

    SINK_REGEX = re.compile("|".join(SINK_PATTERNS), re.IGNORECASE)

    # Known dangerous sink functions for cross-file taint tracking (MISS 4 fix)
    DANGEROUS_SINK_FUNCTIONS = {
        "subprocess.getoutput",
        "subprocess.call",
        "subprocess.run",
        "subprocess.Popen",
        "subprocess.check_output",
        "subprocess.check_call",
        "os.system",
        "os.popen",
        "os.execv",
        "os.execve",
        "commands.getoutput",
        "commands.getstatusoutput",
        "eval",
        "exec",
        "compile",
        "pickle.loads",
        "pickle.load",
        "cPickle.loads",
        "yaml.load",
        "yaml.unsafe_load",
        "render_template_string",
        "render_template",
        "execute",
        "raw",
    }

    # Maximum depth for traversal
    FULL_SOURCE_DEPTH = 2
    SIGNATURE_DEPTH = 3
    # Cross-file taint propagation depth (MISS 4 fix)
    CROSS_FILE_TAINT_DEPTH = 2

    def __init__(self):
        self.call_graph: Dict = {}
        self.sanitizer_registry: Dict = {}
        self.dead_code_map: Dict = {}
        self.file_store: Dict[str, str] = {}

    def _load_from_redis(self, scan_id: str) -> bool:
        """Load index data from Redis."""
        if not REDIS_AVAILABLE:
            logger.warning(f"[{scan_id}] Redis not available, context slicing disabled")
            return False

        try:
            # Load call graph
            call_graph_data = redis_client.get(f"{scan_id}:call_graph")
            if call_graph_data:
                self.call_graph = json.loads(call_graph_data)

            # Load sanitizer registry
            sanitizer_data = redis_client.get(f"{scan_id}:sanitizer_registry")
            if sanitizer_data:
                self.sanitizer_registry = json.loads(sanitizer_data)

            # Load dead code map
            dead_code_data = redis_client.get(f"{scan_id}:dead_code_map")
            if dead_code_data:
                self.dead_code_map = json.loads(dead_code_data)

            file_store_data = redis_client.get(f"{scan_id}:file_store")
            if file_store_data:
                self.file_store = json.loads(file_store_data)

            return True
        except Exception as e:
            logger.error(f"[{scan_id}] Failed to load context from Redis: {e}")
            return False

    def _get_function_key(self, filepath: str, function_name: str) -> str:
        """Build the function key from filepath and function name."""
        return f"{filepath}::{function_name}"

    def _is_sanitizer(self, function_key: str) -> bool:
        """Check if a function is in the sanitizer registry."""
        full_map = self.sanitizer_registry.get("full_map", {})
        if function_key in full_map:
            role = full_map[function_key].get("role", "")
            return role == "SANITIZER"
        return False

    def _is_sink(self, function_key: str) -> bool:
        """Check if a function contains sink patterns in its name."""
        # Check function name for sink patterns
        if "::" in function_key:
            func_name = function_key.split("::")[1]
            if self.SINK_REGEX.search(func_name):
                return True
        return False

    def _is_dead_code(self, function_key: str) -> bool:
        """Check if a function is dead code."""
        if function_key in self.dead_code_map:
            return self.dead_code_map[function_key].get("is_dead", False)
        return False

    def _is_test_only(self, function_key: str) -> bool:
        """Check if a function is test-only."""
        if function_key in self.dead_code_map:
            return self.dead_code_map[function_key].get("is_test_only", False)
        return False

    def _contains_dangerous_sink(self, function_key: str, project_path: str, depth: int = 0, visited: Optional[Set[str]] = None) -> Tuple[bool, List[Dict]]:
        """
        Check if a function (or any function it calls) contains a dangerous sink.

        This is the core of cross-file taint propagation (MISS 4 fix).
        Returns (True, chain_info) if a dangerous sink is found in the call chain.

        Args:
            function_key: The function key to check
            project_path: Project root directory
            depth: Current recursion depth
            visited: Set of visited functions to prevent cycles

        Returns:
            Tuple of (has_dangerous_sink, list of sink details with chain info)
        """
        if visited is None:
            visited = set()

        if function_key in visited or depth > self.CROSS_FILE_TAINT_DEPTH:
            return False, []

        visited.add(function_key)

        if function_key not in self.call_graph:
            return False, []

        func_data = self.call_graph[function_key]
        func_source = self._get_function_source(function_key, project_path) or ""
        sinks_found = []

        # Check if this function directly contains dangerous sink patterns
        for sink_func in self.DANGEROUS_SINK_FUNCTIONS:
            # Check for subprocess.getoutput, os.system, etc.
            if sink_func in func_source:
                # Extract the line with the sink
                for line_num, line in enumerate(func_source.splitlines(), func_data.get("start_line", 1)):
                    if sink_func in line:
                        sinks_found.append({
                            "sink_function": sink_func,
                            "line": line_num,
                            "line_content": line.strip()[:150],
                            "in_function": function_key,
                            "depth": depth,
                        })
                        break

        # Recursively check called functions (cross-file propagation)
        calls = func_data.get("calls", [])
        for callee_key in calls:
            if callee_key in visited:
                continue

            has_sink, chain_sinks = self._contains_dangerous_sink(
                callee_key, project_path, depth + 1, visited
            )
            if has_sink:
                # Add this function to the chain
                for sink_info in chain_sinks:
                    sink_info["chain"] = [function_key] + sink_info.get("chain", [])
                sinks_found.extend(chain_sinks)

        return len(sinks_found) > 0, sinks_found

    def find_cross_file_taint_chains(
        self,
        entry_function: str,
        tainted_args: List[str],
        project_path: str,
    ) -> List[Dict]:
        """
        Find cross-file taint chains from entry point to dangerous sinks.

        This implements the cross-file taint propagation logic for MISS 4.

        Args:
            entry_function: The entry point function key
            tainted_args: List of argument names that are tainted
            project_path: Project root directory

        Returns:
            List of taint chains showing the flow from entry to dangerous sinks
        """
        chains = []

        if entry_function not in self.call_graph:
            return chains

        func_data = self.call_graph[entry_function]
        calls = func_data.get("calls", [])

        for callee_key in calls:
            # Check if the called function eventually reaches a dangerous sink
            has_sink, sink_info_list = self._contains_dangerous_sink(
                callee_key, project_path, depth=0, visited=set()
            )

            if has_sink:
                for sink_info in sink_info_list:
                    chains.append({
                        "entry_point": entry_function,
                        "intermediate_function": callee_key,
                        "final_sink": sink_info["sink_function"],
                        "sink_line": sink_info["line"],
                        "sink_content": sink_info["line_content"],
                        "chain_depth": sink_info["depth"] + 1,
                        "tainted_args": tainted_args,
                        "full_chain": [entry_function, callee_key] + sink_info.get("chain", []),
                    })

        return chains

    def _get_function_source(self, function_key: str, project_path: str) -> Optional[str]:
        """Get the full source code of a function."""
        if "::" not in function_key:
            return None

        filepath, func_name = function_key.split("::", 1)
        content = self.file_store.get(filepath)
        if content is None and project_path:
            full_path = os.path.join(project_path, filepath)
            if not os.path.exists(full_path):
                return None
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except Exception as e:
                logger.warning(f"Failed to get source for {function_key}: {e}")
                return None

        try:
            lines = (content or "").splitlines()
            # Find the function in the call graph to get line numbers
            if function_key not in self.call_graph:
                return None

            func_data = self.call_graph[function_key]
            start_line = func_data.get("start_line", 1)
            end_line = func_data.get("end_line", start_line + 50)

            # Extract the function source
            func_lines = lines[start_line - 1:end_line]
            return "\n".join(func_lines)

        except Exception as e:
            logger.warning(f"Failed to get source for {function_key}: {e}")
            return None

    def _get_function_signature(self, function_key: str) -> Optional[Dict]:
        """Get the signature (metadata) of a function."""
        if function_key not in self.call_graph:
            return None

        func_data = self.call_graph[function_key]
        return {
            "name": func_data.get("name"),
            "file": func_data.get("file"),
            "line": func_data.get("start_line"),
            "is_entry_point": func_data.get("is_entry_point", False),
            "is_test": func_data.get("is_test", False),
        }

    def _get_callers(self, function_key: str, max_depth: int = 5) -> List[Dict]:
        """Get callers of a function up to max_depth levels."""
        if function_key not in self.call_graph:
            return []

        func_data = self.call_graph[function_key]
        called_by = func_data.get("called_by", [])

        callers = []
        for caller_key in called_by[:max_depth]:  # Limit to max_depth callers
            caller_sig = self._get_function_signature(caller_key)
            if caller_sig:
                callers.append(caller_sig)

        return callers

    def _get_callees_with_context(
        self,
        function_key: str,
        project_path: str,
        depth: int = 0,
        visited: Optional[Set[str]] = None,
    ) -> List[Dict]:
        """
        Get callees of a function with appropriate context.
        - Sanitizers and sinks: full source
        - Others: signature only
        """
        if visited is None:
            visited = set()

        if function_key in visited:
            return []
        visited.add(function_key)

        if function_key not in self.call_graph:
            return []

        func_data = self.call_graph[function_key]
        calls = func_data.get("calls", [])

        callees = []
        for callee_key in calls:
            if callee_key in visited:
                continue

            role = "OTHER"
            source = None

            # Determine role and content depth
            if self._is_sanitizer(callee_key):
                role = "SANITIZER"
                if depth < self.FULL_SOURCE_DEPTH:
                    source = self._get_function_source(callee_key, project_path)
            elif self._is_sink(callee_key):
                role = "SINK"
                if depth < self.FULL_SOURCE_DEPTH:
                    source = self._get_function_source(callee_key, project_path)

            # Always get signature
            sig = self._get_function_signature(callee_key)
            if sig:
                callee_info = {
                    "key": callee_key,
                    "role": role,
                    "signature": sig,
                    "source": source,
                }
                callees.append(callee_info)

                # Recurse if needed (for signatures only)
                if depth < self.SIGNATURE_DEPTH:
                    sub_callees = self._get_callees_with_context(
                        callee_key, project_path, depth + 1, visited
                    )
                    # Don't include sub-callees in the main list, they stay separate

        return callees

    def slice_for_scan(
        self,
        filepath: str,
        function_name: str,
        scan_id: str,
        project_path: str,
        tainted_variables: Optional[List[Dict]] = None,
    ) -> Dict:
        """
        Build a context slice for scanning a specific function.

        Enhanced with cross-file taint propagation to track when tainted
        arguments flow to dangerous sinks in other files.

        Args:
            filepath: Relative path to the file
            function_name: Name of the function to analyze
            scan_id: Unique scan identifier
            project_path: Project root directory (for reading source files)
            tainted_variables: Optional list of tainted variable dicts with 'variable' keys

        Returns:
            Dictionary with callers, security-relevant callees, and cross-file taint chains
        """
        # Load data from Redis
        if not self._load_from_redis(scan_id):
            return {
                "callers": [],
                "security_callees": [],
                "function_key": None,
                "is_entry_point": False,
                "is_dead": False,
                "is_test_only": False,
                "cross_file_taint_chains": [],
            }

        function_key = self._get_function_key(filepath, function_name)

        # Get function info
        is_entry_point = False
        is_dead = False
        is_test_only = False

        if function_key in self.call_graph:
            func_data = self.call_graph[function_key]
            is_entry_point = func_data.get("is_entry_point", False)
            is_dead = self._is_dead_code(function_key)
            is_test_only = self._is_test_only(function_key)

        # Get callers (up to 5)
        callers = self._get_callers(function_key, max_depth=5)

        # Get callees with security context
        security_callees = self._get_callees_with_context(
            function_key, project_path, depth=0, visited=set()
        )

        # Cross-file taint propagation (MISS 4 fix)
        cross_file_taint_chains = []
        if tainted_variables and is_entry_point:
            tainted_arg_names = [v.get("variable") for v in tainted_variables if v.get("variable")]
            if tainted_arg_names:
                cross_file_taint_chains = self.find_cross_file_taint_chains(
                    function_key, tainted_arg_names, project_path or ""
                )
                if cross_file_taint_chains:
                    logger.info(f"Cross-file taint chains found: {len(cross_file_taint_chains)}")

        return {
            "function_key": function_key,
            "is_entry_point": is_entry_point,
            "is_dead": is_dead,
            "is_test_only": is_test_only,
            "callers": callers,
            "security_callees": security_callees,
            "cross_file_taint_chains": cross_file_taint_chains,
        }

    def format_for_prompt(self, slice_data: Dict) -> str:
        """
        Format the context slice as a string for LLM prompt injection.

        Enhanced to include cross-file taint chains for better detection
        of vulnerabilities that span multiple files.

        Args:
            slice_data: The slice data from slice_for_scan()

        Returns:
            Formatted context string
        """
        lines = ["## Call Chain Context", ""]

        # Callers section
        lines.append("### Who calls this function:")
        if slice_data.get("callers"):
            for caller in slice_data["callers"]:
                entry_marker = " [ENTRY POINT]" if caller.get("is_entry_point") else ""
                test_marker = " [TEST ONLY]" if caller.get("is_test_only") else ""
                lines.append(
                    f"- {caller['name']} ({caller['file']}:{caller['line']})"
                    f"{entry_marker}{test_marker}"
                )
        else:
            lines.append("- No callers found (may be an entry point or dead code)")
        lines.append("")

        # Security-relevant callees
        security_callees = slice_data.get("security_callees", [])
        if security_callees:
            lines.append("### Security-Relevant Callees:")

            for callee in security_callees:
                role = callee.get("role", "OTHER")
                sig = callee.get("signature", {})
                source = callee.get("source")

                lines.append(f"\n[ROLE: {role}] {sig.get('name')} ({sig.get('file')}:{sig.get('line')})")

                if source:
                    lines.append("```")
                    lines.append(source[:500])  # Limit source length
                    lines.append("```")
                else:
                    lines.append(f"  Signature: {sig.get('name')}()")

        # Cross-file taint chains (MISS 4 fix)
        cross_file_chains = slice_data.get("cross_file_taint_chains", [])
        if cross_file_chains:
            lines.append("")
            lines.append("### CROSS-FILE TAINT CHAINS DETECTED (CRITICAL):")
            lines.append("User input flows from this function to dangerous sinks in other files:")

            for i, chain in enumerate(cross_file_chains, 1):
                lines.append(f"\n**Chain {i}:**")
                lines.append(f"- Entry: {chain['entry_point']}")
                lines.append(f"- Intermediate: {chain['intermediate_function']}")
                lines.append(f"- Final Sink: {chain['final_sink']} (line {chain['sink_line']})")
                lines.append(f"- Tainted Args: {', '.join(chain['tainted_args'])}")
                lines.append(f"- Full Chain: {' -> '.join(chain['full_chain'])}")
                lines.append(f"- VULNERABILITY: **{chain['final_sink'].upper()} with unsanitized user input**")

            lines.append("")
            lines.append("> **ALERT**: The entry point function passes user-controlled input to another"
                        " function which eventually reaches a dangerous execution sink."
                        " This is a HIGH SEVERITY cross-file taint vulnerability.")

        return "\n".join(lines)
