//! Dead code map matching DeadCodeDetector.

use once_cell::sync::Lazy;
use regex::Regex;
use serde_json::{json, Map, Value};
use std::collections::BTreeMap;

static TEST_FILE_PATTERNS: Lazy<Vec<Regex>> = Lazy::new(|| {
    [
        r"^test_",
        r"_test\.py$",
        r"_test\.js$",
        r"_test\.ts$",
        r"\.test\.js$",
        r"\.test\.ts$",
        r"\.test\.tsx$",
        r"\.test\.jsx$",
        r"\.spec\.js$",
        r"\.spec\.ts$",
        r"\.spec\.tsx$",
        r"\.spec\.jsx$",
        r"^tests?/",
        r"/tests?/",
        r"__tests__/",
        r"spec/",
        r"/spec/",
    ]
    .iter()
    .map(|p| Regex::new(&format!("(?i){}", p)).unwrap())
    .collect()
});

static MIGRATION_PATTERNS: Lazy<Vec<Regex>> = Lazy::new(|| {
    ["migration", "seed", "fixture", "mock", "factory", "populate"]
        .iter()
        .map(|p| Regex::new(&format!("(?i){}", p)).unwrap())
        .collect()
});

fn is_test_file(filepath: &str) -> bool {
    let normalized = filepath.replace('\\', "/");
    TEST_FILE_PATTERNS.iter().any(|re| re.is_match(&normalized))
}

fn is_migration_file(filepath: &str) -> bool {
    let normalized = filepath.replace('\\', "/");
    MIGRATION_PATTERNS.iter().any(|re| re.is_match(&normalized))
}

fn count_inbound(func_key: &str, call_graph: &BTreeMap<String, Value>) -> usize {
    let mut count = 0;
    for other_data in call_graph.values() {
        if let Some(calls) = other_data.get("calls").and_then(|v| v.as_array()) {
            if calls.iter().any(|c| c.as_str() == Some(func_key)) {
                count += 1;
            }
        }
    }
    count
}

fn get_callers(func_key: &str, call_graph: &BTreeMap<String, Value>) -> Vec<String> {
    let mut callers = Vec::new();
    for (other_key, other_data) in call_graph {
        if let Some(calls) = other_data.get("calls").and_then(|v| v.as_array()) {
            if calls.iter().any(|c| c.as_str() == Some(func_key)) {
                callers.push(other_key.clone());
            }
        }
    }
    callers
}

fn caller_files(callers: &[String]) -> Vec<String> {
    let mut files = BTreeMap::new();
    for caller in callers {
        if let Some((file, _)) = caller.split_once("::") {
            files.insert(file.to_string(), ());
        }
    }
    files.into_keys().collect()
}

pub fn build_dead_code_map(call_graph: &BTreeMap<String, Value>) -> Value {
    let mut dead_code_map = Map::new();

    for (func_key, func_data) in call_graph {
        let file_path = func_data
            .get("file")
            .and_then(|v| v.as_str())
            .unwrap_or("");
        let is_entry_point = func_data
            .get("is_entry_point")
            .and_then(|v| v.as_bool())
            .unwrap_or(false);

        if is_entry_point {
            dead_code_map.insert(
                func_key.clone(),
                json!({
                    "inbound_call_count": -1,
                    "is_dead": false,
                    "is_test_only": false,
                    "is_entry_point": true,
                    "called_from_files": [],
                }),
            );
            continue;
        }

        let inbound_count = count_inbound(func_key, call_graph);
        let callers = get_callers(func_key, call_graph);
        let caller_files_list = caller_files(&callers);

        let mut is_dead = inbound_count == 0;
        let mut is_test_only = false;

        if !is_dead {
            let all_tests = !caller_files_list.is_empty()
                && caller_files_list.iter().all(|f| is_test_file(f));
            if all_tests {
                is_test_only = true;
            }
        }

        if is_test_file(file_path) || is_migration_file(file_path) {
            is_test_only = true;
        }

        // silence unused mut warning path for is_dead
        let _ = &mut is_dead;

        dead_code_map.insert(
            func_key.clone(),
            json!({
                "inbound_call_count": inbound_count,
                "is_dead": is_dead,
                "is_test_only": is_test_only,
                "is_entry_point": false,
                "called_from_files": caller_files_list,
            }),
        );
    }

    Value::Object(dead_code_map)
}
