"""Fixture tests for native (Rust) index with Python fallback."""

import os
import tempfile

from backend.worker.core.native_index import (
    build_deepwiki_project_ir,
    check_keywords,
    index_project,
    index_project_on_disk,
    native_available,
)


REQUIRED_KEYS = {
    "symbol_table",
    "file_symbols",
    "symbol_call_graph",
    "file_deps",
    "call_graph",
    "sanitizer_registry",
    "dead_code_map",
    "api_surface",
    "keyword_hits",
}


def test_index_small_fixture_call_graph_and_keywords():
    """Rust index (or Python fallback) returns call-graph keys and keyword hits."""
    with tempfile.TemporaryDirectory() as tmp:
        app_path = os.path.join(tmp, "app.py")
        with open(app_path, "w", encoding="utf-8") as fh:
            fh.write(
                "from flask import Flask\n"
                "app = Flask(__name__)\n"
                "\n"
                "@app.route('/run')\n"
                "def handler():\n"
                "    eval(user_input)\n"
                "    return 'ok'\n"
                "\n"
                "def sanitize_input(value):\n"
                "    return value.strip()\n"
            )
        util_path = os.path.join(tmp, "util.py")
        with open(util_path, "w", encoding="utf-8") as fh:
            fh.write("def helper():\n    return sanitize_input('x')\n")

        data = index_project(tmp)
        for key in REQUIRED_KEYS:
            assert key in data, f"missing key: {key}"

        assert isinstance(data["call_graph"], dict)
        assert len(data["call_graph"]) >= 1

        hits = data.get("keyword_hits") or {}
        # At least one file should surface keyword hits (eval / similar)
        assert any(hits.values()), f"expected keyword hits, got {hits!r}"

        on_disk = index_project_on_disk(tmp)
        assert "symbol_index" in on_disk
        assert "symbol_table" in on_disk["symbol_index"]
        assert "file_symbols" in on_disk["symbol_index"]


def test_check_keywords_hits():
    found = check_keywords("please eval(user_input) and execute(query)")
    assert isinstance(found, list)
    assert len(found) >= 1
    assert len(found) <= 10


def test_build_deepwiki_project_ir_shape():
    sample = {
        "symbol_table": {"foo": {"file": "a.py", "code": "def foo():\n  pass", "dependencies": []}},
        "symbol_call_graph": {},
        "file_symbols": {"a.py": ["foo"]},
        "keyword_hits": {"a.py": ["eval("]},
        "api_surface": [],
        "file_deps": {"a.py": {"imports": [], "imported_by": [], "external_packages": []}},
        "call_graph": {
            "a.py::foo": {
                "name": "foo",
                "file": "a.py",
                "start_line": 1,
                "end_line": 2,
                "calls": [],
                "called_by": [],
                "is_entry_point": False,
                "is_test": False,
            }
        },
        "sanitizer_registry": {
            "custom_sanitizers": [],
            "auth_guards": [],
            "framework_sanitizers": [],
        },
        "dead_code_map": {},
    }
    ir = build_deepwiki_project_ir(sample)
    assert ir["source"] == "native_index"
    assert ir["file_count"] == 1
    assert ir["function_count"] == 1


def test_native_availability_reported():
    # Does not require Rust; just ensures the probe does not raise.
    assert isinstance(native_available(), bool)
