import { invoke } from "@tauri-apps/api/core";
import type { AppSettings } from "./types";
import { defaultSettings } from "./types";

const LEGACY_FLASH_MODELS = new Set([
  "deepseek-flash",
  "deepseek-v4-flash",
  "dsv4.1flash",
  "dsv4.1-flash",
]);

export async function loadSettings(): Promise<AppSettings> {
  try {
    const raw = await invoke<AppSettings>("read_settings_file");
    const merged = { ...defaultSettings, ...raw };
    if (LEGACY_FLASH_MODELS.has(merged.scanModel)) {
      merged.scanModel = defaultSettings.scanModel;
    }
    return merged;
  } catch {
    return { ...defaultSettings };
  }
}

export async function saveSettings(settings: AppSettings): Promise<void> {
  await invoke("write_settings_file", { settings });
}

export async function settingsPath(): Promise<string> {
  return invoke<string>("settings_file_location");
}
