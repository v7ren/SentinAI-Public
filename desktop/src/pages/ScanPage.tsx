import { open } from "@tauri-apps/plugin-dialog";
import { useEffect, useRef, useState } from "react";
import { eventsUrl, startLocalScan } from "../scan/api";
import type { FindingRow, ScanEvent } from "../scan/types";
import type { AppSettings } from "../settings/types";

type Props = {
  settings: AppSettings;
};

export function ScanPage({ settings }: Props) {
  const [folder, setFolder] = useState<string | null>(null);
  const [scanType, setScanType] = useState("2");
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [log, setLog] = useState<string[]>([]);
  const [findings, setFindings] = useState<FindingRow[]>([]);
  const [scanId, setScanId] = useState<string | null>(null);
  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    return () => {
      esRef.current?.close();
    };
  }, []);

  const pickFolder = async () => {
    const selected = await open({ directory: true, multiple: false });
    if (typeof selected === "string") {
      setFolder(selected);
      setStatus(null);
    }
  };

  const pushLog = (line: string) => {
    setLog((prev) => [...prev.slice(-40), line]);
  };

  const startScan = async () => {
    if (!folder) {
      setStatus("Choose a project folder first.");
      return;
    }
    esRef.current?.close();
    setBusy(true);
    setProgress(0);
    setFindings([]);
    setLog([]);
    setScanId(null);
    setStatus(`Calling ${settings.gatewayUrl}/api/scan/local-start …`);

    try {
      const started = await startLocalScan({
        settings,
        sourceDir: folder,
        scanType,
      });
      setScanId(started.scan_id);
      const count = started.file_count != null ? ` (${started.file_count} files)` : "";
      setStatus(`Scan ${started.scan_id}${count}`);
      pushLog(`Started ${started.scan_id}${count}`);

      const es = new EventSource(eventsUrl(settings.gatewayUrl, started.scan_id));
      esRef.current = es;
      es.onmessage = (e) => {
        let event: ScanEvent;
        try {
          event = JSON.parse(e.data) as ScanEvent;
        } catch {
          return;
        }
        const kind = event.type;
        if (kind === "vuln_found") {
          const n = event.count || 0;
          const msg = `Found ${n} issue${n !== 1 ? "s" : ""} in ${event.filename}`;
          setStatus(msg);
          pushLog(msg);
          const rows = (event.issues || []).map((issue) => ({
            file: event.filename || "",
            type: issue.type || "Unknown",
            severity: issue.severity || "",
            line: issue.line || 0,
            description: issue.description || "",
          }));
          setFindings((prev) => [...prev, ...rows]);
        } else if (kind === "file_safe") {
          pushLog(`OK ${event.filename}`);
        } else if (kind === "progress") {
          if (event.total_files && event.total_files > 0 && event.files_scanned != null) {
            setProgress(Math.round((100 * event.files_scanned) / event.total_files));
          }
        } else if (kind === "log" || kind === "start") {
          if (event.msg) {
            setStatus(event.msg);
            pushLog(event.msg);
          }
        } else if (kind === "complete") {
          setProgress(100);
          setStatus("Scan complete");
          pushLog("Scan complete");
          es.close();
          esRef.current = null;
          setBusy(false);
        } else if (kind === "_final") {
          if (event.error) {
            setStatus(event.error);
            pushLog(`Error: ${event.error}`);
          }
          es.close();
          esRef.current = null;
          setBusy(false);
        }
      };
      es.onerror = () => {
        if (es.readyState === EventSource.CLOSED) {
          setBusy(false);
          setStatus((prev) => prev || "Event stream closed");
        }
      };
    } catch (err) {
      setBusy(false);
      setStatus(String(err));
    }
  };

  return (
    <div className="panel">
      <h2>Scan</h2>
      <p className="muted">
        Sends the folder path to the gateway at {settings.gatewayUrl}. Engine should be on{" "}
        {settings.engineUrl}.
      </p>
      <button type="button" onClick={pickFolder}>
        Choose project folder
      </button>
      {folder && <p className="path">{folder}</p>}
      <label>
        Scan tier
        <select value={scanType} onChange={(e) => setScanType(e.target.value)} disabled={busy}>
          <option value="1">1 — basic</option>
          <option value="2">2 — standard</option>
          <option value="3">3 — advanced</option>
          <option value="4">4 — full</option>
        </select>
      </label>
      <button type="button" onClick={startScan} disabled={!folder || busy}>
        {busy ? "Scanning…" : "Start scan"}
      </button>
      {scanId && <p className="muted">{scanId}</p>}
      {busy || progress > 0 ? (
        <div className="progress-wrap">
          <div className="progress-bar" style={{ width: `${progress}%` }} />
        </div>
      ) : null}
      {status && <p className="status">{status}</p>}
      {log.length > 0 && (
        <pre className="log">
          {log.join("\n")}
        </pre>
      )}
      {findings.length > 0 && (
        <table className="findings">
          <thead>
            <tr>
              <th>File</th>
              <th>Line</th>
              <th>Type</th>
              <th>Severity</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            {findings.map((row, i) => (
              <tr key={`${row.file}:${row.line}:${i}`}>
                <td>{row.file}</td>
                <td>{row.line || ""}</td>
                <td>{row.type}</td>
                <td>{row.severity}</td>
                <td>{row.description}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
