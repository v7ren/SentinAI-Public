import { NextRequest, NextResponse } from "next/server";
const BACKEND_URL = process.env.SENTINEL_API_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001";
export const dynamic = "force-dynamic";
export const runtime = "nodejs";
export async function GET(request: NextRequest) {
    const scanId = request.nextUrl.searchParams.get("scan_id");
    if (!scanId) {
        return NextResponse.json({ error: "Missing scan_id" }, { status: 400 });
    }
    try {
        const headers: Record<string, string> = { Accept: "text/event-stream" };
        const cookie = request.headers.get("cookie");
        if (cookie)
            headers["Cookie"] = cookie;
        const res = await fetch(`${BACKEND_URL}/api/scan/events/${encodeURIComponent(scanId)}`, {
            cache: "no-store",
            headers,
        });
        if (res.status === 404) {
            return new NextResponse(JSON.stringify({ error: "Event stream not ready. Retrying..." }), {
                status: 503,
                headers: {
                    "Content-Type": "application/json",
                    "Retry-After": "2",
                },
            });
        }
        if (!res.ok) {
            const text = await res.text();
            try {
                return NextResponse.json(JSON.parse(text), { status: res.status });
            }
            catch {
                return NextResponse.json({ error: text || res.statusText }, { status: res.status });
            }
        }
        const stream = res.body;
        if (!stream) {
            return NextResponse.json({ error: "No stream" }, { status: 502 });
        }
        return new NextResponse(stream, {
            headers: {
                "Content-Type": "text/event-stream; charset=utf-8",
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        });
    }
    catch (err) {
        const message = err instanceof Error ? err.message : String(err);
        return NextResponse.json({ error: message || "Proxy request failed" }, { status: 502 });
    }
}
