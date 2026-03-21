import { NextRequest, NextResponse } from "next/server";
const BACKEND_URL = process.env.SENTINEL_API_URL ||
    process.env.SENTINAL_API_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    "http://localhost:5001";
export async function POST(request: NextRequest) {
    let body: {
        account?: string;
        password?: string;
    };
    try {
        body = await request.json();
    }
    catch {
        return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
    }
    try {
        const res = await fetch(`${BACKEND_URL}/auth/admin-login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Cookie: request.headers.get("cookie") ?? "",
            },
            body: JSON.stringify({
                account: body.account ?? "",
                password: body.password ?? "",
            }),
        });
        const data = await res.json().catch(() => ({}));
        const nextRes = NextResponse.json(data, { status: res.status });
        const setCookies = res.headers.getSetCookie?.() ?? (res.headers.get("set-cookie") ? [res.headers.get("set-cookie")!] : []);
        for (const c of setCookies) {
            nextRes.headers.append("Set-Cookie", c);
        }
        return nextRes;
    }
    catch (err) {
        const message = err instanceof Error ? err.message : String(err);
        return NextResponse.json({ error: message || "Proxy request failed" }, { status: 502 });
    }
}
