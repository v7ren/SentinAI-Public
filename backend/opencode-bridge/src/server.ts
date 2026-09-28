import http from "node:http";

import { resolveApiKey, withApiKey } from "./apiKey.js";
import { Bridge, isUnreachableError, OpenCodeUnreachableError } from "./bridge.js";
import { MODEL_ID } from "./constants.js";
import { parseListenHostPort } from "./config.js";

export type CompleteRequest = {
  scan_id: string;
  system: string;
  user: string;
};

export type CompleteResponse = {
  scan_id: string;
  text: string;
  session_id?: string;
  model: string;
};

export type ErrorResponse = { error: string };

export type HealthResponse = {
  ok: boolean;
  opencode: string;
  model: string;
  opencode_base_url: string;
};

export function createServer(bridge: Bridge): http.Server {
  return http.createServer((req, res) => {
    void handle(bridge, req, res);
  });
}

async function handle(bridge: Bridge, req: http.IncomingMessage, res: http.ServerResponse): Promise<void> {
  const url = new URL(req.url ?? "/", `http://${req.headers.host ?? "localhost"}`);

  if (req.method === "GET" && url.pathname === "/health") {
    const reachable = await bridge.reachable();
    writeJson(res, 200, {
      ok: true,
      opencode: reachable ? "reachable" : "unreachable",
      model: MODEL_ID,
      opencode_base_url: bridge.baseURL,
    } satisfies HealthResponse);
    return;
  }

  if (req.method === "POST" && url.pathname === "/complete") {
    let body: CompleteRequest;
    try {
      body = await readJson<CompleteRequest>(req);
    } catch (err) {
      writeJson(res, 400, { error: `invalid JSON body: ${formatErr(err)}` } satisfies ErrorResponse);
      return;
    }

    const scanId = (body.scan_id ?? "").trim();
    const user = (body.user ?? "").trim();
    if (!scanId) {
      writeJson(res, 400, { error: "scan_id is required" } satisfies ErrorResponse);
      return;
    }
    if (!user) {
      writeJson(res, 400, { error: "user is required" } satisfies ErrorResponse);
      return;
    }

    const apiKey = resolveApiKey(req.headers);
    try {
      const { text, sessionID } = await withApiKey(apiKey, () =>
        bridge.complete(scanId, body.system ?? "", user),
      );
      writeJson(res, 200, {
        scan_id: scanId,
        text,
        session_id: sessionID,
        model: MODEL_ID,
      } satisfies CompleteResponse);
    } catch (err) {
      let status = 502;
      if (err instanceof OpenCodeUnreachableError || isUnreachableError(err)) {
        status = 503;
      }
      console.error(`opencode-bridge: /complete failed scan_id=${scanId}:`, err);
      writeJson(res, status, { error: formatErr(err) } satisfies ErrorResponse);
    }
    return;
  }

  writeJson(res, 404, { error: "not found" } satisfies ErrorResponse);
}

function readJson<T>(req: http.IncomingMessage): Promise<T> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    req.on("data", (c) => chunks.push(c));
    req.on("end", () => {
      try {
        const raw = Buffer.concat(chunks).toString("utf8");
        resolve(JSON.parse(raw) as T);
      } catch (e) {
        reject(e);
      }
    });
    req.on("error", reject);
  });
}

function writeJson(res: http.ServerResponse, status: number, payload: unknown): void {
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json");
  res.end(JSON.stringify(payload));
}

function formatErr(err: unknown): string {
  if (err instanceof Error) return err.message;
  return String(err);
}

export function newHttpServer(listenAddr: string, bridge: Bridge): http.Server {
  const { host, port } = parseListenHostPort(listenAddr);
  const server = createServer(bridge);
  server.requestTimeout = 10 * 60 * 1000;
  server.headersTimeout = 10_000;
  server.on("error", (err) => {
    console.error(`opencode-bridge: failed to listen on ${host}:${port}:`, err);
    process.exit(1);
  });
  server.listen(port, host, () => {
    console.log(
      `opencode-bridge listening on http://${host}:${port} (opencode=${bridge.baseURL} model=${MODEL_ID})`,
    );
  });
  return server;
}
