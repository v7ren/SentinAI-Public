//! PyO3 bindings for the SentinAI local indexer.

mod call_graph;
mod dead_code;
mod file_deps;
mod index;
mod keywords;
mod project_index;
mod sanitizers;
mod walk;

use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use std::path::PathBuf;

/// Index a project root and return a Python dict matching Redis indexer shapes.
///
/// Keys: symbol_table, file_symbols, symbol_call_graph, file_deps, call_graph,
/// sanitizer_registry, dead_code_map, api_surface, keyword_hits.
#[pyfunction]
fn index_project(py: Python<'_>, root: &str) -> PyResult<PyObject> {
    let path = PathBuf::from(root);
    let value = index::index_project(&path).map_err(PyRuntimeError::new_err)?;
    let json_str = serde_json::to_string(&value).map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
    let json = py.import("json")?;
    let obj = json.call_method1("loads", (json_str,))?;
    Ok(obj.into())
}

/// Match Python utils.check_keywords: return up to 10 keyword hits in content.
#[pyfunction]
fn check_keywords(content: &str) -> Vec<String> {
    keywords::check_keywords(content)
}

/// Return the JSON document as a string (useful for tests without round-tripping).
#[pyfunction]
fn index_project_json(root: &str) -> PyResult<String> {
    let path = PathBuf::from(root);
    let value = index::index_project(&path).map_err(PyRuntimeError::new_err)?;
    serde_json::to_string(&value).map_err(|e| PyRuntimeError::new_err(e.to_string()))
}

#[pymodule]
fn sentinai_index(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(index_project, m)?)?;
    m.add_function(wrap_pyfunction!(index_project_json, m)?)?;
    m.add_function(wrap_pyfunction!(check_keywords, m)?)?;
    m.add("__version__", "0.1.0")?;
    Ok(())
}
