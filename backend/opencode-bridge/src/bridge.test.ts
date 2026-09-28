import assert from "node:assert/strict";
import { describe, it } from "node:test";

import { Bridge, isUnreachableError, OpenCodeUnreachableError } from "./bridge.js";
import { parseListenAddr, parseListenHostPort } from "./config.js";
import { resolveModelId } from "./constants.js";
import { shouldRejectPermission } from "./permissions.js";
import { createServer } from "./server.js";

describe("shouldRejectPermission", () => {
  const cases: Array<[string, boolean]> = [
    ["bash", true],
    ["Bash", true],
    ["shell", true],
    ["edit", true],
    ["write", true],
    ["read", false],
    ["glob", false],
    ["", false],
    ["  EDIT ", true],
  ];
  for (const [input, want] of cases) {
    it(`${input}`, () => {
      assert.equal(shouldRejectPermission(input), want);
    });
  }
});

describe("parseListenAddr", () => {
  const cases: Record<string, string> = {
    "": "127.0.0.1:5010",
    ":8080": "127.0.0.1:8080",
    "5010": "127.0.0.1:5010",
    "0.0.0.0:5010": "0.0.0.0:5010",
  };
  for (const [input, want] of Object.entries(cases)) {
    it(input || "(empty)", () => {
      assert.equal(parseListenAddr(input), want);
    });
  }
});

describe("parseListenHostPort", () => {
  it("defaults", () => {
    assert.deepEqual(parseListenHostPort(""), { host: "127.0.0.1", port: 5010 });
  });
  it("host and port", () => {
    assert.deepEqual(parseListenHostPort("127.0.0.1:5010"), { host: "127.0.0.1", port: 5010 });
  });
});

describe("resolveModelId", () => {
  it("aliases deepseek-flash to Go id", () => {
    assert.equal(resolveModelId("deepseek-flash"), "deepseek-v4.1-flash");
  });
  it("aliases dsv4.1flash to Go catalog id", () => {
    assert.equal(resolveModelId("dsv4.1flash"), "deepseek-v4.1-flash");
  });
  it("strips provider prefix", () => {
    assert.equal(resolveModelId("opencode-go/kimi-k3"), "kimi-k3");
  });
});

describe("HTTP handlers", () => {
  it("GET /health reports unreachable OpenCode", async () => {
    const bridge = new Bridge({
      baseURL: "http://127.0.0.1:59991",
      workDir: process.cwd(),
      autostart: false,
    });
    const server = createServer(bridge);
    await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", () => resolve()));
    const addr = server.address();
    assert(addr && typeof addr === "object");
    const res = await fetch(`http://127.0.0.1:${addr.port}/health`);
    assert.equal(res.status, 200);
    const body = await res.json();
    assert.equal(body.model, resolveModelId(process.env.SCAN_MODEL));
    assert.equal(body.opencode, "unreachable");
    server.close();
  });

  it("POST /complete rejects missing scan_id", async () => {
    const bridge = new Bridge({
      baseURL: "http://127.0.0.1:59991",
      workDir: process.cwd(),
      autostart: false,
    });
    const server = createServer(bridge);
    await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", () => resolve()));
    const addr = server.address();
    assert(addr && typeof addr === "object");
    const res = await fetch(`http://127.0.0.1:${addr.port}/complete`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scan_id: "", user: "hi" }),
    });
    assert.equal(res.status, 400);
    server.close();
  });

    it("unreachable complete does not mention OpenRouter", async () => {
    process.env.OPENCODE_API_KEY = "test-key";
    const bridge = new Bridge({
      baseURL: "http://127.0.0.1:59991",
      workDir: process.cwd(),
      autostart: false,
    });
    await assert.rejects(
      () => bridge.complete("scan-1", "sys", "user prompt"),
      (err: unknown) => {
        assert.ok(err instanceof Error);
        assert.ok(
          err instanceof OpenCodeUnreachableError ||
            isUnreachableError(err) ||
            err.message.toLowerCase().includes("unreachable"),
        );
        assert.ok(!err.message.toLowerCase().includes("openrouter"));
        return true;
      },
    );

    const server = createServer(bridge);
    await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", () => resolve()));
    const addr = server.address();
    assert(addr && typeof addr === "object");
    const res = await fetch(`http://127.0.0.1:${addr.port}/complete`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scan_id: "scan-1", system: "s", user: "u" }),
    });
    assert.equal(res.status, 503);
    const body = await res.json();
    assert.ok(body.error);
    assert.ok(!String(body.error).toLowerCase().includes("openrouter"));
    server.close();
  });
});
