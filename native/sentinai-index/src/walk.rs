//! Shared filesystem helpers for source discovery.

use std::collections::HashSet;
use std::path::{Path, PathBuf};
use walkdir::WalkDir;

const SKIP_DIRS: &[&str] = &[
    "node_modules", "venv", ".venv", "__pycache__", ".git", "dist", "build",
    ".next", "target", "vendor", "third_party",
];

const VALID_EXTS: &[&str] = &[".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".go", ".mjs", ".php"];

pub fn detect_language(filepath: &str) -> Option<&'static str> {
    let lower = filepath.to_lowercase();
    if lower.ends_with(".py") {
        Some("python")
    } else if lower.ends_with(".js") || lower.ends_with(".jsx") || lower.ends_with(".mjs") {
        Some("javascript")
    } else if lower.ends_with(".ts") || lower.ends_with(".tsx") {
        Some("typescript")
    } else if lower.ends_with(".java") {
        Some("java")
    } else if lower.ends_with(".go") {
        Some("go")
    } else if lower.ends_with(".php") {
        Some("php")
    } else {
        None
    }
}

/// Relative path using OS separators (matches Python os.path.relpath).
pub fn rel_path(project_root: &Path, full: &Path) -> String {
    full.strip_prefix(project_root)
        .unwrap_or(full)
        .to_string_lossy()
        .to_string()
}

pub fn list_source_files(project_root: &Path) -> Vec<PathBuf> {
    let skip: HashSet<&str> = SKIP_DIRS.iter().copied().collect();
    let mut out = Vec::new();
    for entry in WalkDir::new(project_root)
        .into_iter()
        .filter_entry(|e| {
            if e.file_type().is_dir() {
                let name = e.file_name().to_string_lossy();
                !skip.contains(name.as_ref())
            } else {
                true
            }
        })
        .filter_map(|e| e.ok())
    {
        if !entry.file_type().is_file() {
            continue;
        }
        let path = entry.path();
        let ext = path
            .extension()
            .and_then(|e| e.to_str())
            .map(|e| format!(".{}", e.to_lowercase()))
            .unwrap_or_default();
        if VALID_EXTS.contains(&ext.as_str()) {
            out.push(path.to_path_buf());
        }
    }
    out.sort();
    out
}

pub fn read_file(path: &Path) -> Option<String> {
    std::fs::read_to_string(path).ok()
}
