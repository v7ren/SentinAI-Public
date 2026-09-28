import { spawn, type ChildProcess } from "node:child_process";
import net from "node:net";
import { createOpencodeClient, type OpencodeClient, type TextPart } from "@opencode-ai/sdk/client";

import { activeApiKey, applyKeyToProcessEnv } from "./apiKey.js";
import { MODEL_ID, PROVIDER_ID } from "./constants.js";
import { shouldRejectPermission } from "./permissions.js";

export class OpenCodeUnreachableError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "OpenCodeUnreachableError";
  }
}

export type BridgeConfig = {
  baseURL: string;
  workDir: string;
  autostart: boolean;
};

export class Bridge {
  readonly baseURL: string;
  private readonly client: OpencodeClient;
  private readonly workDir: string;
  private readonly autostart: boolean;
  private readonly sessions = new Map<string, string>();
  private serveCmd: ChildProcess | null = null;
  private permAbort: AbortController | null = null;
  private permWatcherStarted = false;

  constructor(cfg: BridgeConfig) {
    this.baseURL = cfg.baseURL.replace(/\/$/, "");
    this.workDir = cfg.workDir;
    this.autostart = cfg.autostart;
    this.client = createOpencodeClient({
      baseUrl: this.baseURL,
      directory: this.workDir,
    });
  }

  close(): void {
    this.permAbort?.abort();
    this.permAbort = null;
    if (this.serveCmd?.pid) {
      try {
        this.serveCmd.kill();
      } catch {
        // ignore
      }
      this.serveCmd = null;
    }
  }

  async reachable(): Promise<boolean> {
    try {
      const { error } = await this.client.session.list({
        query: { directory: this.workDir },
      });
      return !error;
    } catch {
      return false;
    }
  }

  async ensureOpenCode(): Promise<void> {
    if (await this.waitReachable(3_000)) {
      this.startPermissionWatcher();
      return;
    }
    if (!this.autostart) {
      throw new OpenCodeUnreachableError(
        `opencode server unreachable at ${this.baseURL} (set OPENCODE_BASE_URL or enable OPENCODE_AUTOSTART)`,
      );
    }
    await this.startServe();
    if (await this.waitReachable(30_000)) {
      this.startPermissionWatcher();
      return;
    }
    throw new OpenCodeUnreachableError(
      `opencode server unreachable at ${this.baseURL} after starting opencode serve`,
    );
  }

  private async waitReachable(timeoutMs: number): Promise<boolean> {
    const deadline = Date.now() + timeoutMs;
    while (Date.now() < deadline) {
      if (await this.reachable()) return true;
      await sleep(250);
    }
    return false;
  }

  private async startServe(): Promise<void> {
    if (this.serveCmd) return;

    let host = "127.0.0.1";
    let port = "4096";
    try {
      const u = new URL(this.baseURL);
      if (u.hostname) host = u.hostname;
      if (u.port) port = u.port;
      else if (u.protocol === "https:") port = "443";
    } catch {
      throw new OpenCodeUnreachableError(`invalid OPENCODE_BASE_URL ${this.baseURL}`);
    }

    try {
      await waitForPortFree(host, port, 5_000);
    } catch (err) {
      console.warn(
        `opencode-bridge: port ${host}:${port} not free (${String(err)}); attaching to existing server if reachable`,
      );
      if (await this.waitReachable(15_000)) {
        return;
      }
      throw new OpenCodeUnreachableError(
        `port ${host}:${port} is in use but OpenCode is not reachable at ${this.baseURL} (stop the other process or set OPENCODE_BASE_URL)`,
      );
    }

    const key = activeApiKey();
    const childEnv = { ...process.env };
    if (key) {
      childEnv.OPENCODE_API_KEY = key;
    }
    const cmd = spawn("opencode", ["serve", "--hostname", host, "--port", port], {
      cwd: this.workDir,
      env: childEnv,
      stdio: ["ignore", "inherit", "inherit"],
      shell: process.platform === "win32",
    });
    this.serveCmd = cmd;
    console.log(
      `opencode-bridge: started opencode serve pid=${cmd.pid} at ${this.baseURL} (cwd=${this.workDir})`,
    );
    cmd.on("exit", (code, signal) => {
      if (this.serveCmd === cmd) this.serveCmd = null;
      if (code !== 0 && code !== null) {
        console.warn(`opencode-bridge: opencode serve exited: code=${code} signal=${signal}`);
      }
    });
  }

  private startPermissionWatcher(): void {
    if (this.permWatcherStarted) return;
    this.permWatcherStarted = true;
    this.permAbort = new AbortController();
    void this.watchPermissions(this.permAbort.signal);
  }

  private async watchPermissions(signal: AbortSignal): Promise<void> {
    while (!signal.aborted) {
      try {
        const { stream } = await this.client.event.subscribe({
          query: { directory: this.workDir },
          signal,
        });
        for await (const event of stream) {
          if (signal.aborted) return;
          if (event.type !== "permission.updated") continue;
          const perm = event.properties;
          if (!shouldRejectPermission(perm.type)) continue;
          console.log(
            `opencode-bridge: rejecting permission type="${perm.type}" session=${perm.sessionID} id=${perm.id}`,
          );
          const { error } = await this.client.postSessionIdPermissionsPermissionId({
            path: { id: perm.sessionID, permissionID: perm.id },
            query: { directory: this.workDir },
            body: { response: "reject" },
          });
          if (error) {
            console.warn(`opencode-bridge: permission reject failed: ${JSON.stringify(error)}`);
          }
        }
      } catch (err) {
        if (signal.aborted) return;
        console.warn(`opencode-bridge: event stream ended: ${String(err)} (reconnecting)`);
        await sleep(500);
      }
    }
  }

  async complete(scanID: string, system: string, user: string): Promise<{ text: string; sessionID: string }> {
    const apiKey = activeApiKey();
    if (!apiKey) {
      throw new Error("OPENCODE_API_KEY is required (desktop Settings or X-Opencode-Api-Key)");
    }
    applyKeyToProcessEnv(apiKey);

    await this.ensureOpenCode();

    const sessionID = await this.sessionForScan(scanID);
    const body: {
      parts: Array<{ type: "text"; text: string }>;
      model: { providerID: string; modelID: string };
      system?: string;
      tools: Record<string, boolean>;
    } = {
      parts: [{ type: "text", text: user }],
      model: { providerID: PROVIDER_ID, modelID: MODEL_ID },
      tools: { bash: false, shell: false, edit: false, write: false },
    };
    if (system.trim()) body.system = system;

    const { data, error } = await this.client.session.prompt({
      path: { id: sessionID },
      query: { directory: this.workDir },
      body,
    });
    if (error) {
      if (isUnreachableError(error)) {
        throw new OpenCodeUnreachableError(`opencode server unreachable at ${this.baseURL}: ${formatErr(error)}`);
      }
      throw new Error(formatErr(error));
    }
    return { text: extractAssistantText(data?.parts ?? []), sessionID };
  }

  private async sessionForScan(scanID: string): Promise<string> {
    const existing = this.sessions.get(scanID);
    if (existing) return existing;

    const { data, error } = await this.client.session.create({
      body: { title: `sentinai-scan-${scanID}` },
      query: { directory: this.workDir },
    });
    if (error) {
      if (isUnreachableError(error)) {
        throw new OpenCodeUnreachableError(`opencode server unreachable at ${this.baseURL}: ${formatErr(error)}`);
      }
      throw new Error(formatErr(error));
    }
    if (!data?.id) throw new Error("session create returned no id");

    if (!this.sessions.has(scanID)) {
      this.sessions.set(scanID, data.id);
    }
    return this.sessions.get(scanID)!;
  }
}

function extractAssistantText(parts: Array<{ type: string; text?: string }>): string {
  let out = "";
  for (const part of parts) {
    if (part.type === "text" && typeof (part as TextPart).text === "string") {
      out += (part as TextPart).text;
    }
  }
  return out;
}

export function isUnreachableError(err: unknown): boolean {
  if (err instanceof OpenCodeUnreachableError) return true;
  const msg = formatErr(err).toLowerCase();
  return (
    msg.includes("connection refused") ||
    msg.includes("econnrefused") ||
    msg.includes("no such host") ||
    msg.includes("enotfound") ||
    msg.includes("timeout") ||
    msg.includes("fetch failed") ||
    msg.includes("unreachable")
  );
}

function formatErr(err: unknown): string {
  if (err instanceof Error) return err.message;
  return String(err);
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function waitForPortFree(host: string, port: string, timeoutMs: number): Promise<void> {
  const deadline = Date.now() + timeoutMs;
  const addr = `${host}:${port}`;
  return new Promise((resolve, reject) => {
    const tryListen = () => {
      const server = net.createServer();
      server.once("error", () => {
        if (Date.now() >= deadline) {
          reject(new Error(`address ${addr} still in use`));
          return;
        }
        setTimeout(tryListen, 100);
      });
      server.once("listening", () => {
        server.close(() => resolve());
      });
      server.listen({ port: Number(port), host });
    };
    tryListen();
  });
}
