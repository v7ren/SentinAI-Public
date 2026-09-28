"""
Native (Rust) project indexer with pure-Python fallback.

When ``sentinai_index`` is importable (built via maturin in native/sentinai-index),
``index_project`` / ``index_project_on_disk`` use the Rust implementation. Otherwise
the existing Python indexer classes run unchanged.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

_NATIVE = None
_NATIVE_TRIED = False

# Top-level keys returned by index_project / index_project_on_disk
INDEX_KEYS = (
    "symbol_table",
    "file_symbols",
    "symbol_call_graph",
    "file_deps",
    "call_graph",
    "sanitizer_registry",
    "dead_code_map",
    "api_surface",
    "keyword_hits",
    "symbol_index",
)


def _load_native():
    global _NATIVE, _NATIVE_TRIED
    if _NATIVE_TRIED:
        return _NATIVE
    _NATIVE_TRIED = True
    try:
        import sentinai_index as _mod  # type: ignore

        _NATIVE = _mod
        logger.info("Using Rust sentinai_index extension for local indexing")
    except Exception as e:
        _NATIVE = None
        logger.info("Rust sentinai_index not available (%s); using Python fallback", e)
    return _NATIVE


def native_available() -> bool:
    return _load_native() is not None


def check_keywords(content: str) -> List[str]:
    """Prefer Rust check_keywords; else Python ALL_KEYWORDS scan."""
    native = _load_native()
    if native is not None:
        try:
            return list(native.check_keywords(content))
        except Exception as e:
            logger.warning("native check_keywords failed (%s); falling back", e)

    from backend.worker.core.keywords import ALL_KEYWORDS

    content_lower = content.lower()
    found = [kw for kw in ALL_KEYWORDS if kw in content_lower]
    return found[:10]


def index_project_python(root: str) -> Dict[str, Any]:
    """Pure-Python equivalent of the Rust ``index_project`` entry point."""
    from backend.worker.core.indexers import (
        DeadCodeDetector,
        FileDependencyMapper,
        FunctionCallMapper,
        SanitizerRegistry,
    )
    from backend.worker.core.project_indexer import ProjectIndexer

    root = os.path.abspath(root)
    indexer = ProjectIndexer()
    keyword_hits: Dict[str, List[str]] = {}

    skip_dirs = {
        "node_modules", "venv", ".venv", "__pycache__", ".git",
        "dist", "build", ".next", "target", "vendor", "third_party",
    }
    valid_exts = {".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".go", ".mjs", ".php"}

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for name in filenames:
            ext = os.path.splitext(name)[1].lower()
            if ext not in valid_exts:
                continue
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, root)
            try:
                with open(full, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except OSError:
                continue
            indexer.index_file(rel, content)
            hits = check_keywords(content)
            if hits:
                keyword_hits[rel] = hits

    indexer._populate_dependencies()
    scan_id = "native-fallback"

    fdm = FileDependencyMapper()
    file_deps = fdm.build(root, scan_id)

    fcm = FunctionCallMapper()
    call_graph = fcm.build(root, scan_id, file_deps)

    api_surface = [
        {
            "function_key": key,
            "file": value.get("file"),
            "name": value.get("name"),
            "line": value.get("start_line"),
        }
        for key, value in call_graph.items()
        if value.get("is_entry_point")
    ]

    sr = SanitizerRegistry()
    sanitizer_registry = sr.build(root, scan_id)

    dcd = DeadCodeDetector()
    dead_code_map = dcd.build(root, scan_id, call_graph)

    return {
        "symbol_table": indexer.symbol_table,
        "file_symbols": indexer.file_symbols,
        "symbol_call_graph": indexer.call_graph,
        "file_deps": file_deps,
        "call_graph": call_graph,
        "sanitizer_registry": sanitizer_registry,
        "dead_code_map": dead_code_map,
        "api_surface": api_surface,
        "keyword_hits": keyword_hits,
    }


def index_project(root: str) -> Dict[str, Any]:
    """
    Index ``root`` and return Redis-shaped maps.

    Uses Rust when ``sentinai_index`` is built; otherwise Python fallback.
    """
    root = os.path.abspath(root)
    native = _load_native()
    if native is not None:
        try:
            result = native.index_project(root)
            if isinstance(result, dict):
                return result
            return dict(result)
        except Exception as e:
            logger.warning("native index_project failed (%s); falling back to Python", e)
        except BaseException as e:
            # PyO3 panics surface as PanicException (not a subclass of Exception).
            if type(e).__name__ != "PanicException":
                raise
            logger.warning("native index_project panicked (%s); falling back to Python", e)
    return index_project_python(root)


def _with_symbol_index(result: Dict[str, Any]) -> Dict[str, Any]:
    """Attach ProjectIndexer-shaped ``symbol_index`` for Redis /index_project."""
    out = dict(result)
    out["symbol_index"] = {
        "symbol_table": result.get("symbol_table") or {},
        "call_graph": result.get("symbol_call_graph") or {},
        "file_symbols": result.get("file_symbols") or {},
    }
    return out


def index_project_on_disk(root: str) -> Dict[str, Any]:
    """Worker entry used by main.py: full index plus ``symbol_index`` blob."""
    return _with_symbol_index(index_project(root))


def regex_index_blob(result: Dict[str, Any]) -> str:
    """Serialize ProjectIndexer-compatible JSON for Redis ``scan_id`` storage."""
    sym = result.get("symbol_index")
    if isinstance(sym, dict) and sym:
        return json.dumps(sym)
    return json.dumps({
        "symbol_table": result.get("symbol_table") or {},
        "call_graph": result.get("symbol_call_graph") or {},
        "file_symbols": result.get("file_symbols") or {},
    })


def persist_extended_index(scan_id: str, index_data: Dict[str, Any]) -> None:
    """Write extended indexer maps to Redis under ``scan_id:*`` keys."""
    from backend.worker.core.config import SCAN_TTL
    from backend.worker.core.redis_client import REDIS_AVAILABLE, redis_client

    if not REDIS_AVAILABLE or redis_client is None:
        logger.warning("[%s] Redis not available; extended index not persisted", scan_id)
        return

    payloads = {
        f"{scan_id}:file_deps": index_data.get("file_deps") or {},
        f"{scan_id}:call_graph": index_data.get("call_graph") or {},
        f"{scan_id}:sanitizer_registry": index_data.get("sanitizer_registry") or {},
        f"{scan_id}:dead_code_map": index_data.get("dead_code_map") or {},
        f"{scan_id}:api_surface": index_data.get("api_surface") or [],
        f"{scan_id}:keyword_hits": index_data.get("keyword_hits") or {},
    }
    sym = index_data.get("symbol_index")
    if isinstance(sym, dict) and sym:
        payloads[scan_id] = sym

    for key, value in payloads.items():
        try:
            redis_client.setex(key, SCAN_TTL, json.dumps(value))
        except Exception as e:
            logger.error("[%s] Failed to store %s: %s", scan_id, key, e)


def build_deepwiki_project_ir(index_data: Dict[str, Any]) -> Dict[str, Any]:
    """Compact project IR for DeepWiki / Flash summary (no LLM indexing loop)."""
    call_graph = index_data.get("call_graph") or {}
    file_deps = index_data.get("file_deps") or {}
    sanitizer_registry = index_data.get("sanitizer_registry") or {}
    dead_code_map = index_data.get("dead_code_map") or {}
    api_surface = index_data.get("api_surface") or []
    keyword_hits = index_data.get("keyword_hits") or {}
    symbol_table = index_data.get("symbol_table") or {}

    return {
        "source": "native_index",
        "file_count": len(file_deps),
        "function_count": len(call_graph),
        "symbol_count": len(symbol_table),
        "api_surface": api_surface,
        "sanitizer_registry": {
            "custom_sanitizers": (sanitizer_registry or {}).get("custom_sanitizers", []),
            "auth_guards": (sanitizer_registry or {}).get("auth_guards", []),
            "framework_sanitizers": (sanitizer_registry or {}).get("framework_sanitizers", []),
        },
        "dead_code_summary": {
            "dead": sum(1 for v in dead_code_map.values() if isinstance(v, dict) and v.get("is_dead")),
            "test_only": sum(
                1 for v in dead_code_map.values() if isinstance(v, dict) and v.get("is_test_only")
            ),
            "entry_points": sum(
                1 for v in dead_code_map.values() if isinstance(v, dict) and v.get("is_entry_point")
            ),
        },
        "keyword_hit_files": len(keyword_hits),
        "file_deps": file_deps,
        "call_graph": call_graph,
    }
