import { NextResponse } from "next/server";
export async function GET() {
    const wsUrl = process.env.NEXT_PUBLIC_AGENT_LOG_WS_URL ||
        "ws://localhost:5003/ws/logs";
    return NextResponse.json({ wsUrl });
}
export const dynamic = "force-dynamic";
