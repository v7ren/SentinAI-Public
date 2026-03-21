import { NextRequest, NextResponse } from "next/server";
const LOG_SERVER_URL = (process.env.LOG_SERVER_URL || "http://127.0.0.1:5003").replace(/\/$/, "");
export async function GET(request: NextRequest) {
    const { searchParams } = new URL(request.url);
    const type = searchParams.get("type") || "state";
    const limit = searchParams.get("limit") || "100";
    try {
        if (type === "state") {
            const res = await fetch(`${LOG_SERVER_URL}/api/state`, { cache: "no-store" });
            const data = await res.json().catch(() => ({}));
            if (!res.ok)
                return NextResponse.json(data, { status: res.status });
            return NextResponse.json(data);
        }
        if (type === "history") {
            const res = await fetch(`${LOG_SERVER_URL}/api/history?limit=${limit}`, { cache: "no-store" });
            const data = await res.json().catch(() => ({ events: [], count: 0 }));
            if (!res.ok)
                return NextResponse.json(data, { status: res.status });
            return NextResponse.json(data);
        }
        return NextResponse.json({ error: "Invalid type: use state or history" }, { status: 400 });
    }
    catch (err) {
        const message = err instanceof Error ? err.message : String(err);
        return NextResponse.json({ error: message || "Agent log server unreachable", events: [], count: 0 }, { status: 502 });
    }
}
export async function POST() {
    try {
        const res = await fetch(`${LOG_SERVER_URL}/api/clear`, {
            method: "POST",
            cache: "no-store",
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok)
            return NextResponse.json(data, { status: res.status });
        return NextResponse.json(data);
    }
    catch (err) {
        const message = err instanceof Error ? err.message : String(err);
        return NextResponse.json({ ok: false, error: message }, { status: 502 });
    }
}
export const dynamic = "force-dynamic";
