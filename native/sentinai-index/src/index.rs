//! Orchestrates a full project index into one JSON document.

use crate::call_graph::{build_api_surface, build_call_graph, call_graph_to_json};
use crate::dead_code::build_dead_code_map;
use crate::file_deps::{build_file_deps, file_deps_to_json};
use crate::keywords::scan_project_keywords;
use crate::project_index::SymbolIndex;
use crate::sanitizers::build_sanitizer_registry;
use crate::walk::{list_source_files, read_file, rel_path};
use serde_json::{json, Map, Value};
use std::path::Path;

/// Build the full index for `project_root`.
///
/// Top-level keys match Redis shapes used by the Python worker:
/// - `symbol_table`, `file_symbols`, `symbol_call_graph` (ProjectIndexer / regex index)
/// - `file_deps`, `call_graph`, `sanitizer_registry`, `dead_code_map`, `api_surface`
/// - `keyword_hits` (per-file check_keywords results)
pub fn index_project(project_root: &Path) -> Result<Value, String> {
    if !project_root.is_dir() {
        return Err(format!(
            "project root is not a directory: {}",
            project_root.display()
        ));
    }

    let source_full = list_source_files(project_root);
    let mut files: Vec<(String, String)> = Vec::new();
    for full in &source_full {
        let rel = rel_path(project_root, full);
        if let Some(content) = read_file(full) {
            files.push((rel, content));
        }
    }

    let symbols = SymbolIndex::build(&files);
    let file_deps = build_file_deps(project_root);
    let call_graph = build_call_graph(project_root, &file_deps);
    let api_surface = build_api_surface(&call_graph);
    let sanitizer_registry = build_sanitizer_registry(project_root);
    let dead_code_map = build_dead_code_map(&call_graph);
    let keyword_hits = scan_project_keywords(&files);

    let regex = symbols.to_regex_index_json();
    let mut keyword_map = Map::new();
    for (k, v) in keyword_hits {
        keyword_map.insert(
            k,
            Value::Array(v.into_iter().map(Value::String).collect()),
        );
    }

    Ok(json!({
        "symbol_table": regex.get("symbol_table").cloned().unwrap_or(json!({})),
        "file_symbols": regex.get("file_symbols").cloned().unwrap_or(json!({})),
        "symbol_call_graph": regex.get("call_graph").cloned().unwrap_or(json!({})),
        "file_deps": file_deps_to_json(&file_deps),
        "call_graph": call_graph_to_json(&call_graph),
        "sanitizer_registry": sanitizer_registry,
        "dead_code_map": dead_code_map,
        "api_surface": api_surface,
        "keyword_hits": Value::Object(keyword_map),
    }))
}
