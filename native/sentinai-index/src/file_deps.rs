//! File dependency map matching FileDependencyMapper.

use crate::walk::{detect_language, list_source_files, read_file, rel_path};
use regex::Regex;
use serde_json::{json, Map, Value};
use std::collections::{BTreeMap, BTreeSet, HashMap};
use std::path::{Path, PathBuf};
use once_cell::sync::Lazy;

static FROM_IMPORT: Lazy<Regex> = Lazy::new(|| Regex::new(r"(?m)^from\s+([\w.]+)\s+import").unwrap());
static DIRECT_IMPORT: Lazy<Regex> = Lazy::new(|| Regex::new(r"(?m)^import\s+([\w.]+)").unwrap());
static REQUIRE: Lazy<Regex> = Lazy::new(|| Regex::new(r#"require\s*\(\s*['"]([^'"]+)['"]\s*\)"#).unwrap());
static ES6_IMPORT: Lazy<Regex> =
    Lazy::new(|| Regex::new(r#"import\s+(?:.*?\s+from\s+)?['"]([^'"]+)['"]"#).unwrap());
static DYNAMIC_IMPORT: Lazy<Regex> =
    Lazy::new(|| Regex::new(r#"import\s*\(\s*['"]([^'"]+)['"]\s*\)"#).unwrap());
static JAVA_IMPORT: Lazy<Regex> = Lazy::new(|| Regex::new(r"(?m)^import\s+([\w.]+);").unwrap());
static GO_IMPORT: Lazy<Regex> = Lazy::new(|| {
    Regex::new(r#"(?m)^import\s*(?:\([\s\S]*?"([^"]+)".*?\)|"([^"]+)")"#).unwrap()
});

fn extract_imports(content: &str, language: &str) -> Vec<String> {
    let mut imports: BTreeSet<String> = BTreeSet::new();
    match language {
        "python" => {
            for caps in FROM_IMPORT.captures_iter(content) {
                if let Some(m) = caps.get(1) {
                    imports.insert(m.as_str().to_string());
                }
            }
            for caps in DIRECT_IMPORT.captures_iter(content) {
                if let Some(m) = caps.get(1) {
                    imports.insert(m.as_str().to_string());
                }
            }
        }
        "javascript" | "typescript" => {
            for re in [&*REQUIRE, &*ES6_IMPORT, &*DYNAMIC_IMPORT] {
                for caps in re.captures_iter(content) {
                    if let Some(m) = caps.get(1) {
                        imports.insert(m.as_str().to_string());
                    }
                }
            }
        }
        "java" => {
            for caps in JAVA_IMPORT.captures_iter(content) {
                if let Some(m) = caps.get(1) {
                    imports.insert(m.as_str().to_string());
                }
            }
        }
        "go" => {
            for caps in GO_IMPORT.captures_iter(content) {
                let imp = caps.get(1).or_else(|| caps.get(2));
                if let Some(m) = imp {
                    imports.insert(m.as_str().to_string());
                }
            }
        }
        _ => {}
    }
    imports.into_iter().collect()
}

fn resolve_import(
    import_path: &str,
    current_file: &str,
    project_path: &Path,
) -> Option<String> {
    let exts = [
        ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".mjs",
    ];

    if import_path.starts_with("./") || import_path.starts_with("../") {
        let current_dir = project_path.join(Path::new(current_file).parent().unwrap_or(Path::new("")));
        let resolved = current_dir.join(import_path);
        let Ok(resolved) = resolved.canonicalize() else {
            // Fall back to normpath-style without requiring exist
            let resolved = normalize_join(&current_dir, import_path);
            if let Some(rel) = try_with_exts(project_path, &resolved) {
                return Some(rel);
            }
            return None;
        };
        if resolved.starts_with(project_path) {
            let rel = rel_path(project_path, &resolved);
            if project_path.join(&rel).exists() {
                return Some(rel);
            }
            for ext in exts {
                let candidate = format!("{}{}", rel, ext);
                if project_path.join(&candidate).exists() {
                    return Some(candidate);
                }
            }
        }
        return None;
    }

    if import_path.contains('.') && !import_path.starts_with('.') {
        let path_candidate = import_path.replace('.', "/");
        for ext in [
            ".py", ".js", ".ts", "/__init__.py", ".java", ".go", ".mjs",
        ] {
            let full_candidate = format!("{}{}", path_candidate, ext);
            if project_path.join(&full_candidate).exists() {
                return Some(full_candidate);
            }
        }
    }

    if !import_path.starts_with('.') && !import_path.starts_with('/') {
        return Some(format!("EXTERNAL:{}", import_path));
    }
    None
}

fn normalize_join(base: &Path, rel: &str) -> PathBuf {
    let mut parts: Vec<String> = base
        .components()
        .map(|c| c.as_os_str().to_string_lossy().to_string())
        .collect();
    for part in Path::new(rel).components() {
        match part {
            std::path::Component::ParentDir => {
                parts.pop();
            }
            std::path::Component::CurDir => {}
            std::path::Component::Normal(s) => {
                parts.push(s.to_string_lossy().to_string());
            }
            _ => {}
        }
    }
    PathBuf::from(parts.join(std::path::MAIN_SEPARATOR_STR))
}

fn try_with_exts(project_path: &Path, resolved: &Path) -> Option<String> {
    let rel = if let Ok(r) = resolved.strip_prefix(project_path) {
        r.to_string_lossy().to_string()
    } else {
        // On Windows canonicalize may fail; use string after project prefix attempt
        let full = resolved.to_string_lossy().replace('/', std::path::MAIN_SEPARATOR_STR);
        let root = project_path.to_string_lossy().replace('/', std::path::MAIN_SEPARATOR_STR);
        if let Some(stripped) = full.strip_prefix(root.as_str()) {
            stripped.trim_start_matches(['/', '\\']).to_string()
        } else {
            return None;
        }
    };
    if project_path.join(&rel).exists() {
        return Some(rel);
    }
    for ext in [".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".mjs"] {
        let candidate = format!("{}{}", rel, ext);
        if project_path.join(&candidate).exists() {
            return Some(candidate);
        }
    }
    None
}

pub fn build_file_deps(project_root: &Path) -> BTreeMap<String, Value> {
    let source_full = list_source_files(project_root);
    let source_files: Vec<String> = source_full
        .iter()
        .map(|p| rel_path(project_root, p))
        .collect();

    let mut file_imports: HashMap<String, Vec<String>> = HashMap::new();
    let mut external_packages: HashMap<String, BTreeSet<String>> = HashMap::new();

    for rel in &source_files {
        let full = project_root.join(rel);
        let Some(content) = read_file(&full) else {
            continue;
        };
        let Some(language) = detect_language(rel) else {
            continue;
        };
        // typescript uses same patterns as typescript key in Python; detect_language returns typescript for .ts
        let lang = if language == "typescript" {
            "typescript"
        } else {
            language
        };
        let raw = extract_imports(&content, lang);
        let mut resolved_imports = BTreeSet::new();
        let mut externals = BTreeSet::new();
        for imp in raw {
            if let Some(resolved) = resolve_import(&imp, rel, project_root) {
                if let Some(pkg) = resolved.strip_prefix("EXTERNAL:") {
                    externals.insert(pkg.to_string());
                } else {
                    resolved_imports.insert(resolved);
                }
            }
        }
        file_imports.insert(rel.clone(), resolved_imports.into_iter().collect());
        external_packages.insert(rel.clone(), externals);
    }

    let mut reverse: HashMap<String, Vec<String>> = source_files
        .iter()
        .map(|f| (f.clone(), Vec::new()))
        .collect();
    for (file, imports) in &file_imports {
        for imp in imports {
            if let Some(list) = reverse.get_mut(imp) {
                list.push(file.clone());
            }
        }
    }

    let mut file_deps = BTreeMap::new();
    for rel in &source_files {
        file_deps.insert(
            rel.clone(),
            json!({
                "imports": file_imports.get(rel).cloned().unwrap_or_default(),
                "imported_by": reverse.get(rel).cloned().unwrap_or_default(),
                "external_packages": external_packages
                    .get(rel)
                    .map(|s| s.iter().cloned().collect::<Vec<_>>())
                    .unwrap_or_default(),
            }),
        );
    }
    file_deps
}

pub fn file_deps_to_json(deps: &BTreeMap<String, Value>) -> Value {
    let mut m = Map::new();
    for (k, v) in deps {
        m.insert(k.clone(), v.clone());
    }
    Value::Object(m)
}
