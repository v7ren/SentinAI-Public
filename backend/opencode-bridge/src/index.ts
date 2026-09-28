import { apiKeyFromEnv } from "./apiKey.js";
import { Bridge } from "./bridge.js";
import { applyDesktopSettingsEnv, defaultWorkDir, envOr, parseListenAddr } from "./config.js";
import { newHttpServer } from "./server.js";

applyDesktopSettingsEnv();

const workDir = defaultWorkDir();
const baseURL = envOr("OPENCODE_BASE_URL", "http://127.0.0.1:4096");
const listen = parseListenAddr(envOr("BRIDGE_LISTEN", "127.0.0.1:5010"));
const autostart = envOr("OPENCODE_AUTOSTART", "1") !== "0";

if (!apiKeyFromEnv()) {
  console.warn(
    "opencode-bridge: warning: OPENCODE_API_KEY unset; set it in desktop Settings or X-Opencode-Api-Key",
  );
}

const bridge = new Bridge({ baseURL, workDir, autostart });

bridge.ensureOpenCode().catch((err) => {
  console.warn(`opencode-bridge: OpenCode not ready at startup: ${String(err)} (will retry on /complete)`);
});

const server = newHttpServer(listen, bridge);

function shutdown() {
  bridge.close();
  server.close();
  process.exit(0);
}

process.on("SIGINT", shutdown);
process.on("SIGTERM", shutdown);
