import { NextRequest, NextResponse } from "next/server";
const BACKEND_URL = process.env.SENTINEL_API_URL ||
    process.env.SENTINAL_API_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    "http://localhost:5001";
export async function GET(request: NextRequest) {
    const cookie = request.headers.get("cookie") ?? "";
    try {
        const res = await fetch(`${BACKEND_URL}/auth/admin/me`, {
            cache: "no-store",
            headers: { Cookie: cookie },
        });
        const data = await res.json().catch(() => ({}));
        return NextResponse.json(data, { status: res.status });
    }
    catch (err) {
        const message = err instanceof Error ? err.message : String(err);
        return NextResponse.json({ error: message || "Proxy request failed" }, { status: 502 });
    }
}
