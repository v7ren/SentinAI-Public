"""
DeadCodeDetector - Identifies potentially dead code and test-only functions.

Uses the call graph to count inbound call sites per function.
Flags functions with 0 call sites as potentially dead.
Flags functions only called from test files as test-only.
"""

import os
import re
import json
from typing import Dict, List, Set

# Import from parent package (relative import for package usage)
from ..redis_client import redis_client, REDIS_AVAILABLE
from ..config import SCAN_TTL, logger


class DeadCodeDetector:
    """Detects dead code and test-only functions from the call graph."""

    # Test file patterns
    TEST_FILE_PATTERNS = [
        r"^test_",
        r"_test\.py$",
        r"_test\.js$",
        r"_test\.ts$",
        r"\.test\.js$",
        r"\.test\.ts$",
        r"\.test\.tsx$",
        r"\.test\.jsx$",
        r"\.spec\.js$",
        r"\.spec\.ts$",
        r"\.spec\.tsx$",
        r"\.spec\.jsx$",
        r"^tests?/",
        r"/tests?/",
        r"__tests__/",
        r"spec/",
        r"/spec/",
    ]

    # Migration/seed/fixture patterns
    MIGRATION_PATTERNS = [
        r"migration",
        r"seed",
        r"fixture",
        r"mock",
        r"factory",
        r"populate",
    ]

    def __init__(self):
        self.dead_code_map: Dict[str, Dict] = {}

    def _is_test_file(self, filepath: str) -> bool:
        """Check if a file is a test file."""
        for pattern in self.TEST_FILE_PATTERNS:
            if re.search(pattern, filepath, re.IGNORECASE):
                return True
        return False

    def _is_migration_file(self, filepath: str) -> bool:
        """Check if a file is a migration/seed/fixture file."""
        for pattern in self.MIGRATION_PATTERNS:
            if re.search(pattern, filepath, re.IGNORECASE):
                return True
        return False

    def _count_inbound_calls(self, func_key: str, call_graph: Dict) -> int:
        """Count how many functions call this function."""
        count = 0
        for other_key, other_data in call_graph.items():
            if func_key in other_data.get("calls", []):
                count += 1
        return count

    def _get_callers(self, func_key: str, call_graph: Dict) -> List[str]:
        """Get list of functions that call this function."""
        callers = []
        for other_key, other_data in call_graph.items():
            if func_key in other_data.get("calls", []):
                callers.append(other_key)
        return callers

    def _get_caller_files(self, callers: List[str]) -> List[str]:
        """Extract unique file paths from caller function keys."""
        files = set()
        for caller in callers:
            # Function key format: filepath::function_name
            if "::" in caller:
                file_path = caller.split("::")[0]
                files.add(file_path)
        return list(files)

    def build(self, project_path: str, scan_id: str, call_graph: Dict) -> Dict:
        """
        Build the dead code map from the call graph.

        Args:
            project_path: Path to the project root directory
            scan_id: Unique scan identifier for Redis storage
            call_graph: Call graph from FunctionCallMapper

        Returns:
            Dictionary mapping each function to its dead code analysis
        """
        logger.info(f"[{scan_id}] Analyzing dead code...")

        for func_key, func_data in call_graph.items():
            file_path = func_data.get("file", "")
            is_entry_point = func_data.get("is_entry_point", False)
            is_test = func_data.get("is_test", False)

            # Skip entry points - they are always "alive"
            if is_entry_point:
                self.dead_code_map[func_key] = {
                    "inbound_call_count": -1,  # Special marker for entry points
                    "is_dead": False,
                    "is_test_only": False,
                    "is_entry_point": True,
                    "called_from_files": [],
                }
                continue

            # Count inbound calls
            inbound_count = self._count_inbound_calls(func_key, call_graph)
            callers = self._get_callers(func_key, call_graph)
            caller_files = self._get_caller_files(callers)

            # Determine if dead or test-only
            is_dead = inbound_count == 0
            is_test_only = False

            if not is_dead:
                # Check if all callers are test files
                all_callers_are_tests = all(
                    self._is_test_file(f) for f in caller_files
                )
                if all_callers_are_tests:
                    is_test_only = True

            # Check if this function is in a test/migration file
            if self._is_test_file(file_path) or self._is_migration_file(file_path):
                is_test_only = True

            self.dead_code_map[func_key] = {
                "inbound_call_count": inbound_count,
                "is_dead": is_dead,
                "is_test_only": is_test_only,
                "is_entry_point": False,
                "called_from_files": caller_files,
            }

        # Store in Redis
        if REDIS_AVAILABLE:
            try:
                redis_client.setex(f"{scan_id}:dead_code_map", SCAN_TTL, json.dumps(self.dead_code_map))
                logger.info(f"[{scan_id}] Dead code map stored in Redis")
            except Exception as e:
                logger.error(f"[{scan_id}] Failed to store dead_code_map in Redis: {e}")
        else:
            logger.warning(f"[{scan_id}] Redis not available, dead_code_map not persisted")

        # Stats
        dead_count = sum(1 for v in self.dead_code_map.values() if v.get("is_dead"))
        test_only_count = sum(1 for v in self.dead_code_map.values() if v.get("is_test_only"))
        entry_point_count = sum(1 for v in self.dead_code_map.values() if v.get("is_entry_point"))

        logger.info(f"[{scan_id}] DeadCodeDetector complete: {dead_count} dead functions, "
                   f"{test_only_count} test-only, {entry_point_count} entry points")
        return self.dead_code_map
