import path from "node:path";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

export function envOr(name: string, fallback: string): string {
  const v = process.env[name];
  return v !== undefined && v !== "" ? v : fallback;
}

/** host:port for the bridge HTTP server (matches legacy Go parsing). */
export function parseListenAddr(raw: string): string {
  const trimmed = raw.trim();
  if (!trimmed) return "127.0.0.1:5010";
  if (trimmed.startsWith(":")) return `127.0.0.1${trimmed}`;
  if (/^\d+$/.test(trimmed)) return `127.0.0.1:${trimmed}`;
  return trimmed;
}

export type ListenHostPort = { host: string; port: number };

/** Split normalized host:port for Node `server.listen(port, host)` (not a pipe path). */
export function parseListenHostPort(raw: string): ListenHostPort {
  const normalized = parseListenAddr(raw);
  const lastColon = normalized.lastIndexOf(":");
  if (lastColon <= 0) {
    return { host: "127.0.0.1", port: 5010 };
  }
  const host = normalized.slice(0, lastColon);
  const port = Number(normalized.slice(lastColon + 1));
  if (!Number.isInteger(port) || port < 0 || port > 65535) {
    throw new Error(`invalid BRIDGE_LISTEN port: ${raw}`);
  }
  return { host, port };
}

/** Directory containing opencode.json (backend/opencode-bridge). */
export function defaultWorkDir(): string {
  const here = path.dirname(fileURLToPath(import.meta.url));
  return path.resolve(here, "..");
}

/** Load %LOCALAPPDATA%/SentinAI/settings.json into env (OpenCode Go key, scan model). */
export function applyDesktopSettingsEnv(): void {
  const override = process.env.SENTINAI_SETTINGS_PATH;
  const local = process.env.LOCALAPPDATA;
  const home = process.env.HOME || process.env.USERPROFILE;
  const settingsPath =
    override ||
    (local ? path.join(local, "SentinAI", "settings.json") : "") ||
    (home ? path.join(home, "SentinAI", "settings.json") : "");
  if (!settingsPath) return;
  try {
    const raw = readFileSync(settingsPath, "utf8");
    const data = JSON.parse(raw) as Record<string, unknown>;
    const key = data.opencodeApiKey ?? data.opencode_api_key;
    if (typeof key === "string" && key.trim() && !process.env.OPENCODE_API_KEY) {
      process.env.OPENCODE_API_KEY = key.trim();
    }
    const model = data.scanModel ?? data.scan_model;
    if (typeof model === "string" && model.trim() && !process.env.SCAN_MODEL) {
      process.env.SCAN_MODEL = model.trim();
    }
  } catch {
    // Missing or invalid settings file is fine; env/headers still work.
  }
}
