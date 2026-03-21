import { NextRequest, NextResponse } from "next/server";
const BACKEND_URL = process.env.SENTINEL_API_URL ||
    process.env.SENTINAL_API_URL ||
    "https://5001.use-your-own-domain.com";
export const dynamic = "force-dynamic";
export const runtime = "nodejs";
export async function GET(request: NextRequest) {
    const cookie = request.headers.get("cookie") ?? "";
    try {
        const res = await fetch(`${BACKEND_URL}/api/admin/worker-activity/stream`, {
            cache: "no-store",
            headers: {
                Accept: "text/event-stream",
                Cookie: cookie,
            },
        });
        try {
            await fetch("http://127.0.0.1:7566/ingest/343a6e7b-3306-4160-a101-8c37ff48a773", {
                method: "POST",
                headers: { "Content-Type": "application/json", "X-Debug-Session-Id": "600d04" },
                body: JSON.stringify({
                    sessionId: "600d04",
                    location: "worker-activity/stream/route.ts:after-fetch",
                    message: "Backend worker-activity stream response",
                    data: { ok: res.ok, status: res.status, backendUrl: BACKEND_URL ? "set" : "missing" },
                    timestamp: Date.now(),
                    hypothesisId: "H2",
                }),
            });
        }
        catch {
        }
        if (!res.ok) {
            const text = await res.text();
            let data: unknown = { error: text || res.statusText };
            try {
                data = JSON.parse(text);
            }
            catch {
            }
            return NextResponse.json(data, { status: res.status });
        }
        const stream = res.body;
        if (!stream) {
            return NextResponse.json({ error: "No stream" }, { status: 502 });
        }
        return new NextResponse(stream, {
            headers: {
                "Content-Type": "text/event-stream; charset=utf-8",
                "Cache-Control": "no-cache, no-store, must-revalidate",
                Connection: "keep-alive",
                "X-Accel-Buffering": "no",
            },
        });
    }
    catch (err) {
        const message = err instanceof Error ? err.message : String(err);
        return NextResponse.json({ error: message || "Proxy request failed" }, { status: 502 });
    }
}
