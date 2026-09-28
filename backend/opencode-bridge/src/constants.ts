import { applyDesktopSettingsEnv } from "./config.js";

applyDesktopSettingsEnv();

const DEFAULT_MODEL_ID = "deepseek-v4.1-flash";

const MODEL_ALIASES: Record<string, string> = {
  "deepseek-flash": DEFAULT_MODEL_ID,
  "deepseek/deepseek-flash": DEFAULT_MODEL_ID,
  "deepseek-v4-flash": DEFAULT_MODEL_ID,
  "dsv4.1flash": DEFAULT_MODEL_ID,
  "dsv4.1-flash": DEFAULT_MODEL_ID,
  "deepseek-v4.1-flash": DEFAULT_MODEL_ID,
};

export const PROVIDER_ID = (process.env.OPENCODE_PROVIDER_ID || "opencode-go").trim();

export function resolveModelId(raw: string | undefined): string {
  let id = (raw || DEFAULT_MODEL_ID).trim();
  if (!id) id = DEFAULT_MODEL_ID;
  const aliased = MODEL_ALIASES[id] || MODEL_ALIASES[id.toLowerCase()];
  if (aliased) return aliased;
  if (id.includes("/")) id = id.split("/").pop() || id;
  return MODEL_ALIASES[id] || MODEL_ALIASES[id.toLowerCase()] || id;
}

export const MODEL_ID = resolveModelId(process.env.SCAN_MODEL);
