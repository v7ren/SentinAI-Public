import { NextRequest, NextResponse } from "next/server";
const BACKEND_URL = process.env.SENTINEL_API_URL || "https://5001.use-your-own-domain.com";
export async function POST(request: NextRequest) {
    try {
        const formData = await request.formData();
        const res = await fetch(`${BACKEND_URL}/api/scan`, {
            method: "POST",
            body: formData,
            signal: AbortSignal.timeout(600000),
        });
        const data = await res.json().catch(() => ({ error: "Invalid JSON from backend" }));
        if (!res.ok) {
            return NextResponse.json(data, { status: res.status });
        }
        return NextResponse.json(data);
    }
    catch (err) {
        const message = err instanceof Error ? err.message : String(err);
        if (message.includes("timeout") || message.includes("aborted")) {
            return NextResponse.json({ error: "Scan timed out. Try fewer/smaller files." }, { status: 504 });
        }
        return NextResponse.json({ error: message || "Proxy request failed" }, { status: 502 });
    }
}
