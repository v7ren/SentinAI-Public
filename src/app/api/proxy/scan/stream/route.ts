import { NextRequest, NextResponse } from "next/server";
const BACKEND_URL = process.env.SENTINEL_API_URL || "https://5001.use-your-own-domain.com";
export async function POST(request: NextRequest) {
    try {
        const formData = await request.formData();
        const res = await fetch(`${BACKEND_URL}/api/scan/stream`, {
            method: "POST",
            body: formData,
            signal: AbortSignal.timeout(600000),
        });
        if (!res.ok) {
            const text = await res.text();
            try {
                return NextResponse.json(JSON.parse(text), { status: res.status });
            }
            catch {
                return NextResponse.json({ error: text || res.statusText }, { status: res.status });
            }
        }
        const contentType = res.headers.get("Content-Type") || "text/event-stream; charset=utf-8";
        const stream = res.body;
        if (!stream) {
            return NextResponse.json({ error: "No response body" }, { status: 502 });
        }
        return new NextResponse(stream, {
            headers: {
                "Content-Type": contentType,
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "X-Accel-Buffering": "no",
            },
        });
    }
    catch (err) {
        const message = err instanceof Error ? err.message : String(err);
        if (message.includes("timeout") || message.includes("aborted")) {
            return NextResponse.json({ error: "Scan timed out. Try fewer/smaller files or use non-streaming." }, { status: 504 });
        }
        return NextResponse.json({ error: message || "Proxy request failed" }, { status: 502 });
    }
}
