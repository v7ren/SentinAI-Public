//! Sanitizer registry matching SanitizerRegistry.

use crate::walk::{detect_language, list_source_files, read_file, rel_path};
use once_cell::sync::Lazy;
use regex::Regex;
use serde_json::{json, Map, Value};
use std::collections::{BTreeMap, BTreeSet};
use std::path::Path;

static SANITIZER_NAME_PATTERNS: Lazy<Vec<Regex>> = Lazy::new(|| {
    [
        r"^sanitize_",
        r"^validate_",
        r"^escape_",
        r"^encode_",
        r"^clean_",
        r"^strip_",
        r"^filter_",
        r"^purify_",
        r"^normalize_",
        r"^hash_",
        r"^encrypt_",
        r"^decrypt_",
        r"^verify_",
        r"^check_",
        r"^is_valid",
        r"_hash$",
        r"_escape$",
        r"_encode$",
        r"_sanitize$",
    ]
    .iter()
    .map(|p| Regex::new(&format!("(?i){}", p)).unwrap())
    .collect()
});

static AUTH_GUARD_PATTERNS: Lazy<Vec<Regex>> = Lazy::new(|| {
    [
        r"@login_required",
        r"@requires_auth",
        r"@jwt_required",
        r"@permission_required",
        r"@authenticate",
        r"@auth_required",
        r"@login_protected",
        r"@admin_required",
        r"@staff_required",
        r"@roles_required",
        r"@fresh_login_required",
        r"@oidc_require_login",
    ]
    .iter()
    .map(|p| Regex::new(p).unwrap())
    .collect()
});

static FRAMEWORK_PATTERNS: Lazy<Vec<(&'static str, Regex)>> = Lazy::new(|| {
    vec![
        ("bleach.clean", Regex::new(r"bleach\.clean\s*\(").unwrap()),
        ("bleach.linkify", Regex::new(r"bleach\.linkify\s*\(").unwrap()),
        (
            "markupsafe.escape",
            Regex::new(r"(?:markupsafe\.)?escape\s*\(").unwrap(),
        ),
        ("markupsafe.Markup", Regex::new(r"Markup\s*\(").unwrap()),
        ("html.escape", Regex::new(r"html\.escape\s*\(").unwrap()),
        ("cgi.escape", Regex::new(r"cgi\.escape\s*\(").unwrap()),
        (
            "urllib.parse.quote",
            Regex::new(r"urllib\.parse\.quote\s*\(").unwrap(),
        ),
        ("bcrypt.checkpw", Regex::new(r"bcrypt\.checkpw\s*\(").unwrap()),
        ("bcrypt.hashpw", Regex::new(r"bcrypt\.hashpw\s*\(").unwrap()),
        ("hashlib.sha256", Regex::new(r"hashlib\.sha256\s*\(").unwrap()),
        ("hashlib.sha512", Regex::new(r"hashlib\.sha512\s*\(").unwrap()),
        (
            "hashlib.pbkdf2_hmac",
            Regex::new(r"hashlib\.pbkdf2_hmac\s*\(").unwrap(),
        ),
        (
            "hmac.compare_digest",
            Regex::new(r"hmac\.compare_digest\s*\(").unwrap(),
        ),
        (
            "secrets.compare_digest",
            Regex::new(r"secrets\.compare_digest\s*\(").unwrap(),
        ),
    ]
});

static PARAM_QUERY_PATTERNS: Lazy<Vec<(&'static str, Regex)>> = Lazy::new(|| {
    vec![
        (
            "sqlalchemy_execute",
            Regex::new(r"(?:session|db|conn|connection)\.execute\s*\([^,]+,\s*[^)]+\)").unwrap(),
        ),
        ("django_raw", Regex::new(r"\.raw\s*\([^,]+,\s*[^)]+\)").unwrap()),
        (
            "cursor_execute",
            Regex::new(r"cursor\.execute\s*\([^,]+,\s*[^)]+\)").unwrap(),
        ),
        (
            "dbapi_execute",
            Regex::new(r"\.execute\s*\([^,]+,\s*[^)]+\)").unwrap(),
        ),
    ]
});

static PY_DEF: Lazy<Regex> = Lazy::new(|| Regex::new(r"^def\s+(\w+)\s*\(").unwrap());
static JS_FUNCS: Lazy<Vec<Regex>> = Lazy::new(|| {
    vec![
        Regex::new(r"function\s+(\w+)\s*\(").unwrap(),
        Regex::new(r"(?:const|let|var)\s+(\w+)\s*=\s*function").unwrap(),
        Regex::new(r"(?:const|let|var)\s+(\w+)\s*=\s*.*?=>").unwrap(),
    ]
});

fn is_sanitizer_name(name: &str) -> bool {
    SANITIZER_NAME_PATTERNS.iter().any(|re| re.is_match(name))
}

struct FuncInfo {
    name: String,
    line: usize,
    is_auth_guard: bool,
}

fn extract_functions(content: &str, language: &str) -> Vec<FuncInfo> {
    let lines: Vec<&str> = content.lines().collect();
    let mut functions = Vec::new();

    if language == "python" {
        let mut decorator_stack: Vec<String> = Vec::new();
        for (line_num, line) in lines.iter().enumerate() {
            let stripped = line.trim();
            if stripped.starts_with('@') {
                decorator_stack.push(stripped.to_string());
                continue;
            }
            if stripped.starts_with("def ") {
                if let Some(caps) = PY_DEF.captures(stripped) {
                    let func_name = caps.get(1).map(|m| m.as_str()).unwrap_or("").to_string();
                    let is_auth_guard = decorator_stack.iter().any(|dec| {
                        AUTH_GUARD_PATTERNS.iter().any(|p| p.is_match(dec))
                    });
                    functions.push(FuncInfo {
                        name: func_name,
                        line: line_num + 1,
                        is_auth_guard,
                    });
                }
                decorator_stack.clear();
            } else if !stripped.is_empty() && !stripped.starts_with('#') {
                decorator_stack.clear();
            }
        }
    } else {
        for (line_num, line) in lines.iter().enumerate() {
            let stripped = line.trim();
            for pattern in JS_FUNCS.iter() {
                if let Some(caps) = pattern.captures(stripped) {
                    if let Some(m) = caps.get(1) {
                        functions.push(FuncInfo {
                            name: m.as_str().to_string(),
                            line: line_num + 1,
                            is_auth_guard: false,
                        });
                        break;
                    }
                }
            }
        }
    }
    functions
}

pub fn build_sanitizer_registry(project_root: &Path) -> Value {
    let mut custom_sanitizers: BTreeSet<String> = BTreeSet::new();
    let mut auth_guards: BTreeSet<String> = BTreeSet::new();
    let mut framework_sanitizers: BTreeSet<String> = BTreeSet::new();
    let mut parameterized_queries: BTreeSet<String> = BTreeSet::new();
    let mut full_map: BTreeMap<String, Value> = BTreeMap::new();

    for full in list_source_files(project_root) {
        let rel = rel_path(project_root, &full);
        let Some(language) = detect_language(&rel) else {
            continue;
        };
        // SanitizerRegistry only processes py/js/ts
        if !matches!(language, "python" | "javascript" | "typescript") {
            continue;
        }
        let Some(content) = read_file(&full) else {
            continue;
        };
        let funcs = extract_functions(&content, language);
        for func in funcs {
            if is_sanitizer_name(&func.name) {
                custom_sanitizers.insert(func.name.clone());
                let key = format!("{}::{}", rel, func.name);
                full_map.insert(
                    key,
                    json!({
                        "name": func.name,
                        "file": rel,
                        "line": func.line,
                        "role": "SANITIZER",
                    }),
                );
            }
            if func.is_auth_guard {
                auth_guards.insert(func.name.clone());
                let key = format!("{}::{}", rel, func.name);
                full_map.insert(
                    key,
                    json!({
                        "name": func.name,
                        "file": rel,
                        "line": func.line,
                        "role": "AUTH_GUARD",
                    }),
                );
            }
        }
        for (name, re) in FRAMEWORK_PATTERNS.iter() {
            if re.is_match(&content) {
                framework_sanitizers.insert((*name).to_string());
            }
        }
        for (name, re) in PARAM_QUERY_PATTERNS.iter() {
            if re.is_match(&content) {
                parameterized_queries.insert(format!("{}:{}", rel, name));
            }
        }
    }

    let mut fm = Map::new();
    for (k, v) in full_map {
        fm.insert(k, v);
    }

    json!({
        "custom_sanitizers": custom_sanitizers.into_iter().collect::<Vec<_>>(),
        "auth_guards": auth_guards.into_iter().collect::<Vec<_>>(),
        "framework_sanitizers": framework_sanitizers.into_iter().collect::<Vec<_>>(),
        "parameterized_queries": parameterized_queries.into_iter().collect::<Vec<_>>(),
        "full_map": Value::Object(fm),
    })
}
