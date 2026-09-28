//! Function call graph matching FunctionCallMapper (regex-based; no Python AST).

use crate::walk::{detect_language, read_file};
use once_cell::sync::Lazy;
use regex::Regex;
use serde_json::{json, Map, Value};
use std::collections::{BTreeMap, BTreeSet, HashMap};
use std::path::Path;

static ENTRY_POINT_RE: Lazy<Regex> = Lazy::new(|| {
    Regex::new(
        r"@app\.(route|get|post|put|delete|patch|head|options)|@router\.(get|post|put|delete|patch|head|options)|@blueprint\.(route|get|post|put|delete|patch)|@api_view|@action|@click\.command|@click\.(argument|option)|@app\.command|@typer\.(command|callback)|@celery\.task|@app\.on_event|@app\.websocket|@periodic_task|@background_task|@job|@task|@socketio\.on|ipcMain\.handle|ipcMain\.on",
    )
    .unwrap()
});

static PY_FUNC_DEF: Lazy<Regex> = Lazy::new(|| Regex::new(r"(?m)^def\s+(\w+)\s*\(").unwrap());
static PY_METHOD_DEF: Lazy<Regex> = Lazy::new(|| Regex::new(r"(?m)^\s+def\s+(\w+)\s*\(").unwrap());
static JS_FUNC_DEF: Lazy<Regex> = Lazy::new(|| {
    Regex::new(r"(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:function|.*?=>))\s*[\({]")
        .unwrap()
});
static CALL_RE: Lazy<Regex> = Lazy::new(|| Regex::new(r"(\w+)\s*\(").unwrap());

const SKIP_CALLS: &[&str] = &[
    "if", "while", "for", "switch", "catch", "return", "yield", "await", "sizeof", "typeof",
];

fn infer_entry_point(filepath: &str, func_name: &str, lines: &[&str], lineno: usize) -> bool {
    let start = lineno.saturating_sub(4);
    let end = (lineno + 2).min(lines.len());
    let nearby = lines[start..end].join("\n");
    if ENTRY_POINT_RE.is_match(&nearby) {
        return true;
    }
    let path_lower = filepath.to_lowercase().replace('\\', "/");
    let name_lower = func_name.to_lowercase();
    if path_lower.ends_with("/route.py")
        || path_lower.contains("/routes/")
        || path_lower.ends_with("/route.ts")
    {
        return true;
    }
    for token in ["/commands/", "/cli/", "/ipc/", "/jobs/", "/tasks/"] {
        if path_lower.contains(token) {
            return true;
        }
    }
    matches!(
        name_lower.as_str(),
        "main" | "handler" | "serve" | "run" | "cli" | "command"
    )
}

fn is_test_function(func_key: &str, func_name: &str, filepath: &str) -> bool {
    let patterns = [
        "test_", "_test.", ".test.", ".spec.", "tests/", "test/", "__tests__/", "spec/",
    ];
    for p in patterns {
        if filepath.contains(p) {
            return true;
        }
    }
    func_name.starts_with("test_") || func_name.ends_with("_test") || func_key.contains("test_")
}

struct FuncDef {
    name: String,
    file: String,
    start_line: usize,
    end_line: usize,
    is_method: bool,
    is_entry_point: bool,
}

fn extract_defs(content: &str, filepath: &str, language: &str) -> Vec<FuncDef> {
    let lines: Vec<&str> = content.lines().collect();
    let mut functions = Vec::new();

    if language == "python" {
        for caps in PY_FUNC_DEF.captures_iter(content) {
            let name = caps.get(1).map(|m| m.as_str()).unwrap_or("").to_string();
            let start = caps.get(0).map(|m| m.start()).unwrap_or(0);
            let line_num = content[..start].matches('\n').count() + 1;
            // Estimate end: next top-level def or EOF
            let end_line = estimate_end(content, start, language);
            let is_entry = infer_entry_point(filepath, &name, &lines, line_num);
            functions.push(FuncDef {
                name,
                file: filepath.to_string(),
                start_line: line_num,
                end_line,
                is_method: false,
                is_entry_point: is_entry,
            });
        }
        // Methods (indented def) — may duplicate; prefer Class.method naming lightly
        for caps in PY_METHOD_DEF.captures_iter(content) {
            let name = caps.get(1).map(|m| m.as_str()).unwrap_or("").to_string();
            let start = caps.get(0).map(|m| m.start()).unwrap_or(0);
            let line_num = content[..start].matches('\n').count() + 1;
            // Skip if already captured as top-level at same line
            if functions.iter().any(|f| f.start_line == line_num) {
                continue;
            }
            let end_line = estimate_end(content, start, language);
            let is_entry = infer_entry_point(filepath, &name, &lines, line_num);
            functions.push(FuncDef {
                name,
                file: filepath.to_string(),
                start_line: line_num,
                end_line,
                is_method: true,
                is_entry_point: is_entry,
            });
        }
    } else {
        for caps in JS_FUNC_DEF.captures_iter(content) {
            let name = caps
                .get(1)
                .or_else(|| caps.get(2))
                .map(|m| m.as_str())
                .unwrap_or("")
                .to_string();
            if name.is_empty() {
                continue;
            }
            let start = caps.get(0).map(|m| m.start()).unwrap_or(0);
            let line_num = content[..start].matches('\n').count() + 1;
            let end_line = estimate_end(content, start, language);
            let is_entry = infer_entry_point(filepath, &name, &lines, line_num);
            functions.push(FuncDef {
                name,
                file: filepath.to_string(),
                start_line: line_num,
                end_line,
                is_method: false,
                is_entry_point: is_entry,
            });
        }
    }
    functions
}

fn estimate_end(content: &str, start: usize, language: &str) -> usize {
    let after = &content[start..];
    let lines: Vec<&str> = after.lines().collect();
    if lines.is_empty() {
        return content[..start].matches('\n').count() + 1;
    }
    let start_line = content[..start].matches('\n').count() + 1;
    if language == "python" {
        let indent = lines[0].chars().take_while(|c| c.is_whitespace()).count();
        for (i, line) in lines.iter().enumerate().skip(1) {
            if line.trim().is_empty() {
                continue;
            }
            let ind = line.chars().take_while(|c| c.is_whitespace()).count();
            if ind <= indent && (line.trim_start().starts_with("def ") || line.trim_start().starts_with("class ")) {
                return start_line + i - 1;
            }
        }
        return start_line + lines.len() - 1;
    }
    // brace-ish languages: crude +100 line window like Python fallback
    (start_line + 100).min(start_line + lines.len().saturating_sub(1))
}

fn extract_calls(content: &str) -> Vec<(String, usize)> {
    let mut calls = Vec::new();
    for (line_num, line) in content.lines().enumerate() {
        for caps in CALL_RE.captures_iter(line) {
            let name = caps.get(1).map(|m| m.as_str()).unwrap_or("");
            if !SKIP_CALLS.contains(&name) {
                calls.push((name.to_string(), line_num + 1));
            }
        }
    }
    calls
}

fn resolve_call(
    call_name: &str,
    caller_file: &str,
    all_functions: &HashMap<String, Value>,
    file_dep_map: &BTreeMap<String, Value>,
) -> Option<String> {
    let same = format!("{}::{}", caller_file, call_name);
    if all_functions.contains_key(&same) {
        return Some(same);
    }
    if let Some(deps) = file_dep_map.get(caller_file) {
        if let Some(imports) = deps.get("imports").and_then(|v| v.as_array()) {
            for imp in imports {
                if let Some(imported_file) = imp.as_str() {
                    let key = format!("{}::{}", imported_file, call_name);
                    if all_functions.contains_key(&key) {
                        return Some(key);
                    }
                }
            }
        }
    }
    None
}

pub fn build_call_graph(
    project_root: &Path,
    file_dep_map: &BTreeMap<String, Value>,
) -> BTreeMap<String, Value> {
    let source_files: Vec<String> = file_dep_map.keys().cloned().collect();
    let mut all_functions: HashMap<String, Value> = HashMap::new();
    let mut file_functions: HashMap<String, Vec<String>> = HashMap::new();

    for rel in &source_files {
        let language = match detect_language(rel) {
            Some("python") => "python",
            Some("javascript") | Some("typescript") => "javascript",
            _ => continue,
        };
        let full = project_root.join(rel);
        let Some(content) = read_file(&full) else {
            continue;
        };
        let funcs = extract_defs(&content, rel, language);
        let mut keys = Vec::new();
        for func in funcs {
            let func_key = format!("{}::{}", rel, func.name);
            all_functions.insert(
                func_key.clone(),
                json!({
                    "name": func.name,
                    "file": func.file,
                    "start_line": func.start_line,
                    "end_line": func.end_line,
                    "is_method": func.is_method,
                    "is_entry_point": func.is_entry_point,
                    "calls": [],
                    "called_by": [],
                    "is_test": false,
                }),
            );
            keys.push(func_key);
        }
        file_functions.insert(rel.clone(), keys);
    }

    for rel in &source_files {
        let language = match detect_language(rel) {
            Some("python") => "python",
            Some("javascript") | Some("typescript") => "javascript",
            _ => continue,
        };
        let _ = language;
        let full = project_root.join(rel);
        let Some(content) = read_file(&full) else {
            continue;
        };
        let calls = extract_calls(&content);
        let func_keys = file_functions.get(rel).cloned().unwrap_or_default();
        for func_key in func_keys {
            let Some(func) = all_functions.get(&func_key).cloned() else {
                continue;
            };
            let start_line = func.get("start_line").and_then(|v| v.as_u64()).unwrap_or(0) as usize;
            let end_line = func
                .get("end_line")
                .and_then(|v| v.as_u64())
                .unwrap_or(start_line as u64 + 100) as usize;
            let mut func_calls: BTreeSet<String> = BTreeSet::new();
            for (call_name, call_line) in &calls {
                if *call_line >= start_line && *call_line <= end_line {
                    if let Some(resolved) =
                        resolve_call(call_name, rel, &all_functions, file_dep_map)
                    {
                        if resolved != func_key {
                            func_calls.insert(resolved);
                        }
                    }
                }
            }
            if let Some(entry) = all_functions.get_mut(&func_key) {
                entry["calls"] = Value::Array(
                    func_calls
                        .into_iter()
                        .map(Value::String)
                        .collect(),
                );
            }
        }
    }

    // called_by
    let keys: Vec<String> = all_functions.keys().cloned().collect();
    for key in &keys {
        if let Some(entry) = all_functions.get_mut(key) {
            entry["called_by"] = Value::Array(vec![]);
        }
    }
    let snapshot: HashMap<String, Value> = all_functions.clone();
    for (func_key, func_data) in &snapshot {
        if let Some(calls) = func_data.get("calls").and_then(|v| v.as_array()) {
            for called in calls {
                if let Some(called_key) = called.as_str() {
                    if let Some(target) = all_functions.get_mut(called_key) {
                        let arr = target
                            .get_mut("called_by")
                            .and_then(|v| v.as_array_mut());
                        if let Some(arr) = arr {
                            let already = arr.iter().any(|v| v.as_str() == Some(func_key.as_str()));
                            if !already {
                                arr.push(Value::String(func_key.clone()));
                            }
                        }
                    }
                }
            }
        }
    }

    // is_test
    for (func_key, func_data) in all_functions.iter_mut() {
        let name = func_data
            .get("name")
            .and_then(|v| v.as_str())
            .unwrap_or("");
        let file = func_data
            .get("file")
            .and_then(|v| v.as_str())
            .unwrap_or("");
        func_data["is_test"] = Value::Bool(is_test_function(func_key, name, file));
    }

    let mut out = BTreeMap::new();
    for (k, v) in all_functions {
        out.insert(k, v);
    }
    out
}

pub fn build_api_surface(call_graph: &BTreeMap<String, Value>) -> Value {
    let mut surface = Vec::new();
    for (key, value) in call_graph {
        if value
            .get("is_entry_point")
            .and_then(|v| v.as_bool())
            .unwrap_or(false)
        {
            surface.push(json!({
                "function_key": key,
                "file": value.get("file"),
                "name": value.get("name"),
                "line": value.get("start_line"),
            }));
        }
    }
    Value::Array(surface)
}

pub fn call_graph_to_json(cg: &BTreeMap<String, Value>) -> Value {
    let mut m = Map::new();
    for (k, v) in cg {
        m.insert(k.clone(), v.clone());
    }
    Value::Object(m)
}
