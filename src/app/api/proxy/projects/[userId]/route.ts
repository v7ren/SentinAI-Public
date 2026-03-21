import { NextRequest, NextResponse } from "next/server";
const BACKEND_URL = process.env.SENTINEL_API_URL || "https://5001.use-your-own-domain.com";
export async function GET(_request: NextRequest, { params }: {
    params: Promise<{
        userId: string;
    }>;
}) {
    try {
        const { userId } = await params;
        if (!userId) {
            return NextResponse.json({ error: "Missing userId" }, { status: 400 });
        }
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 12000);
        const res = await fetch(`${BACKEND_URL}/api/projects/${userId}`, {
            cache: "no-store",
            signal: controller.signal,
        });
        clearTimeout(timeoutId);
        const data = await res.json().catch(() => []);
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
