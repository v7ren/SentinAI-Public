import { useEffect, useState } from "react";
import "./App.css";
import { ScanPage } from "./pages/ScanPage";
import { SettingsPage } from "./pages/SettingsPage";
import { loadSettings } from "./settings/api";
import type { AppSettings } from "./settings/types";
import { defaultSettings } from "./settings/types";

type Tab = "scan" | "settings";

function App() {
  const [tab, setTab] = useState<Tab>("scan");
  const [settings, setSettings] = useState<AppSettings>(defaultSettings);

  useEffect(() => {
    void loadSettings().then(setSettings);
  }, []);

  return (
    <main className="app">
      <header>
        <h1>SentinAI</h1>
        <nav>
          <button type="button" className={tab === "scan" ? "active" : ""} onClick={() => setTab("scan")}>
            Scan
          </button>
          <button
            type="button"
            className={tab === "settings" ? "active" : ""}
            onClick={() => setTab("settings")}
          >
            Settings
          </button>
        </nav>
      </header>
      {tab === "settings" ? (
        <SettingsPage onSaved={setSettings} />
      ) : (
        <ScanPage settings={settings} />
      )}
    </main>
  );
}

export default App;
