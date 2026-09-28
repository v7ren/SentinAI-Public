import type { AppSettings } from "../settings/types";

function apiKey(settings: AppSettings): string {
  return settings.workerSecret || settings.closesourceApiKey;
}

export async function startLocalScan(args: {
  settings: AppSettings;
  sourceDir: string;
  scanType: string;
}): Promise<{ scan_id: string; file_count?: number }> {
  const base = args.settings.gatewayUrl.replace(/\/$/, "");
  const res = await fetch(`${base}/api/scan/local-start`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Api-Key": apiKey(args.settings),
    },
    body: JSON.stringify({
      source_dir: args.sourceDir,
      project_name: args.sourceDir.split(/[/\\]/).filter(Boolean).pop() || "Local folder",
      scan_type: args.scanType,
    }),
  });
  const body = (await res.json().catch(() => ({}))) as {
    scan_id?: string;
    file_count?: number;
    error?: string;
  };
  if (!res.ok || !body.scan_id) {
    throw new Error(body.error || `Gateway ${res.status} from ${base}/api/scan/local-start`);
  }
  return { scan_id: body.scan_id, file_count: body.file_count };
}

export function eventsUrl(gatewayUrl: string, scanId: string): string {
  const base = gatewayUrl.replace(/\/$/, "");
  return `${base}/api/scan/events/${encodeURIComponent(scanId)}`;
}
