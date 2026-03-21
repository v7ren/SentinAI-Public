import { NextRequest, NextResponse } from "next/server";
const BACKEND_URL = process.env.SENTINEL_API_URL || "https://5001.use-your-own-domain.com";
const PROXY_SECRET = process.env.PROXY_SECRET || "";
export const dynamic = "force-dynamic";
export const runtime = "nodejs";
export async function POST(request: NextRequest) {
    try {
        const body = await request.json().catch(() => ({}));
        const { scan_id, use_cache } = body as {
            scan_id?: string;
            use_cache?: boolean;
        };
        const headers: Record<string, string> = {
            "Content-Type": "application/json",
        };
        if (PROXY_SECRET)
            headers["X-Proxy-Secret"] = PROXY_SECRET;
        const cookie = request.headers.get("cookie");
        if (cookie)
            headers["Cookie"] = cookie;
        const res = await fetch(`${BACKEND_URL}/api/scan/cache-choice`, {
            method: "POST",
            headers,
            body: JSON.stringify({ scan_id, use_cache: use_cache ?? true }),
            signal: AbortSignal.timeout(10000),
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
