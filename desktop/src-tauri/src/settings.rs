use serde::{Deserialize, Serialize};
use std::fs;
use std::path::PathBuf;

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AppSettings {
    pub gateway_url: String,
    pub engine_url: String,
    pub opencode_bridge_url: String,
    pub opencode_api_key: String,
    pub closesource_api_key: String,
    pub worker_secret: String,
    pub scan_model: String,
}

impl Default for AppSettings {
    fn default() -> Self {
        Self {
            gateway_url: "http://127.0.0.1:5001".into(),
            engine_url: "http://127.0.0.1:5002".into(),
            opencode_bridge_url: "http://127.0.0.1:5010".into(),
            opencode_api_key: String::new(),
            closesource_api_key: String::new(),
            worker_secret: String::new(),
            scan_model: "deepseek-flash".into(),
        }
    }
}

pub fn settings_file_path() -> Result<PathBuf, String> {
    let base = std::env::var("LOCALAPPDATA")
        .or_else(|_| std::env::var("HOME"))
        .map_err(|_| "Could not resolve LOCALAPPDATA or HOME")?;
    Ok(PathBuf::from(base).join("SentinAI").join("settings.json"))
}

#[tauri::command]
pub fn read_settings_file() -> Result<AppSettings, String> {
    let path = settings_file_path()?;
    if !path.is_file() {
        return Ok(AppSettings::default());
    }
    let raw = fs::read_to_string(&path).map_err(|e| e.to_string())?;
    serde_json::from_str(&raw).map_err(|e| e.to_string())
}

#[tauri::command]
pub fn write_settings_file(settings: AppSettings) -> Result<(), String> {
    let path = settings_file_path()?;
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent).map_err(|e| e.to_string())?;
    }
    let raw = serde_json::to_string_pretty(&settings).map_err(|e| e.to_string())?;
    fs::write(&path, raw).map_err(|e| e.to_string())?;
    Ok(())
}

#[tauri::command]
pub fn settings_file_location() -> Result<String, String> {
    settings_file_path().map(|p| p.to_string_lossy().into_owned())
}
