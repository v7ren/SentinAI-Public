import { AsyncLocalStorage } from "node:async_hooks";
import type { IncomingHttpHeaders } from "node:http";

const requestKey = new AsyncLocalStorage<string>();

/** API key from environment (bridge process). */
export function apiKeyFromEnv(): string {
  return (process.env.OPENCODE_API_KEY || process.env.DEEPSEEK_API_KEY || "").trim();
}

export function activeApiKey(): string {
  return requestKey.getStore() || apiKeyFromEnv();
}

export function withApiKey<T>(key: string, fn: () => Promise<T>): Promise<T> {
  return requestKey.run(key.trim(), fn);
}

export function headerApiKey(headers: IncomingHttpHeaders): string {
  const bearer = headers.authorization;
  if (typeof bearer === "string" && bearer.toLowerCase().startsWith("bearer ")) {
    return bearer.slice(7).trim();
  }
  const opencode = headers["x-opencode-api-key"];
  if (typeof opencode === "string" && opencode.trim()) return opencode.trim();
  const deepseek = headers["x-deepseek-key"];
  if (typeof deepseek === "string" && deepseek.trim()) return deepseek.trim();
  return "";
}

export function resolveApiKey(headers: IncomingHttpHeaders): string {
  return headerApiKey(headers) || apiKeyFromEnv();
}

/** Ensure OpenCode child processes see the active key. */
export function applyKeyToProcessEnv(key: string): void {
  if (!key) return;
  process.env.OPENCODE_API_KEY = key;
}
