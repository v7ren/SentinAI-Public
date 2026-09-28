mod settings;

use settings::{read_settings_file, settings_file_location, write_settings_file};

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_store::Builder::default().build())
        .invoke_handler(tauri::generate_handler![
            read_settings_file,
            write_settings_file,
            settings_file_location,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
