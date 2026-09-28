import { useEffect, useState } from "react";
import type { AppSettings } from "../settings/types";
import { loadSettings, saveSettings, settingsPath } from "../settings/api";

type Props = {
  onSaved?: (s: AppSettings) => void;
};

export function SettingsPage({ onSaved }: Props) {
  const [form, setForm] = useState<AppSettings | null>(null);
  const [path, setPath] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    void (async () => {
      setForm(await loadSettings());
      setPath(await settingsPath());
    })();
  }, []);

  if (!form) {
    return <p className="muted">Loading settings…</p>;
  }

  const update = (key: keyof AppSettings, value: string) => {
    setForm((prev) => (prev ? { ...prev, [key]: value } : prev));
  };

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setStatus(null);
    try {
      await saveSettings(form);
      setStatus("Saved. Restart the gateway and engine so they pick up the new values.");
      onSaved?.(form);
    } catch (err) {
      setStatus(`Save failed: ${String(err)}`);
    } finally {
      setSaving(false);
    }
  };

  return (
    <form className="panel" onSubmit={onSubmit}>
      <h2>Settings</h2>
      <p className="muted">
        Keys and URLs are stored locally (not in <code>.env</code>). Python services read{" "}
        <code>{path || "%LOCALAPPDATA%\\SentinAI\\settings.json"}</code> on startup.
      </p>

      <label>
        Gateway URL
        <input
          value={form.gatewayUrl}
          onChange={(e) => update("gatewayUrl", e.target.value)}
          placeholder="http://127.0.0.1:5001"
        />
      </label>
      <label>
        Engine URL
        <input
          value={form.engineUrl}
          onChange={(e) => update("engineUrl", e.target.value)}
          placeholder="http://127.0.0.1:5002"
        />
      </label>
      <label>
        OpenCode bridge URL
        <input
          value={form.opencodeBridgeUrl}
          onChange={(e) => update("opencodeBridgeUrl", e.target.value)}
          placeholder="http://127.0.0.1:5010"
        />
      </label>
      <label>
        OpenCode Go API key
        <input
          type="password"
          value={form.opencodeApiKey}
          onChange={(e) => update("opencodeApiKey", e.target.value)}
          autoComplete="off"
        />
      </label>
      <label>
        Engine API key (CLOSESOURCE_API_KEY)
        <input
          type="password"
          value={form.closesourceApiKey}
          onChange={(e) => update("closesourceApiKey", e.target.value)}
          autoComplete="off"
        />
      </label>
      <label>
        Worker secret
        <input
          type="password"
          value={form.workerSecret}
          onChange={(e) => update("workerSecret", e.target.value)}
          autoComplete="off"
        />
      </label>
      <label>
        Scan model (OpenCode Go id, e.g. dsv4.1flash / deepseek-v4.1-flash)
        <input value={form.scanModel} onChange={(e) => update("scanModel", e.target.value)} />
      </label>

      <button type="submit" disabled={saving}>{saving ? "Saving…" : "Save settings"}</button>
      {status && <p className="status">{status}</p>}
    </form>
  );
}
