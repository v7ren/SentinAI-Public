//! Symbol index matching ProjectIndexer (regex-based).

use regex::Regex;
use serde_json::{json, Map, Value};
use std::collections::{BTreeMap, HashSet};

struct LangPatterns {
    patterns: Vec<Regex>,
}

fn patterns() -> BTreeMap<&'static str, LangPatterns> {
    let mut m = BTreeMap::new();
    m.insert(
        "python",
        LangPatterns {
            patterns: vec![
                Regex::new(r"(?m)^[ \t]*def\s+([a-zA-Z0-9_]+)\s*\(").unwrap(),
                Regex::new(r"(?m)^[ \t]*class\s+([a-zA-Z0-9_]+)").unwrap(),
            ],
        },
    );
    m.insert(
        "javascript",
        LangPatterns {
            patterns: vec![
                Regex::new(r"function\s+([a-zA-Z0-9_]+)\s*\(").unwrap(),
                Regex::new(r"class\s+([a-zA-Z0-9_]+)").unwrap(),
                Regex::new(
                    r"(?:const|let|var)\s+([a-zA-Z0-9_]+)\s*=\s*(?:async\s*)?(?:\(|[a-zA-Z0-9_]+)\s*=>",
                )
                .unwrap(),
                Regex::new(r"([a-zA-Z0-9_]+)\s*:\s*function").unwrap(),
            ],
        },
    );
    m.insert(
        "java",
        LangPatterns {
            patterns: vec![
                Regex::new(r"(?:public|private|protected|static|\s)+\s*[\w.<>\[\]]+\s+([a-zA-Z0-9_]+)\s*\(").unwrap(),
                Regex::new(r"class\s+([a-zA-Z0-9_]+)").unwrap(),
            ],
        },
    );
    m.insert(
        "go",
        LangPatterns {
            patterns: vec![
                Regex::new(r"func\s+([a-zA-Z0-9_]+)\s*\(").unwrap(),
                Regex::new(r"func\s+\(.*\)\s+([a-zA-Z0-9_]+)\s*\(").unwrap(),
            ],
        },
    );
    m.insert(
        "php",
        LangPatterns {
            patterns: vec![
                Regex::new(r"function\s+([a-zA-Z0-9_]+)\s*\(").unwrap(),
                Regex::new(r"class\s+([a-zA-Z0-9_]+)").unwrap(),
            ],
        },
    );
    m
}

fn lang_for_path(filepath: &str) -> Option<&'static str> {
    if filepath.ends_with(".py") {
        Some("python")
    } else if filepath.ends_with(".js")
        || filepath.ends_with(".ts")
        || filepath.ends_with(".jsx")
        || filepath.ends_with(".tsx")
    {
        Some("javascript")
    } else if filepath.ends_with(".java") {
        Some("java")
    } else if filepath.ends_with(".go") {
        Some("go")
    } else if filepath.ends_with(".php") {
        Some("php")
    } else {
        None
    }
}

pub struct SymbolIndex {
    pub symbol_table: BTreeMap<String, Value>,
    pub file_symbols: BTreeMap<String, Vec<String>>,
    pub call_graph: BTreeMap<String, Vec<String>>,
}

impl SymbolIndex {
    pub fn build(files: &[(String, String)]) -> Self {
        let pats = patterns();
        let mut symbol_table: BTreeMap<String, Value> = BTreeMap::new();
        let mut file_symbols: BTreeMap<String, Vec<String>> = BTreeMap::new();

        for (filepath, content) in files {
            let Some(lang) = lang_for_path(filepath) else {
                continue;
            };
            let Some(lp) = pats.get(lang) else {
                continue;
            };
            let line_limit = if lang == "python" { 50 } else { 30 };
            let mut indexed_names: Vec<String> = Vec::new();

            for pat in &lp.patterns {
                for caps in pat.captures_iter(content) {
                    let name = caps.get(1).map(|m| m.as_str()).unwrap_or("");
                    if name.len() < 2 {
                        continue;
                    }
                    let start = caps.get(0).map(|m| m.start()).unwrap_or(0);
                    let body_slice: Vec<&str> = content[start..].lines().take(line_limit).collect();
                    let code_body = body_slice.join("\n");
                    symbol_table.insert(
                        name.to_string(),
                        json!({
                            "file": filepath,
                            "code": code_body,
                            "dependencies": []
                        }),
                    );
                    if !indexed_names.iter().any(|n| n == name) {
                        indexed_names.push(name.to_string());
                    }
                }
            }
            if !indexed_names.is_empty() {
                file_symbols.insert(filepath.clone(), indexed_names);
            }
        }

        let all_symbols: HashSet<String> = symbol_table.keys().cloned().collect();
        let mut call_graph: BTreeMap<String, Vec<String>> = BTreeMap::new();
        for (name, data) in &symbol_table {
            let body = data
                .get("code")
                .and_then(|v| v.as_str())
                .unwrap_or("");
            let mut deps = Vec::new();
            for other in &all_symbols {
                if other != name && body.contains(other.as_str()) && !deps.contains(other) {
                    deps.push(other.clone());
                }
            }
            call_graph.insert(name.clone(), deps);
        }

        Self {
            symbol_table,
            file_symbols,
            call_graph,
        }
    }

    pub fn to_regex_index_json(&self) -> Value {
        let mut st = Map::new();
        for (k, v) in &self.symbol_table {
            st.insert(k.clone(), v.clone());
        }
        let mut fs = Map::new();
        for (k, v) in &self.file_symbols {
            fs.insert(
                k.clone(),
                Value::Array(v.iter().cloned().map(Value::String).collect()),
            );
        }
        let mut cg = Map::new();
        for (k, v) in &self.call_graph {
            cg.insert(
                k.clone(),
                Value::Array(v.iter().cloned().map(Value::String).collect()),
            );
        }
        json!({
            "symbol_table": Value::Object(st),
            "call_graph": Value::Object(cg),
            "file_symbols": Value::Object(fs),
        })
    }
}
