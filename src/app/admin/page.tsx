"use client";
import { useTheme } from "@/context/ThemeContext";
import Link from "next/link";
import React, { useCallback, useEffect, useRef, useState } from "react";
import { Activity, AlertCircle, CheckCircle, ChevronDown, ChevronLeft, ChevronRight, Loader2, Server, Shield, Terminal, Zap, Code, Wrench, Search, FileText, RotateCcw, Trash2 } from "lucide-react";
interface WorkerActivityItem {
    id: string;
    worker: string | null;
    filename: string;
    scan_id: string;
    scan_type: string;
    started_at: string;
    completed_at: string | null;
    input_size: number;
    input_preview: string;
    status: "running" | "ok" | "error";
    findings_count: number | null;
    scan_status: string | null;
    error: string | null;
}
interface WorkerActivityResponse {
    workers: string[];
    max_parallel_workers: number;
    activity: WorkerActivityItem[];
}
interface AgentLogEvent {
    event_type: string;
    agent_name: string;
    timestamp: string;
    scan_id: string;
    data: Record<string, unknown>;
}
interface AgentBlock {
    name: string;
    type: string;
    phase: string;
    status: "idle" | "running" | "completed" | "error";
    scanId: string;
    events: AgentLogEvent[];
    contextSummary?: Record<string, unknown>;
    config?: Record<string, unknown>;
    prompt?: string;
    promptTokens?: number;
    response?: string;
    responseTokens?: number;
    latencyMs?: number;
    toolCalls: {
        name: string;
        args: unknown;
        result?: string;
    }[];
    findings: unknown[];
    executionTimeMs?: number;
    tokenUsage?: number;
    errors?: string[];
    findingsCount?: number;
    synthesisNote?: string;
    steps?: {
        type: "prompt" | "response" | "tool_call" | "tool_result" | "complete";
        title: string;
        content?: string;
        data?: Record<string, unknown>;
    }[];
}
function formatTime(iso: string | null): string {
    if (!iso)
        return "—";
    try {
        const d = new Date(iso);
        return d.toLocaleTimeString(undefined, { hour12: false }) + " " + d.toLocaleDateString();
    }
    catch {
        return iso;
    }
}
const PIPELINE_AGENTS: {
    id: string;
    label: string;
    phase: string;
    agentType: string;
}[] = [
    { id: "ReconAgent", label: "ReconAgent", phase: "Pre-scan", agentType: "pre-scan" },
    { id: "PatternAgent", label: "PatternAgent", phase: "Pre-scan", agentType: "pre-scan" },
    { id: "ThreatModelAgent", label: "ThreatModelAgent", phase: "Pre-scan", agentType: "pre-scan" },
    { id: "injection_specialist", label: "InjectionSpecialist", phase: "Specialists", agentType: "specialist" },
    { id: "auth_specialist", label: "AuthSpecialist", phase: "Specialists", agentType: "specialist" },
    { id: "crypto_specialist", label: "CryptoSpecialist", phase: "Specialists", agentType: "specialist" },
    { id: "logic_analyst", label: "LogicAnalyst", phase: "Specialists", agentType: "specialist" },
    { id: "config_hunter", label: "ConfigHunter", phase: "Specialists", agentType: "specialist" },
    { id: "llm_security_agent", label: "LLMSecurityAgent", phase: "Specialists (opt.)", agentType: "specialist" },
    { id: "DeduplicationEngine", label: "DeduplicationEngine", phase: "Synthesis", agentType: "synthesis" },
    { id: "ChainCombiner", label: "ChainCombiner", phase: "Synthesis", agentType: "synthesis" },
    { id: "AttackPathSimulator", label: "AttackPathSimulator", phase: "Synthesis", agentType: "synthesis" },
    { id: "ConsensusScorer", label: "ConsensusScorer", phase: "Synthesis", agentType: "synthesis" },
    { id: "SkepticAgent", label: "SkepticAgent", phase: "Validation", agentType: "validation" },
    { id: "RemediationAgent", label: "RemediationAgent", phase: "Output", agentType: "validation" },
    { id: "Tier3Validator", label: "Tier3Validator", phase: "Per-file validation", agentType: "validation" },
    { id: "coordinator", label: "Coordinator", phase: "Pipeline", agentType: "coordinator" },
];
const AGENT_ID_ALIASES: Record<string, string> = {
    Coordinator: "coordinator",
    coordinator: "coordinator",
    remediation_agent: "RemediationAgent",
    RemediationAgent: "RemediationAgent",
    InjectionSpecialist: "injection_specialist",
    AuthSpecialist: "auth_specialist",
    CryptoSpecialist: "crypto_specialist",
    LogicAnalyst: "logic_analyst",
    ConfigHunter: "config_hunter",
    LLMSecurityAgent: "llm_security_agent",
    llm_security_agent: "llm_security_agent",
};
function canonicalAgentId(raw: string, eventType: string): string {
    const s = (raw || "").trim();
    if (AGENT_ID_ALIASES[s])
        return AGENT_ID_ALIASES[s];
    if (s && AGENT_ID_ALIASES[s.toLowerCase()])
        return AGENT_ID_ALIASES[s.toLowerCase()] || s;
    if (!s) {
        switch (eventType) {
            case "deduplication":
                return "DeduplicationEngine";
            case "consensus_scoring":
                return "ConsensusScorer";
            case "skeptic_review":
                return "SkepticAgent";
            case "chain_combiner":
                return "ChainCombiner";
            case "attack_paths":
                return "AttackPathSimulator";
            case "remediation":
                return "RemediationAgent";
            case "phase_transition":
            case "scan_start":
            case "scan_complete":
                return "coordinator";
            default:
                return "_other";
        }
    }
    return s;
}
function buildAgentBlocks(events: AgentLogEvent[]): AgentBlock[] {
    const byAgent = new Map<string, AgentLogEvent[]>();
    for (const e of events) {
        const key = canonicalAgentId(e.agent_name, e.event_type);
        if (key === "_other")
            continue;
        if (!byAgent.has(key))
            byAgent.set(key, []);
        byAgent.get(key)!.push(e);
    }
    const pipelineIds = new Set(PIPELINE_AGENTS.map((p) => p.id));
    const blocks: AgentBlock[] = [];
    const processEvents = (name: string, agentEvents: AgentLogEvent[], phase: string, defaultType: string): AgentBlock => {
        const sorted = [...agentEvents].sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
        let type = defaultType;
        let status: AgentBlock["status"] = "idle";
        let contextSummary: Record<string, unknown> | undefined;
        let config: Record<string, unknown> | undefined;
        let prompt: string | undefined;
        let promptTokens: number | undefined;
        let response: string | undefined;
        let responseTokens: number | undefined;
        let latencyMs: number | undefined;
        const toolCalls: AgentBlock["toolCalls"] = [];
        const findings: unknown[] = [];
        let executionTimeMs: number | undefined;
        let tokenUsage: number | undefined;
        let errors: string[] | undefined;
        let findingsCount: number | undefined;
        let scanId = "";
        let synthesisNote: string | undefined;
        const steps: AgentBlock["steps"] = [];
        for (const e of sorted) {
            if (e.scan_id)
                scanId = e.scan_id;
            const d = e.data || {};
            switch (e.event_type) {
                case "agent_start":
                    type = (d.agent_type as string) || type;
                    status = "running";
                    contextSummary = (d.context_summary as Record<string, unknown>) || contextSummary;
                    config = (d.config as Record<string, unknown>) || config;
                    break;
                case "agent_prompt":
                    prompt = (d.prompt_full as string) || (d.prompt_preview as string);
                    promptTokens = d.prompt_tokens as number;
                    steps.push({
                        type: "prompt",
                        title: "Sent to LLM",
                        content: (d.prompt_full as string) || (d.prompt_preview as string),
                    });
                    break;
                case "agent_response":
                    response = (d.response_full as string) || (d.response_preview as string);
                    responseTokens = d.response_tokens as number;
                    latencyMs = d.latency_ms as number;
                    steps.push({
                        type: "response",
                        title: "LLM output",
                        content: (d.response_full as string) || (d.response_preview as string),
                    });
                    break;
                case "tool_call":
                    toolCalls.push({
                        name: (d.tool_name as string) || "?",
                        args: d.tool_args,
                    });
                    steps.push({
                        type: "tool_call",
                        title: `Tool: ${(d.tool_name as string) || "?"}`,
                        data: { tool_name: d.tool_name, tool_args: d.tool_args },
                    });
                    break;
                case "tool_result": {
                    const last = toolCalls[toolCalls.length - 1];
                    if (last)
                        last.result = (d.result_preview as string) || String(d);
                    steps.push({
                        type: "tool_result",
                        title: `Reply to ${(d.tool_name as string) || "?"}`,
                        content: (d.result_preview as string) || String(d),
                    });
                    break;
                }
                case "agent_findings":
                    findings.push(...((d.all_findings as unknown[]) || (d.findings as unknown[]) || []));
                    break;
                case "agent_complete":
                    status = (d.errors as string[])?.length ? "error" : "completed";
                    executionTimeMs = d.execution_time_ms as number;
                    tokenUsage = d.token_usage as number;
                    errors = d.errors as string[];
                    findingsCount = d.findings_count as number;
                    if (d.verdict_keep !== undefined && d.verdict_confidence !== undefined) {
                        synthesisNote = `Verdict: ${d.verdict_keep ? "keep" : "drop"} · confidence ${d.verdict_confidence} · tools ${d.tool_calls_used ?? 0}${d.validation_mode ? ` (${d.validation_mode})` : ""}`;
                        steps.push({
                            type: "complete",
                            title: "Verdict",
                            data: d as Record<string, unknown>,
                        });
                    }
                    break;
                case "error":
                    status = "error";
                    errors = [...(errors || []), (d.error_message as string) || "Unknown error"];
                    break;
                case "deduplication":
                    status = "completed";
                    synthesisNote = `Dedup: ${d.input_findings ?? "?"} → ${d.output_findings ?? "?"} findings (${d.duplicates_found ?? 0} dupes)`;
                    break;
                case "consensus_scoring":
                    status = "completed";
                    synthesisNote = `Scored ${d.findings_scored ?? 0} findings (consensus)`;
                    break;
                case "skeptic_review":
                    status = "completed";
                    synthesisNote = `Reviewed ${d.findings_reviewed ?? 0} · reject rate ${d.rejection_rate ?? 0}%`;
                    break;
                case "chain_combiner":
                    status = "completed";
                    synthesisNote = `Chains: ${d.chains_created ?? 0} · unchained: ${d.unchained_findings ?? 0}`;
                    break;
                case "attack_paths":
                    status = "completed";
                    synthesisNote = `Paths simulated: ${d.paths_simulated ?? 0}`;
                    break;
                case "remediation":
                    status = "completed";
                    synthesisNote = `Remediations: ${d.remediations_generated ?? 0}`;
                    break;
                case "phase_transition":
                    status = "completed";
                    synthesisNote = `${d.from_phase ?? "?"} → ${d.to_phase ?? "?"}`;
                    break;
                case "scan_start":
                    status = "running";
                    synthesisNote = `Scan start · ${d.file_count ?? 0} files · ${d.language ?? ""} ${d.framework ?? ""}`;
                    break;
                case "scan_complete":
                    status = "completed";
                    synthesisNote = `Done · ${d.total_findings ?? 0} findings · ${d.total_time_ms ?? 0}ms`;
                    break;
                default:
                    break;
            }
        }
        if (name === "Coordinator" && status === "running" && sorted.length > 0) {
            const hasComplete = sorted.some((e) => e.event_type === "scan_complete");
            if (!hasComplete) {
                const last = sorted[sorted.length - 1];
                const ageMs = Date.now() - new Date(last.timestamp).getTime();
                if (ageMs > 90000) {
                    status = "completed";
                    synthesisNote = (synthesisNote || "Scan start") + " · ended (no completion event)";
                }
            }
        }
        return {
            name,
            type,
            phase,
            status,
            scanId,
            events: sorted,
            contextSummary,
            config,
            prompt,
            promptTokens,
            response,
            responseTokens,
            latencyMs,
            toolCalls,
            findings,
            executionTimeMs,
            tokenUsage,
            errors,
            findingsCount,
            synthesisNote,
            steps: steps.length > 0 ? steps : undefined,
        };
    };
    for (const p of PIPELINE_AGENTS) {
        const ev = byAgent.get(p.id) || [];
        const block = processEvents(p.label, ev.length ? ev : [], p.phase, p.agentType);
        if (!ev.length)
            block.status = "idle";
        blocks.push(block);
    }
    for (const [id, ev] of byAgent) {
        if (pipelineIds.has(id) || id === "_other")
            continue;
        const block = processEvents(id, ev, "Other", "agent");
        blocks.push(block);
    }
    const orderIdx = new Map(PIPELINE_AGENTS.map((p, i) => [p.label, i]));
    blocks.sort((a, b) => {
        const ia = orderIdx.get(a.name) ?? 999;
        const ib = orderIdx.get(b.name) ?? 999;
        if (ia !== ib)
            return ia - ib;
        const st = { running: 0, completed: 1, error: 2, idle: 3 };
        return st[a.status] - st[b.status];
    });
    return blocks;
}
function Collapsible({ title, children, defaultOpen = false, theme, maxHeight = "max-h-96", headerClassName = "", bodyClassName = "p-3 text-xs font-mono overflow-x-auto overflow-y-auto whitespace-pre-wrap break-words", }: {
    title: React.ReactNode;
    children: React.ReactNode;
    defaultOpen?: boolean;
    theme: {
        colors: Record<string, string>;
    };
    maxHeight?: string;
    headerClassName?: string;
    bodyClassName?: string;
}) {
    const [open, setOpen] = useState(defaultOpen);
    return (<div className="border rounded-lg overflow-hidden" style={{ borderColor: theme.colors.border }}>
      <button type="button" onClick={() => setOpen(!open)} className={`w-full px-3 py-2 flex items-center justify-between text-left text-sm font-medium transition-colors hover:opacity-80 ${headerClassName}`} style={{ backgroundColor: theme.colors.surface, color: theme.colors.textMain }}>
        <div className="flex items-center gap-2">{title}</div>
        {open ? <ChevronDown className="w-4 h-4 shrink-0"/> : <ChevronRight className="w-4 h-4 shrink-0"/>}
      </button>
      {open && (<div className={`${bodyClassName} ${maxHeight}`} style={{ backgroundColor: theme.colors.bg, color: theme.colors.textMuted }}>
          {children}
        </div>)}
    </div>);
}
function AdminLoginForm({ theme, onSuccess, }: {
    theme: {
        colors: Record<string, string>;
    };
    onSuccess: () => void;
}) {
    const [account, setAccount] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState<string | null>(null);
    const [submitting, setSubmitting] = useState(false);
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setSubmitting(true);
        try {
            const res = await fetch("/api/proxy/auth/admin-login", {
                method: "POST",
                credentials: "include",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ account, password }),
            });
            const data = await res.json().catch(() => ({}));
            if (res.ok) {
                onSuccess();
                return;
            }
            setError((data.error as string) || "Login failed");
        }
        catch {
            setError("Network error");
        }
        finally {
            setSubmitting(false);
        }
    };
    return (<div className="min-h-screen flex items-center justify-center p-6" style={{ backgroundColor: theme.colors.bg, color: theme.colors.textMain }}>
      <div className="w-full max-w-sm rounded-xl border p-6" style={{ borderColor: theme.colors.border, backgroundColor: theme.colors.surface }}>
        <div className="flex items-center gap-3 mb-6">
          <Shield className="w-8 h-8" style={{ color: theme.colors.accent }}/>
          <h1 className="text-xl font-bold">Admin login</h1>
        </div>
        <p className="text-sm mb-4" style={{ color: theme.colors.textMuted }}>
          Use the dedicated admin account (ADMIN_ACCOUNT / ADMIN_PASSWORD in backend .env), or sign in with an email listed in ADMIN_EMAILS and open /admin again.
        </p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1" style={{ color: theme.colors.textMuted }}>
              Account
            </label>
            <input type="text" value={account} onChange={(e) => setAccount(e.target.value)} autoComplete="username" className="w-full px-3 py-2 rounded-lg border focus:outline-none focus:ring-2" style={{
            borderColor: theme.colors.border,
            backgroundColor: theme.colors.bg,
            color: theme.colors.textMain,
        }} required/>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1" style={{ color: theme.colors.textMuted }}>
              Password
            </label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" className="w-full px-3 py-2 rounded-lg border focus:outline-none focus:ring-2" style={{
            borderColor: theme.colors.border,
            backgroundColor: theme.colors.bg,
            color: theme.colors.textMain,
        }} required/>
          </div>
          {error && (<p className="text-sm" style={{ color: theme.colors.accent }}>
              {error}
            </p>)}
          <button type="submit" disabled={submitting} className="w-full py-2 rounded-lg font-medium flex items-center justify-center gap-2 disabled:opacity-50" style={{ backgroundColor: theme.colors.accent, color: theme.colors.bg }}>
            {submitting ? <Loader2 className="w-4 h-4 animate-spin"/> : null}
            Sign in
          </button>
        </form>
        <Link href="/dashboard" className="mt-4 inline-block text-sm hover:underline" style={{ color: theme.colors.textMuted }}>
          ← Back to dashboard
        </Link>
      </div>
    </div>);
}
export default function AdminWorkersPage() {
    const { theme } = useTheme();
    const [adminChecked, setAdminChecked] = useState(false);
    const [isAdmin, setIsAdmin] = useState(false);
    const [workerData, setWorkerData] = useState<WorkerActivityResponse | null>(null);
    const [workerLoading, setWorkerLoading] = useState(true);
    const [workerError, setWorkerError] = useState<string | null>(null);
    const [agentEvents, setAgentEvents] = useState<AgentLogEvent[]>([]);
    const [agentWsConnected, setAgentWsConnected] = useState(false);
    const [agentError, setAgentError] = useState<string | null>(null);
    const [logConfig, setLogConfig] = useState<{
        wsUrl: string;
    } | null>(null);
    const [logServerState, setLogServerState] = useState<{
        current_scan_id: string;
        active_agent: string;
        active_phase: string;
        events_count: number;
    } | null>(null);
    const [agentActivityClearing, setAgentActivityClearing] = useState(false);
    const eventSourceRef = useRef<EventSource | null>(null);
    const wsRef = useRef<WebSocket | null>(null);
    const agentHistoryFromRestRef = useRef(false);
    useEffect(() => {
        let mounted = true;
        fetch("/api/proxy/auth/admin/me", { credentials: "include" })
            .then((res) => {
            if (mounted) {
                setAdminChecked(true);
                setIsAdmin(res.ok);
                fetch("http://127.0.0.1:7566/ingest/343a6e7b-3306-4160-a101-8c37ff48a773", {
                    method: "POST",
                    headers: { "Content-Type": "application/json", "X-Debug-Session-Id": "600d04" },
                    body: JSON.stringify({
                        sessionId: "600d04",
                        location: "admin/page.tsx:admin-check",
                        message: "Admin check result",
                        data: { isAdmin: res.ok, status: res.status },
                        timestamp: Date.now(),
                        hypothesisId: "H4",
                    }),
                }).catch(() => { });
            }
        })
            .catch(() => {
            if (mounted) {
                setAdminChecked(true);
                setIsAdmin(false);
            }
        });
        return () => {
            mounted = false;
        };
    }, []);
    useEffect(() => {
        if (!adminChecked || !isAdmin)
            return;
        const streamUrl = "/api/proxy/admin/worker-activity/stream";
        const es = new EventSource(streamUrl);
        eventSourceRef.current = es;
        es.onopen = () => {
            setWorkerError(null);
            setWorkerLoading(false);
            fetch("http://127.0.0.1:7566/ingest/343a6e7b-3306-4160-a101-8c37ff48a773", {
                method: "POST",
                headers: { "Content-Type": "application/json", "X-Debug-Session-Id": "600d04" },
                body: JSON.stringify({
                    sessionId: "600d04",
                    location: "admin/page.tsx:sse-onopen",
                    message: "Worker activity SSE opened",
                    data: {},
                    timestamp: Date.now(),
                    hypothesisId: "H2",
                }),
            }).catch(() => { });
        };
        es.onmessage = (event) => {
            try {
                const json: WorkerActivityResponse = JSON.parse(event.data);
                setWorkerData(json);
                setWorkerError(null);
            }
            catch {
            }
        };
        es.onerror = () => {
            setWorkerLoading(false);
            es.close();
            eventSourceRef.current = null;
            fetch("http://127.0.0.1:7566/ingest/343a6e7b-3306-4160-a101-8c37ff48a773", {
                method: "POST",
                headers: { "Content-Type": "application/json", "X-Debug-Session-Id": "600d04" },
                body: JSON.stringify({
                    sessionId: "600d04",
                    location: "admin/page.tsx:sse-onerror",
                    message: "Worker activity SSE error",
                    data: { hadWorkerData: !!workerData },
                    timestamp: Date.now(),
                    hypothesisId: "H2",
                }),
            }).catch(() => { });
            if (!workerData) {
                setWorkerError("Live stream failed. Ensure you are logged in as admin.");
                fetch("/api/proxy/admin/worker-activity", { credentials: "include" })
                    .then((res) => (res.ok ? res.json() : null))
                    .then((data: WorkerActivityResponse | null) => {
                    if (data && Array.isArray(data.workers)) {
                        setWorkerData(data);
                        setWorkerError(null);
                    }
                    else {
                        setWorkerData({ workers: [], max_parallel_workers: 0, activity: [] });
                    }
                })
                    .catch(() => {
                    setWorkerData({ workers: [], max_parallel_workers: 0, activity: [] });
                });
            }
        };
        return () => {
            es.close();
            eventSourceRef.current = null;
        };
    }, [adminChecked, isAdmin]);
    const appendAgentEvent = useCallback((event: AgentLogEvent) => {
        setAgentEvents((prev) => [...prev.slice(-999), event]);
    }, []);
    const refreshAgentActivity = useCallback(async () => {
        try {
            const [configRes, historyRes, stateRes] = await Promise.all([
                fetch("/api/proxy/agent-logs/config"),
                fetch("/api/proxy/agent-logs?type=history&limit=500"),
                fetch("/api/proxy/agent-logs?type=state"),
            ]);
            const config = await configRes.json().catch(() => null);
            const history = await historyRes.json().catch(() => ({ events: [] }));
            const state = await stateRes.json().catch(() => null);
            if (config?.wsUrl)
                setLogConfig(config);
            if (Array.isArray(history.events)) {
                setAgentEvents(history.events);
                agentHistoryFromRestRef.current = history.events.length > 0;
            }
            if (state && typeof state.events_count === "number") {
                setLogServerState({
                    current_scan_id: state.current_scan_id || "",
                    active_agent: state.active_agent || "",
                    active_phase: state.active_phase || "",
                    events_count: state.events_count || 0,
                });
            }
            setAgentError(null);
        }
        catch {
            setAgentError("Agent log server unreachable. Start: python -m backend.worker.core.start_log_server (port 5003)");
        }
    }, []);
    useEffect(() => {
        if (!adminChecked || !isAdmin)
            return;
        let mounted = true;
        (async () => {
            try {
                await refreshAgentActivity();
            }
            catch {
                if (mounted)
                    setAgentError("Agent log server unreachable. Is it running on port 5003?");
            }
        })();
        return () => {
            mounted = false;
        };
    }, [adminChecked, isAdmin, refreshAgentActivity]);
    useEffect(() => {
        if (!adminChecked || !isAdmin || !logConfig?.wsUrl)
            return;
        const ws = new WebSocket(logConfig.wsUrl);
        wsRef.current = ws;
        ws.onopen = () => {
            setAgentWsConnected(true);
            setAgentError(null);
        };
        ws.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                if (msg.type === "cleared") {
                    setAgentEvents([]);
                    agentHistoryFromRestRef.current = false;
                    setLogServerState((s) => s ? { ...s, events_count: 0, active_agent: "", active_phase: "", current_scan_id: "" } : null);
                    return;
                }
                if (msg.type === "state" && msg.data) {
                    const d = msg.data;
                    setLogServerState({
                        current_scan_id: d.current_scan_id || "",
                        active_agent: d.active_agent || "",
                        active_phase: d.active_phase || "",
                        events_count: d.events_count ?? 0,
                    });
                    return;
                }
                if (msg.type === "event" && msg.data)
                    appendAgentEvent(msg.data as AgentLogEvent);
                if (msg.type === "history" && msg.data && !agentHistoryFromRestRef.current) {
                    appendAgentEvent(msg.data as AgentLogEvent);
                }
            }
            catch {
            }
        };
        ws.onclose = () => {
            setAgentWsConnected(false);
            wsRef.current = null;
        };
        ws.onerror = () => {
            setAgentError("WebSocket error. Is the log server running on 5003?");
        };
        return () => {
            ws.close();
            wsRef.current = null;
        };
    }, [adminChecked, isAdmin, logConfig?.wsUrl, appendAgentEvent]);
    const clearAgentActivity = useCallback(async () => {
        setAgentActivityClearing(true);
        try {
            await fetch("/api/proxy/agent-logs", { method: "POST" });
            setAgentEvents([]);
            agentHistoryFromRestRef.current = false;
            setLogServerState((s) => s ? { ...s, events_count: 0, active_agent: "", active_phase: "", current_scan_id: "" } : null);
        }
        catch {
            setAgentError("Could not clear log server buffer.");
        }
        finally {
            setAgentActivityClearing(false);
        }
    }, []);
    const agentBlocks = buildAgentBlocks(agentEvents);
    const loading = workerLoading && !workerData;
    if (!adminChecked) {
        return (<div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: theme.colors.bg, color: theme.colors.textMain }}>
        <Loader2 className="w-8 h-8 animate-spin" style={{ color: theme.colors.accent }}/>
      </div>);
    }
    if (!isAdmin) {
        return (<AdminLoginForm theme={theme} onSuccess={() => {
                setIsAdmin(true);
            }}/>);
    }
    if (loading) {
        return (<div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: theme.colors.bg, color: theme.colors.textMain }}>
        <Loader2 className="w-8 h-8 animate-spin" style={{ color: theme.colors.accent }}/>
      </div>);
    }
    return (<div className="min-h-screen p-6 md:p-8" style={{ backgroundColor: theme.colors.bg, color: theme.colors.textMain }}>
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center gap-4 mb-8">
          <Link href="/dashboard" className="flex items-center gap-2 rounded-lg px-3 py-2 transition-colors hover:opacity-80" style={{ color: theme.colors.textMuted, backgroundColor: theme.colors.surface }}>
            <ChevronLeft className="w-4 h-4"/> Back to Dashboard
          </Link>
        </div>

        <div className="flex items-center gap-3 mb-6">
          <Activity className="w-8 h-8" style={{ color: theme.colors.accent }}/>
          <div>
            <h1 className="text-2xl font-bold" style={{ color: theme.colors.textMain }}>
              Admin
            </h1>
            <p className="text-sm" style={{ color: theme.colors.textMuted }}>
              Worker nodes, scan activity, and live agent blocks (what each agent gets, uses, calls).
            </p>
          </div>
        </div>

        {workerError && (<div className="mb-6 p-4 rounded-xl flex items-center gap-2" style={{
                backgroundColor: theme.colors.surface,
                borderLeft: `4px solid ${theme.colors.accent}`,
            }}>
            <AlertCircle className="w-5 h-5 shrink-0"/>
            <span>{workerError}</span>
          </div>)}

        
        {workerData && (<div className="mb-8">
            <h2 className="text-lg font-semibold mb-3 flex items-center gap-2" style={{ color: theme.colors.textMain }}>
              <Server className="w-5 h-5"/> Worker nodes
            </h2>
            <div className="flex flex-wrap gap-3">
              {workerData.workers.map((node) => (<div key={node} className="px-4 py-3 rounded-xl font-mono text-sm flex items-center gap-2" style={{
                    backgroundColor: theme.colors.surface,
                    borderColor: theme.colors.border,
                    borderWidth: 1,
                }}>
                  <CheckCircle className="w-4 h-4 shrink-0" style={{ color: theme.colors.accent }}/>
                  {node}
                </div>))}
            </div>
            <p className="mt-2 text-sm" style={{ color: theme.colors.textMuted }}>
              Max parallel file scans: <strong>{workerData.max_parallel_workers}</strong>
            </p>
          </div>)}

        
        <div className="mb-8">
          <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
            <h2 className="text-lg font-semibold flex items-center gap-2" style={{ color: theme.colors.textMain }}>
              <Zap className="w-5 h-5 shrink-0"/> Agent activity
              {agentWsConnected ? (<span className="flex items-center gap-1 text-xs font-normal" style={{ color: theme.colors.accent }}>
                  <span className="w-2 h-2 rounded-full bg-current animate-pulse"/> Live
                </span>) : (<span className="text-xs font-normal" style={{ color: theme.colors.textMuted }}>
                  (connect log server for live)
                </span>)}
            </h2>
            <div className="flex flex-wrap items-center gap-2">
              <button type="button" onClick={() => void refreshAgentActivity()} className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium border transition-colors hover:opacity-90" style={{ borderColor: theme.colors.border, color: theme.colors.textMain, backgroundColor: theme.colors.surface }}>
                <RotateCcw className="w-4 h-4"/> Refresh
              </button>
              <button type="button" onClick={() => void clearAgentActivity()} disabled={agentActivityClearing} className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium border transition-colors hover:opacity-90 disabled:opacity-50" style={{ borderColor: theme.colors.border, color: theme.colors.textMain, backgroundColor: theme.colors.bg }} title="Clear UI and log server buffer (new scans show fresh activity)">
                {agentActivityClearing ? <Loader2 className="w-4 h-4 animate-spin"/> : <Trash2 className="w-4 h-4"/>}
                Clear recent scan activity
              </button>
            </div>
          </div>

          <p className="text-sm mb-3" style={{ color: theme.colors.textMuted }}>
            Full pipeline (pre-scan → specialists → synthesis → validation). Set{" "}
            <code className="px-1 rounded" style={{ backgroundColor: theme.colors.surface }}>
              LOG_SERVER_URL=http://127.0.0.1:5003
            </code>{" "}
            on the worker and run{" "}
            <code className="px-1 rounded" style={{ backgroundColor: theme.colors.surface }}>
              python -m backend.worker.core.start_log_server
            </code>
            .
          </p>

          {logServerState && (logServerState.active_phase || logServerState.active_agent || logServerState.current_scan_id) && (<div className="mb-3 p-3 rounded-lg text-xs font-mono flex flex-wrap gap-x-4 gap-y-1" style={{ backgroundColor: theme.colors.surface, color: theme.colors.textMuted }}>
              {logServerState.current_scan_id && <span>Scan: {logServerState.current_scan_id.slice(0, 12)}…</span>}
              {logServerState.active_phase && <span>Phase: {logServerState.active_phase}</span>}
              {logServerState.active_agent && <span>Active: {logServerState.active_agent}</span>}
              <span>Buffered events: {logServerState.events_count}</span>
            </div>)}

          {agentError && (<div className="mb-4 p-3 rounded-lg text-sm" style={{ backgroundColor: theme.colors.surface, color: theme.colors.textMuted }}>
              {agentError}
            </div>)}

          <div className="space-y-3">
            {agentBlocks.map((block) => (<Collapsible key={`${block.phase}-${block.name}`} defaultOpen={block.status === "running" || block.status === "error"} theme={theme} maxHeight="max-h-none" bodyClassName="p-0" headerClassName="py-3" title={<div className="flex flex-col sm:flex-row sm:items-center gap-2 w-full">
                      <div className="flex items-center gap-3 flex-wrap">
                        <Terminal className="w-5 h-5 shrink-0" style={{ color: theme.colors.accent }}/>
                        <span className="font-semibold" style={{ color: theme.colors.textMain }}>
                          {block.name}
                        </span>
                        <span className="text-xs px-2 py-0.5 rounded" style={{ color: theme.colors.textMuted, backgroundColor: theme.colors.bg }}>
                          {block.phase}
                        </span>
                        <span className="text-xs px-2 py-0.5 rounded opacity-80" style={{ color: theme.colors.textMuted, backgroundColor: theme.colors.bg }}>
                          {block.type}
                        </span>
                        {block.scanId && (<span className="text-xs font-mono truncate max-w-[120px]" title={block.scanId} style={{ color: theme.colors.textMuted }}>
                            {block.scanId.slice(0, 8)}…
                          </span>)}
                      </div>
                      <div className="flex items-center gap-3 sm:ml-auto text-xs font-normal">
                        {block.status === "running" && (<span className="flex items-center gap-1" style={{ color: theme.colors.accent }}>
                            <Loader2 className="w-4 h-4 animate-spin"/> Running
                          </span>)}
                        {block.status === "completed" && (<span className="flex items-center gap-1" style={{ color: theme.colors.accent }}>
                            <CheckCircle className="w-4 h-4"/> Done
                          </span>)}
                        {block.status === "error" && (<span className="flex items-center gap-1" style={{ color: theme.colors.accent }}>
                            <AlertCircle className="w-4 h-4"/> Error
                          </span>)}
                        {block.status === "idle" && (<span style={{ color: theme.colors.textMuted }}>— No activity yet</span>)}
                        {block.executionTimeMs != null && (<span style={{ color: theme.colors.textMuted }}>
                            {block.executionTimeMs}ms
                          </span>)}
                        {block.tokenUsage != null && (<span style={{ color: theme.colors.textMuted }}>
                            {block.tokenUsage} tokens
                          </span>)}
                        {block.findingsCount != null && (<span style={{ color: theme.colors.textMuted }}>
                            {block.findingsCount} findings
                          </span>)}
                        {block.toolCalls.length > 0 && (<span className="flex items-center gap-1" style={{ color: theme.colors.accent }} title="Tool calls used">
                            <Wrench className="w-3.5 h-3.5"/> {block.toolCalls.length} tools
                          </span>)}
                      </div>
                    </div>}>
                  <div className="p-4 space-y-4 border-t" style={{ borderColor: theme.colors.border }}>
                    {block.synthesisNote && (<p className="text-sm font-mono p-2 rounded" style={{ backgroundColor: theme.colors.surface, color: theme.colors.textMain }}>
                        {block.synthesisNote}
                      </p>)}
                    {block.contextSummary && Object.keys(block.contextSummary).length > 0 && (<Collapsible title={<><FileText className="w-4 h-4"/> Context Summary</>} theme={theme}>
                        {JSON.stringify(block.contextSummary, null, 2)}
                      </Collapsible>)}

                    {block.toolCalls.length > 0 && (<div>
                        <p className="text-sm font-medium mb-2 flex items-center gap-2" style={{ color: theme.colors.textMain }}>
                          <Wrench className="w-4 h-4"/> Tool Calls ({block.toolCalls.length})
                        </p>
                        <div className="space-y-2">
                          {block.toolCalls.map((tc, i) => (<Collapsible key={i} title={<span className="font-mono text-xs" style={{ color: theme.colors.accent }}>
                                  {tc.name}
                                </span>} theme={theme}>
                              <div className="space-y-3">
                                {tc.args != null && Object.keys(tc.args as object).length > 0 && (<div>
                                    <p className="text-xs font-semibold mb-1" style={{ color: theme.colors.textMain }}>Arguments:</p>
                                    <pre className="text-xs p-2 rounded" style={{ backgroundColor: theme.colors.surface }}>
                                      {JSON.stringify(tc.args, null, 2)}
                                    </pre>
                                  </div>)}
                                {tc.result != null && (<div>
                                    <p className="text-xs font-semibold mb-1" style={{ color: theme.colors.textMain }}>Result:</p>
                                    <pre className="text-xs p-2 rounded whitespace-pre-wrap break-words max-h-64 overflow-y-auto" style={{ backgroundColor: theme.colors.surface }}>
                                      {tc.result}
                                    </pre>
                                  </div>)}
                              </div>
                            </Collapsible>))}
                        </div>
                      </div>)}

                    {block.steps && block.steps.length > 0 && (<div className="space-y-3">
                        <p className="text-sm font-medium flex items-center gap-2" style={{ color: theme.colors.textMain }}>
                          <Activity className="w-4 h-4"/> Detailed activity
                        </p>
                        <div className="space-y-2">
                          {block.steps.map((step, i) => (<Collapsible key={i} title={<span className="text-xs font-medium flex items-center gap-2" style={{ color: theme.colors.textMain }}>
                                  <span className="shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs" style={{ backgroundColor: theme.colors.surface, color: theme.colors.accent }}>
                                    {i + 1}
                                  </span>
                                  {step.type === "prompt" && <Code className="w-3.5 h-3.5"/>}
                                  {step.type === "response" && <Terminal className="w-3.5 h-3.5"/>}
                                  {step.type === "tool_call" && <Wrench className="w-3.5 h-3.5"/>}
                                  {step.type === "tool_result" && <FileText className="w-3.5 h-3.5"/>}
                                  {step.type === "complete" && <CheckCircle className="w-3.5 h-3.5"/>}
                                  {step.title}
                                </span>} theme={theme}>
                              {step.content != null && step.content !== "" && (<pre className="text-xs p-3 rounded whitespace-pre-wrap break-words max-h-96 overflow-y-auto" style={{ backgroundColor: theme.colors.surface }}>
                                  {step.content}
                                </pre>)}
                              {step.data != null && Object.keys(step.data).length > 0 && (<pre className="text-xs p-3 rounded whitespace-pre-wrap break-words" style={{ backgroundColor: theme.colors.surface }}>
                                  {step.type === "complete" && step.data.verdict_keep !== undefined && (<span className="block mb-2">
                                      {step.data.verdict_keep ? "Keep" : "Drop"} · confidence {String(step.data.verdict_confidence)} · tools {String(step.data.tool_calls_used ?? 0)}
                                      {step.data.validation_mode != null && ` (${String(step.data.validation_mode)})`}
                                    </span>)}
                                  {JSON.stringify(step.data, null, 2)}
                                </pre>)}
                            </Collapsible>))}
                        </div>
                      </div>)}

                    {block.prompt && (<Collapsible title={<>
                            <Code className="w-4 h-4"/>
                            Prompt {block.promptTokens != null && `(${block.promptTokens} tokens)`}
                          </>} theme={theme}>
                        {block.prompt}
                      </Collapsible>)}

                    {block.response && (<Collapsible title={<>
                            <Terminal className="w-4 h-4"/>
                            Response {block.responseTokens != null && `(${block.responseTokens} tokens)`}
                            {block.latencyMs != null && ` - ${block.latencyMs}ms`}
                          </>} theme={theme}>
                        {block.response}
                      </Collapsible>)}

                    {block.findings.length > 0 && (<div>
                        <p className="text-sm font-medium mb-2 flex items-center gap-2" style={{ color: theme.colors.textMain }}>
                          <Search className="w-4 h-4"/> Findings ({block.findings.length})
                        </p>
                        <div className="space-y-2">
                          {block.findings.map((f: unknown, i: number) => {
                    const o = f as Record<string, unknown>;
                    return (<Collapsible key={i} title={<span className="text-xs">
                                    <strong style={{ color: theme.colors.textMain }}>
                                      {String(o.vulnerability_class ?? o.vulnerabilityClass ?? "Finding")}
                                    </strong>
                                    {o.file_path != null && (<span className="ml-2 font-mono" style={{ color: theme.colors.textMuted }}>{String(o.file_path)}</span>)}
                                  </span>} theme={theme}>
                                <pre className="text-xs p-2 rounded" style={{ backgroundColor: theme.colors.surface }}>
                                  {JSON.stringify(o, null, 2)}
                                </pre>
                              </Collapsible>);
                })}
                        </div>
                      </div>)}

                    {block.errors && block.errors.length > 0 && (<div>
                        <p className="text-sm font-medium mb-2 flex items-center gap-2" style={{ color: theme.colors.accent }}>
                          <AlertCircle className="w-4 h-4"/> Errors
                        </p>
                        <div className="space-y-2">
                          {block.errors.map((err, i) => (<div key={i} className="p-3 rounded-lg text-xs font-mono whitespace-pre-wrap break-words" style={{ backgroundColor: theme.colors.surface, color: theme.colors.accent, border: `1px solid ${theme.colors.accent}` }}>
                              {err}
                            </div>))}
                        </div>
                      </div>)}
                  </div>
                </Collapsible>))}
            </div>
        </div>

        
        {workerData && (<div>
            <h2 className="text-lg font-semibold mb-3 flex items-center gap-2" style={{ color: theme.colors.textMain }}>
              <Shield className="w-5 h-5"/> Recent scan activity
            </h2>
            <div className="rounded-xl overflow-hidden border" style={{ borderColor: theme.colors.border, backgroundColor: theme.colors.surface }}>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr style={{ backgroundColor: theme.colors.bg, color: theme.colors.textMuted }}>
                      <th className="px-4 py-3 font-medium">Worker</th>
                      <th className="px-4 py-3 font-medium">Filename</th>
                      <th className="px-4 py-3 font-medium">Scan ID</th>
                      <th className="px-4 py-3 font-medium">Tier</th>
                      <th className="px-4 py-3 font-medium">Input</th>
                      <th className="px-4 py-3 font-medium">Output</th>
                      <th className="px-4 py-3 font-medium">Started</th>
                      <th className="px-4 py-3 font-medium">Completed</th>
                    </tr>
                  </thead>
                  <tbody>
                    {workerData.activity.length === 0 ? (<tr>
                        <td colSpan={8} className="px-4 py-8 text-center" style={{ color: theme.colors.textMuted }}>
                          No activity yet.
                        </td>
                      </tr>) : (workerData.activity.map((item) => (<tr key={item.id} className="border-t" style={{ borderColor: theme.colors.border }}>
                          <td className="px-4 py-3 font-mono text-xs">
                            {item.worker ?? <span style={{ color: theme.colors.textMuted }}>—</span>}
                          </td>
                          <td className="px-4 py-3 font-medium max-w-[180px] truncate" title={item.filename}>
                            {item.filename}
                          </td>
                          <td className="px-4 py-3 font-mono text-xs max-w-[140px] truncate" title={item.scan_id}>
                            {item.scan_id}
                          </td>
                          <td className="px-4 py-3">Tier {item.scan_type}</td>
                          <td className="px-4 py-3 max-w-[220px]">
                            <span className="text-xs" style={{ color: theme.colors.textMuted }}>
                              {item.input_size} chars
                            </span>
                            {item.input_preview && (<Collapsible title="View Input" theme={theme} maxHeight="max-h-48" headerClassName="py-1 px-2 mt-1 text-xs">
                                {item.input_preview}
                              </Collapsible>)}
                          </td>
                          <td className="px-4 py-3">
                            {item.status === "running" && (<span className="flex items-center gap-1">
                                <Loader2 className="w-3 h-3 animate-spin"/> running
                              </span>)}
                            {item.status === "ok" && (<span className="flex items-center gap-1">
                                <CheckCircle className="w-3 h-3" style={{ color: theme.colors.accent }}/>
                                {item.scan_status} — {item.findings_count ?? 0} findings
                              </span>)}
                            {item.status === "error" && (<span className="flex items-center gap-1" style={{ color: theme.colors.accent }}>
                                <AlertCircle className="w-3 h-3"/>
                                {item.error || "Error"}
                              </span>)}
                          </td>
                          <td className="px-4 py-3 text-xs" style={{ color: theme.colors.textMuted }}>
                            {formatTime(item.started_at)}
                          </td>
                          <td className="px-4 py-3 text-xs" style={{ color: theme.colors.textMuted }}>
                            {formatTime(item.completed_at)}
                          </td>
                        </tr>)))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>)}
      </div>
    </div>);
}
