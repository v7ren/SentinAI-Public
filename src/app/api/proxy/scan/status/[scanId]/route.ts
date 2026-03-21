import { NextRequest, NextResponse } from "next/server";
const BACKEND_URL = process.env.SENTINEL_API_URL || "https://5001.use-your-own-domain.com";
export async function GET(_request: NextRequest, { params }: {
    params: Promise<{
        scanId: string;
    }>;
}) {
    try {
        const { scanId } = await params;
        if (!scanId) {
            return NextResponse.json({ error: "Missing scanId" }, { status: 400 });
        }
        const res = await fetch(`${BACKEND_URL}/api/scan/status/${encodeURIComponent(scanId)}`, {
            cache: "no-store",
        });
        const data = await res.json().catch(() => ({}));
        if (res.status === 404) {
            return NextResponse.json(data, { status: 404 });
        }
        return NextResponse.json(data);
    }
    catch (err) {
        const message = err instanceof Error ? err.message : String(err);
        return NextResponse.json({ error: message || "Proxy request failed" }, { status: 502 });
    }
}
