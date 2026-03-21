import { NextRequest, NextResponse } from "next/server";
const BACKEND_URL = process.env.SENTINEL_API_URL || "https://5001.use-your-own-domain.com";
const PROXY_SECRET = process.env.PROXY_SECRET || "";
export const dynamic = "force-dynamic";
export const runtime = "nodejs";
export async function POST(request: NextRequest) {
    try {
        const formData = await request.formData();
        const headers: Record<string, string> = {};
        if (PROXY_SECRET) {
            headers["X-Proxy-Secret"] = PROXY_SECRET;
        }
        const res = await fetch(`${BACKEND_URL}/api/scan/start`, {
            method: "POST",
            body: formData,
            headers,
            signal: AbortSignal.timeout(30000),
        });
        const data = await res.json().catch(() => ({ error: "Invalid JSON from backend" }));
        if (!res.ok) {
            return NextResponse.json(data, { status: res.status });
        }
        return NextResponse.json(data);
    }
    catch (err) {
        const message = err instanceof Error ? err.message : String(err);
        return NextResponse.json({ error: message || "Proxy request failed" }, { status: 502 });
    }
}
