# sentinai-index (Rust / PyO3)

Local project indexer used by the SentinAI worker. One entry point:

```python
import sentinai_index
result = sentinai_index.index_project("/path/to/project")
# keys: symbol_table, file_symbols, symbol_call_graph, file_deps,
#       call_graph, sanitizer_registry, dead_code_map, api_surface, keyword_hits
```

Also exposes `check_keywords(content) -> list[str]` (same semantics as `utils.check_keywords`).

## Build

Requires:

- Rust toolchain (`rustc`, `cargo`) — https://rustup.rs
- Python 3.10+ with development headers (`Python.h` / Windows: matching Python install)
- `maturin` (`pip install maturin`)

From this directory:

```bash
pip install maturin
# Python 3.14+: PyO3 may need forward-compat until it officially supports the interpreter
set PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
maturin build --release
pip install target/wheels/sentinai_index-*.whl
```

On Unix shells use `export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1` instead of `set`.

If you have a virtualenv:

```bash
maturin develop --release
```

If `cargo`, `rustc`, or Python headers are missing, **skip the native build**. The worker keeps a pure-Python fallback in `backend/worker/core/native_index.py` that uses the existing indexer classes. Scans still work; they are just slower on the local indexing path.

## Verify

```bash
python -c "import sentinai_index; print(sorted(sentinai_index.index_project('.').keys()))"
```

From the repo root, the fixture test exercises Rust when available and otherwise the Python fallback:

```bash
python -m pytest backend/worker/tests/test_native_index.py -q
```
