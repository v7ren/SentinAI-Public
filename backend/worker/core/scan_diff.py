# backend/worker/core/scan_diff.py
"""
Scan Diff Mode — Incremental scan for CI/CD: only changed files + dependents.

Expands a set of changed file paths using dependency_map and call_graph so that
the agent pipeline runs on a minimal but complete context. Target: ~80% token
reduction vs full scan on typical PRs (5–10 files changed in 500-file repo).
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def _file_from_key(key: str) -> str | None:
    if "::" in key:
        return key.split("::", 1)[0].replace("\\", "/")
    return key.replace("\\", "/") if key else None


def expand_changed_files(
    changed_files: list[str],
    dependency_map: dict[str, list[str]],
    call_graph: dict[str, Any],
    depth: int = 2,
) -> list[str]:
    """
    Expand changed files to include all files that could be affected.

    - dependency_map: file_path -> list of files it imports (or that import it)
    - call_graph: function_key -> { "file", "callees", "called_by" } or similar
    - depth: 1 = direct importers/imported + direct callers/callees;
            2 = one more hop; typical PR uses depth=2.

    Returns a sorted list of file paths (changed + expanded), deduplicated.
    """
    if not changed_files:
        return []

    changed_set = set(f.replace("\\", "/") for f in changed_files)
    # Normalize dependency_map keys
    dep_map_norm: dict[str, list[str]] = {}
    for k, v in dependency_map.items():
        key = k.replace("\\", "/")
        dep_map_norm[key] = [x.replace("\\", "/") for x in (v if isinstance(v, list) else [])]
    # Build reverse: who imports this file?
    imported_by: dict[str, set[str]] = {}
    for importer, deps in dep_map_norm.items():
        for dep in deps:
            imported_by.setdefault(dep, set()).add(importer)
    # Call graph: file from function key (e.g. "path/to/file.py::func")
    def file_from_key(key: str) -> str | None:
        return _file_from_key(key)
    call_graph_files: dict[str, set[str]] = {}  # file -> set of files it calls or is called by
    for func_key, data in call_graph.items():
        f = file_from_key(func_key)
        if not f:
            continue
        call_graph_files.setdefault(f, set())
        if isinstance(data, dict):
            for callee in data.get("callees", []) or data.get("callees_list", []):
                c = file_from_key(callee) if isinstance(callee, str) else None
                if c and c != f:
                    call_graph_files[f].add(c)
            for caller in data.get("called_by", []) or data.get("callers", []):
                c = file_from_key(caller) if isinstance(caller, str) else None
                if c and c != f:
                    call_graph_files[f].add(c)
        elif isinstance(data, list):
            for callee in data:
                c = file_from_key(callee) if isinstance(callee, str) else None
                if c and c != f:
                    call_graph_files[f].add(c)

    expanded: set[str] = set(changed_set)
    current_front = set(changed_set)
    for _ in range(depth):
        next_front: set[str] = set()
        for path in current_front:
            # Files that import this file
            for importer in imported_by.get(path, []):
                if importer not in expanded:
                    expanded.add(importer)
                    next_front.add(importer)
            # Files this file imports
            for dep in dep_map_norm.get(path, []):
                if dep not in expanded:
                    expanded.add(dep)
                    next_front.add(dep)
            # Call graph neighbors
            for neighbor in call_graph_files.get(path, []):
                if neighbor not in expanded:
                    expanded.add(neighbor)
                    next_front.add(neighbor)
        current_front = next_front
        if not current_front:
            break

    return sorted(expanded)


def build_diff_context(
    file_contents: dict[str, str],
    expanded_paths: list[str],
    dependency_map: dict[str, Any],
    call_graph: dict[str, Any],
) -> dict[str, Any]:
    """
    Build a reduced AgentContext-style payload for diff scan: only expanded file
    contents and trimmed dependency/call_graph to those files.
    """
    expanded_set = set(expanded_paths)
    contents = {k: v for k, v in file_contents.items() if k in expanded_set}
    deps = {k: [x for x in (v if isinstance(v, list) else []) if x in expanded_set]
            for k, v in dependency_map.items() if k in expanded_set}
    # Call graph: keep only nodes whose file is in expanded_set
    cg_trimmed: dict[str, Any] = {}
    for k, v in call_graph.items():
        f = _file_from_key(k)
        if f not in expanded_set:
            continue
        if isinstance(v, dict):
            cg_trimmed[k] = {
                **v,
                "callees": [c for c in (v.get("callees") or []) if _file_from_key(c) in expanded_set],
                "called_by": [c for c in (v.get("called_by") or []) if _file_from_key(c) in expanded_set],
            }
        else:
            cg_trimmed[k] = v
    return {
        "file_contents": contents,
        "dependency_map": deps,
        "call_graph": cg_trimmed,
        "expanded_paths": expanded_paths,
        "changed_count": len(expanded_paths),
    }
