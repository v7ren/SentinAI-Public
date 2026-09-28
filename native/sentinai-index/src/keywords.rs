//! Keyword scanning matching check_keywords in utils.py.

use once_cell::sync::Lazy;
use std::collections::BTreeMap;

static KEYWORDS: Lazy<Vec<String>> = Lazy::new(|| {
    let raw = include_str!("../keywords.json");
    serde_json::from_str::<Vec<String>>(raw)
        .unwrap_or_default()
        .into_iter()
        .filter(|kw| kw.trim().len() >= 2)
        .collect()
});

/// Match Python `check_keywords`: lowercase substring search, max 10 hits.
pub fn check_keywords(content: &str) -> Vec<String> {
    let content_lower = content.to_lowercase();
    let mut found = Vec::new();
    for kw in KEYWORDS.iter() {
        if content_lower.contains(kw) {
            found.push(kw.clone());
            if found.len() >= 10 {
                break;
            }
        }
    }
    found
}

/// Per-file keyword hits for the whole project (relative path -> keywords).
pub fn scan_project_keywords(files: &[(String, String)]) -> BTreeMap<String, Vec<String>> {
    let mut out = BTreeMap::new();
    for (rel, content) in files {
        let hits = check_keywords(content);
        if !hits.is_empty() {
            out.insert(rel.clone(), hits);
        }
    }
    out
}
