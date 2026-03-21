import { NextRequest, NextResponse } from "next/server";
const BACKEND_URL = process.env.SENTINEL_API_URL ||
    process.env.SENTINAL_API_URL ||
    "https://5001.use-your-own-domain.com";
export async function GET(request: NextRequest) {
    const cookie = request.headers.get("cookie") ?? "";
    try {
        const res = await fetch(`${BACKEND_URL}/api/admin/worker-activity`, {
            cache: "no-store",
            headers: { Cookie: cookie },
        });
        const data = await res.json().catch(() => ({}));
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
