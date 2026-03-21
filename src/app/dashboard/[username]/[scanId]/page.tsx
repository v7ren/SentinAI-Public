"use client";
import { useTheme } from "@/context/ThemeContext";
import { useAuth } from "@/app/hooks/useAuth";
import { Activity, AlertTriangle, ArrowLeft, BookOpen, Bug, CheckCircle, ChevronRight, Crosshair, ExternalLink, FileCode, LayoutDashboard, List, Menu, Search, Server, Shield, Terminal, X, Zap, } from "lucide-react";
import { useParams, useRouter } from "next/navigation";
import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Cell, Pie, PieChart, Tooltip as RechartsTooltip, ResponsiveContainer, } from "recharts";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { prism, vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { Components } from "react-markdown";
const BACKEND_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001";
const GLOBAL_CSS = `
  .custom-scroll::-webkit-scrollbar { width: 4px; height: 4px; }
  .custom-scroll::-webkit-scrollbar-track { background: transparent; }
  .custom-scroll::-webkit-scrollbar-thumb {
    background: rgba(128,128,128,0.2);
    border-radius: 9999px;
    transition: background 0.2s;
  }
  .custom-scroll::-webkit-scrollbar-thumb:hover { background: rgba(128,128,128,0.45); }
  .custom-scroll { scrollbar-width: thin; scrollbar-color: rgba(128,128,128,0.2) transparent; }
  .dark .custom-scroll::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); }
  .dark .custom-scroll::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.22); }

  .resize-handle {
    width: 4px; cursor: col-resize; flex-shrink: 0;
    position: relative; z-index: 20; transition: background 0.15s;
  }
  .resize-handle:hover, .resize-handle.dragging { background: rgba(99,102,241,0.45) !important; }
  .resize-handle::after {
    content: ''; position: absolute; top: 50%; left: 50%;
    transform: translate(-50%,-50%);
    width: 2px; height: 40px; border-radius: 9999px;
    background: rgba(128,128,128,0.25);
  }

  .drawer-overlay {
    position: fixed; inset: 0; z-index: 40;
    background: rgba(0,0,0,0.45); backdrop-filter: blur(2px);
  }
  .drawer-panel {
    position: fixed; top: 0; left: 0; bottom: 0; z-index: 50;
    width: 88vw; max-width: 340px;
    display: flex; flex-direction: column;
    transform: translateX(-100%);
    transition: transform 0.28s cubic-bezier(0.4,0,0.2,1);
    will-change: transform;
  }
  .drawer-panel.open { transform: translateX(0); }

  .bottom-sheet {
    position: fixed; left: 0; right: 0; bottom: 0; z-index: 50;
    max-height: 88vh; border-radius: 16px 16px 0 0;
    transform: translateY(100%);
    transition: transform 0.3s cubic-bezier(0.4,0,0.2,1);
    will-change: transform; display: flex; flex-direction: column;
  }
  .bottom-sheet.open { transform: translateY(0); }

  .section-divider {
    height: 1px;
    background: linear-gradient(to right, transparent, currentColor 20%, currentColor 80%, transparent);
    opacity: 0.12;
  }
`;
const slugify = (text: string) => text.toString().toLowerCase().trim()
    .replace(/\s+/g, "-").replace(/[^\w\-]+/g, "").replace(/\-\-+/g, "-");
const formatDuration = (seconds?: number) => {
    if (seconds == null)
        return "Unknown";
    const total = Math.floor(seconds);
    if (total < 60)
        return `${total}s`;
    const mins = Math.floor(total / 60);
    const secs = total % 60;
    if (mins < 60)
        return `${mins}m ${secs}s`;
    return `${Math.floor(mins / 60)}h ${mins % 60}m ${secs}s`;
};
const SeverityBadge = ({ severity }: {
    severity: string;
}) => {
    const styles: Record<string, string> = {
        CRITICAL: "bg-red-50 text-red-700 border-red-200 dark:bg-red-950/50 dark:text-red-400 dark:border-red-800",
        HIGH: "bg-orange-50 text-orange-700 border-orange-200 dark:bg-orange-950/50 dark:text-orange-400 dark:border-orange-800",
        MEDIUM: "bg-yellow-50 text-yellow-700 border-yellow-200 dark:bg-yellow-950/50 dark:text-yellow-400 dark:border-yellow-800",
        LOW: "bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950/50 dark:text-blue-400 dark:border-blue-800",
    };
    return (<span className={`px-2.5 py-1 rounded-sm text-[11px] font-semibold border tracking-wider ${styles[severity] || "bg-gray-50 text-gray-700 border-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-700"}`}>
      {severity}
    </span>);
};
const StatCard = ({ title, value, icon: Icon, color }: any) => {
    const { theme } = useTheme();
    return (<div className="p-6 border rounded-sm transition-all duration-200 hover:shadow-md hover:-translate-y-px" style={{ backgroundColor: theme.colors.surface, borderColor: theme.colors.border }}>
      <div className="flex justify-between items-start">
        <div className="space-y-2">
          <p className="text-[11px] font-semibold uppercase tracking-widest" style={{ color: theme.colors.textMuted }}>
            {title}
          </p>
          <h3 className={`text-4xl font-light tracking-tight ${color || ""}`} style={{ color: color ? undefined : theme.colors.textMain }}>
            {value}
          </h3>
        </div>
        <div className="p-2.5 border rounded-sm mt-0.5" style={{ backgroundColor: theme.colors.bg, borderColor: theme.colors.border }}>
          <Icon className="w-4 h-4" style={{ color: theme.colors.textMuted }}/>
        </div>
      </div>
    </div>);
};
const SectionLabel = ({ icon: Icon, children }: {
    icon?: any;
    children: React.ReactNode;
}) => {
    const { theme } = useTheme();
    return (<div className="flex items-center gap-2 mb-4">
      {Icon && <Icon className="w-3.5 h-3.5 shrink-0" style={{ color: theme.colors.textMuted }}/>}
      <span className="text-[11px] font-semibold uppercase tracking-widest" style={{ color: theme.colors.textMuted }}>
        {children}
      </span>
    </div>);
};
const normalizeScan = (scan: any) => {
    if (!scan?.vulnerabilities)
        return scan;
    return {
        ...scan,
        vulnerabilities: scan.vulnerabilities.map((v: any) => ({
            ...v,
            issues: (v.issues || []).map((issue: any) => !issue.poc && issue.poc_script ? { ...issue, poc: issue.poc_script } : issue),
        })),
    };
};
function useResizable(initial: number, min: number, max: number) {
    const [width, setWidth] = useState(initial);
    const dragging = useRef(false);
    const startX = useRef(0);
    const startW = useRef(0);
    const onMouseDown = useCallback((e: React.MouseEvent) => {
        e.preventDefault();
        dragging.current = true;
        startX.current = e.clientX;
        startW.current = width;
        document.body.style.cursor = "col-resize";
        document.body.style.userSelect = "none";
    }, [width]);
    useEffect(() => {
        const onMove = (e: MouseEvent) => {
            if (!dragging.current)
                return;
            setWidth(Math.min(max, Math.max(min, startW.current + (e.clientX - startX.current))));
        };
        const onUp = () => {
            dragging.current = false;
            document.body.style.cursor = "";
            document.body.style.userSelect = "";
        };
        window.addEventListener("mousemove", onMove);
        window.addEventListener("mouseup", onUp);
        return () => {
            window.removeEventListener("mousemove", onMove);
            window.removeEventListener("mouseup", onUp);
        };
    }, [min, max]);
    return { width, onMouseDown };
}
export default function ScanReportPage() {
    const { scanId } = useParams();
    const { isAuthenticated, loading } = useAuth();
    const { theme, isDark } = useTheme();
    const router = useRouter();
    const [scanResult, setScanResult] = useState<any | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [selectedIssue, setSelectedIssue] = useState<any | null>(null);
    const [selectedFileCode, setSelectedFileCode] = useState("");
    const [selectedFileName, setSelectedFileName] = useState("");
    const [expandedFiles, setExpandedFiles] = useState<Set<string>>(new Set());
    const [generatingPoc, setGeneratingPoc] = useState(false);
    const [pocError, setPocError] = useState<string | null>(null);
    const [deepwikiDocs, setDeepwikiDocs] = useState("");
    const [docSections, setDocSections] = useState<string[]>([]);
    const [docsLoading, setDocsLoading] = useState(false);
    const [docsError, setDocsError] = useState<string | null>(null);
    const [showDocs, setShowDocs] = useState(false);
    const [drawerOpen, setDrawerOpen] = useState(false);
    const [sheetOpen, setSheetOpen] = useState(false);
    const { width: sidebarWidth, onMouseDown: onResizeStart } = useResizable(320, 200, 560);
    const scanIdNormalized = useMemo(() => {
        const raw = Array.isArray(scanId) ? scanId[0] : scanId;
        if (!raw)
            return "";
        try {
            return decodeURIComponent(raw);
        }
        catch {
            return String(raw);
        }
    }, [scanId]);
    useEffect(() => {
        const id = "sentinel-global-css";
        if (!document.getElementById(id)) {
            const el = document.createElement("style");
            el.id = id;
            el.textContent = GLOBAL_CSS;
            document.head.appendChild(el);
        }
    }, []);
    useEffect(() => {
        if (!loading && !isAuthenticated)
            router.push("/login");
    }, [loading, isAuthenticated, router]);
    const loadDocs = async (sid: string) => {
        setDocsLoading(true);
        setDocsError(null);
        try {
            const res = await fetch(`${BACKEND_BASE_URL}/api/scan/docs/${sid}`, { credentials: "include" });
            if (res.ok) {
                const text = await res.text();
                setDeepwikiDocs(text);
                setDocSections(text.split("\n")
                    .filter(l => l.startsWith("# "))
                    .map(l => l.replace("# ", "").trim()));
            }
            else if (res.status !== 404) {
                setDocsError(`Docs not available (status ${res.status})`);
            }
        }
        catch {
            setDocsError("Network error while fetching docs.");
        }
        finally {
            setDocsLoading(false);
        }
    };
    const applyFoundScan = (foundScan: any, projectName?: string) => {
        const ns = normalizeScan(foundScan);
        setScanResult({ ...ns, project_name: projectName || ns.project_name });
        if (ns.vulnerabilities) {
            setExpandedFiles(new Set(ns.vulnerabilities.map((v: any) => v.filename)));
        }
        loadDocs(ns.scan_id);
    };
    useEffect(() => {
        if (!isAuthenticated || !scanIdNormalized)
            return;
        const fetchData = async () => {
            try {
                const res = await fetch(`${BACKEND_BASE_URL}/api/projects`, { credentials: "include" });
                if (res.ok) {
                    const projects = await res.json();
                    let found: any = null;
                    let pName = "";
                    for (const p of projects) {
                        const m = p.scans?.find((s: any) => s.scan_id === scanIdNormalized);
                        if (m) {
                            found = m;
                            pName = p.name;
                            break;
                        }
                    }
                    if (!found) {
                        const r2 = await fetch(`${BACKEND_BASE_URL}/api/scan/by-id/${encodeURIComponent(scanIdNormalized)}`, { credentials: "include" });
                        if (r2.ok) {
                            const d = await r2.json();
                            found = d;
                            pName = d.project_name || "";
                        }
                    }
                    if (found)
                        applyFoundScan(found, pName);
                }
                else if (res.status === 401) {
                    router.push("/login");
                }
                else {
                    const r2 = await fetch(`${BACKEND_BASE_URL}/api/scan/by-id/${encodeURIComponent(scanIdNormalized)}`, { credentials: "include" });
                    if (r2.ok) {
                        const d = await r2.json();
                        applyFoundScan(d);
                    }
                }
            }
            catch {
                try {
                    const r2 = await fetch(`${BACKEND_BASE_URL}/api/scan/by-id/${encodeURIComponent(scanIdNormalized)}`, { credentials: "include" });
                    if (r2.ok) {
                        const d = await r2.json();
                        applyFoundScan(d);
                    }
                }
                catch { }
            }
            finally {
                setIsLoading(false);
            }
        };
        fetchData();
    }, [isAuthenticated, scanIdNormalized, router]);
    const stats = useMemo(() => {
        if (!scanResult)
            return null;
        const total = scanResult.stats.vulnerabilities;
        const critical = scanResult.vulnerabilities.reduce((a: number, v: any) => a + v.issues.filter((i: any) => i.severity === "CRITICAL").length, 0);
        const high = scanResult.vulnerabilities.reduce((a: number, v: any) => a + v.issues.filter((i: any) => i.severity === "HIGH").length, 0);
        return {
            total, critical, high,
            chartData: [
                { name: "Critical", value: critical, color: "#ef4444" },
                { name: "High", value: high, color: "#f97316" },
                { name: "Medium", value: total - critical - high, color: "#eab308" },
            ].filter(d => d.value > 0),
        };
    }, [scanResult]);
    const toggleFile = (filename: string) => {
        const s = new Set(expandedFiles);
        s.has(filename) ? s.delete(filename) : s.add(filename);
        setExpandedFiles(s);
    };
    const updateIssuePocInState = (fingerprint: string, poc: any) => {
        setScanResult((prev: any) => prev ? {
            ...prev,
            vulnerabilities: prev.vulnerabilities.map((v: any) => ({
                ...v,
                issues: v.issues.map((i: any) => i.fingerprint === fingerprint ? { ...i, poc } : i),
            })),
        } : prev);
        setSelectedIssue((prev: any) => prev?.fingerprint === fingerprint ? { ...prev, poc } : prev);
    };
    const getCsrfToken = async () => {
        const res = await fetch(`${BACKEND_BASE_URL}/api/csrf-token`, { credentials: "include" });
        return (await res.json()).csrf_token;
    };
    const handleGeneratePoc = async () => {
        if (!scanIdNormalized || !selectedIssue?.fingerprint || !scanResult?.project_name)
            return;
        setGeneratingPoc(true);
        setPocError(null);
        try {
            const csrf = await getCsrfToken();
            const res = await fetch(`${BACKEND_BASE_URL}/api/scan/pocs`, {
                method: "POST",
                headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf },
                credentials: "include",
                body: JSON.stringify({
                    project_name: scanResult.project_name,
                    scan_id: scanIdNormalized,
                    fingerprints: [selectedIssue.fingerprint],
                }),
            });
            const data = await res.json();
            if (!res.ok || data.status !== "OK") {
                setPocError(data.error || data.details || "PoC generation failed");
                return;
            }
            const newPoc = (data.poc_map || {})[selectedIssue.fingerprint];
            if (!newPoc) {
                setPocError("Backend did not return a PoC for this issue.");
                return;
            }
            updateIssuePocInState(selectedIssue.fingerprint, newPoc);
        }
        catch {
            setPocError("Network or server error while generating PoC.");
        }
        finally {
            setGeneratingPoc(false);
        }
    };
    const handleCopyPoc = async () => {
        if (!selectedIssue?.poc?.script)
            return;
        try {
            await navigator.clipboard.writeText(selectedIssue.poc.script);
        }
        catch { }
    };
    const getPocDownloadUrl = () => scanIdNormalized && selectedIssue?.fingerprint
        ? `${BACKEND_BASE_URL}/api/poc/${encodeURIComponent(scanIdNormalized)}/${selectedIssue.fingerprint}`
        : null;
    const scrollToSection = (id: string) => document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
    const selectIssue = (file: any, issue: any) => {
        setSelectedFileCode(file.source_code || "");
        setSelectedFileName(file.filename);
        setSelectedIssue(issue);
        setPocError(null);
        setDrawerOpen(false);
        setSheetOpen(true);
    };
    const mdComponents: Components = {
        h1: ({ node, children, ...props }) => {
            const id = slugify(String(children));
            return (<h1 id={id} className="text-xl font-semibold mt-10 mb-5 pb-3 border-b flex items-center gap-2" style={{ borderColor: theme.colors.border, color: theme.colors.textMain }} {...props}>
          {children}
        </h1>);
        },
        h2: ({ node, ...props }) => (<h2 className="text-lg font-semibold mt-8 mb-3" style={{ color: theme.colors.textMain }} {...props}/>),
        h3: ({ node, ...props }) => (<h3 className="text-sm font-semibold mt-6 mb-2 uppercase tracking-wide" style={{ color: theme.colors.textMuted }} {...props}/>),
        p: ({ node, ...props }) => (<p className="mb-4 text-sm leading-7 opacity-90" style={{ color: theme.colors.textMain }} {...props}/>),
        ul: ({ node, ...props }) => (<ul className="list-disc ml-5 mb-4 text-sm space-y-1.5" style={{ color: theme.colors.textMain }} {...props}/>),
        ol: ({ node, ...props }) => (<ol className="list-decimal ml-5 mb-4 text-sm space-y-1.5" style={{ color: theme.colors.textMain }} {...props}/>),
        li: ({ node, ...props }) => (<li className="text-sm leading-6" style={{ color: theme.colors.textMain }} {...props}/>),
        code: ({ inline, className, children, ...props }: any) => {
            const match = /language-(\w+)/.exec(className || "");
            if (!inline && match) {
                return (<div className="my-4 rounded-sm overflow-hidden border" style={{ borderColor: theme.colors.border }}>
            <SyntaxHighlighter language={match[1]} style={isDark ? vscDarkPlus : prism} customStyle={{ margin: 0, padding: "1.25rem 1.5rem", fontSize: "12px", background: isDark ? "#0a0a0a" : "#f8fafc" }} {...props}>
              {String(children).replace(/\n$/, "")}
            </SyntaxHighlighter>
          </div>);
            }
            return (<code className="px-1.5 py-0.5 rounded-sm text-[11px] font-mono border" style={{ backgroundColor: theme.colors.surface, borderColor: theme.colors.border, color: theme.colors.textMain }} {...props}>
          {children}
        </code>);
        },
        a: ({ node, ...props }) => (<a className="underline decoration-dotted underline-offset-2 hover:text-blue-500 transition-colors" style={{ color: theme.colors.accent }} target="_blank" rel="noopener noreferrer" {...props}/>),
        blockquote: ({ node, ...props }) => (<blockquote className="border-l-2 pl-4 my-4 italic opacity-70 text-sm" style={{ borderColor: theme.colors.accent, color: theme.colors.textMuted }} {...props}/>),
    };
    const FileExplorer = () => (<>
      <div className="p-3 border-b space-y-2" style={{ borderColor: theme.colors.border }}>
        <div className="relative">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5" style={{ color: theme.colors.textMuted }}/>
          <input type="text" placeholder="Search findings..." className="w-full pl-8 pr-3 py-2 text-xs border rounded-sm focus:outline-none focus:ring-1 transition-shadow" style={{ backgroundColor: theme.colors.bg, borderColor: theme.colors.border, color: theme.colors.textMain }}/>
        </div>
        <button onClick={() => { setSelectedIssue(null); setDrawerOpen(false); setSheetOpen(false); }} className={`w-full py-2 px-3 rounded-sm text-xs font-medium flex items-center gap-2 transition-all duration-200 ${!selectedIssue ? "shadow-sm" : "hover:bg-black/5 dark:hover:bg-white/5"}`} style={{
            backgroundColor: !selectedIssue ? theme.colors.bg : "transparent",
            color: !selectedIssue ? theme.colors.accent : theme.colors.textMuted,
            border: `1px solid ${!selectedIssue ? theme.colors.border : "transparent"}`,
        }}>
          <LayoutDashboard className="w-3.5 h-3.5"/>
          Dashboard Overview
        </button>
      </div>

      <div className="flex-1 overflow-y-auto py-2 custom-scroll">
        {scanResult?.vulnerabilities.map((file: any, fIdx: number) => {
            const isExpanded = expandedFiles.has(file.filename);
            return (<div key={fIdx} className="mb-2">
              <button onClick={() => toggleFile(file.filename)} className="w-full flex items-center justify-between px-3 py-2.5 hover:bg-black/5 dark:hover:bg-white/5 transition-colors group">
                <div className="flex items-center gap-2 overflow-hidden">
                  <ChevronRight className={`w-3.5 h-3.5 shrink-0 transition-transform duration-200 ${isExpanded ? "rotate-90" : ""}`} style={{ color: theme.colors.textMuted }}/>
                  <FileCode className="w-3.5 h-3.5 shrink-0 opacity-60 group-hover:opacity-100 transition-opacity" style={{ color: theme.colors.accent }}/>
                  <span className="text-[11px] font-mono truncate" style={{ color: theme.colors.textMain }}>
                    {file.filename}
                  </span>
                </div>
                <span className="ml-2 text-[9px] font-bold px-1.5 py-0.5 rounded-sm bg-black/5 dark:bg-white/10 shrink-0" style={{ color: theme.colors.textMuted }}>
                  {file.issues.length}
                </span>
              </button>

              <div className={`overflow-hidden transition-all duration-300 ${isExpanded ? "max-h-[1000px] opacity-100" : "max-h-0 opacity-0"}`}>
                {file.issues.map((issue: any, iIdx: number) => {
                    const isActive = selectedIssue?.fingerprint === issue.fingerprint;
                    return (<div key={iIdx} onClick={() => selectIssue(file, issue)} className="pl-9 pr-3 py-2.5 cursor-pointer transition-colors relative group" style={{ backgroundColor: isActive ? theme.colors.bg : "transparent" }}>
                      <div className="absolute left-0 top-0 bottom-0 w-[3px] transition-all duration-200" style={{ backgroundColor: isActive ? theme.colors.accent : "transparent" }}/>
                      {isActive && (<>
                          <div className="absolute left-0 top-0 right-0 h-px" style={{ backgroundColor: theme.colors.border }}/>
                          <div className="absolute left-0 bottom-0 right-0 h-px" style={{ backgroundColor: theme.colors.border }}/>
                        </>)}
                      <div className="flex justify-between items-start gap-1.5 mb-1">
                        <span className="font-semibold text-xs leading-snug" style={{ color: theme.colors.textMain }}>
                          {issue.type}
                        </span>
                        <SeverityBadge severity={issue.severity}/>
                      </div>
                      <p className="text-[10px] line-clamp-1 leading-relaxed opacity-60" style={{ color: theme.colors.textMuted }}>
                        {issue.description}
                      </p>
                    </div>);
                })}
              </div>
            </div>);
        })}
      </div>
    </>);
    const OverviewDashboard = () => (<div className="flex-1 overflow-y-auto px-6 py-8 md:px-10 md:py-10 custom-scroll animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="max-w-5xl mx-auto space-y-12">

        
        <div>
          <p className="text-[11px] font-semibold uppercase tracking-widest mb-2" style={{ color: theme.colors.textMuted }}>
            Scan Report
          </p>
          <h2 className="text-2xl font-semibold tracking-tight" style={{ color: theme.colors.textMain }}>
            Execution Summary
          </h2>
        </div>

        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard title="Total Issues" value={stats?.total} icon={Bug}/>
          <StatCard title="Critical" value={stats?.critical} icon={AlertTriangle} color="text-red-600 dark:text-red-500"/>
          <StatCard title="Files Scanned" value={scanResult.stats.files_scanned} icon={FileCode}/>
          <StatCard title="Scan Time" value={formatDuration(scanResult.stats?.elapsed_seconds)} icon={Activity}/>
        </div>

        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

          
          <div className="p-6 border rounded-sm" style={{ backgroundColor: theme.colors.bg, borderColor: theme.colors.border }}>
            <SectionLabel>Risk Distribution</SectionLabel>
            <div className="h-52 relative">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={stats?.chartData} innerRadius={68} outerRadius={84} paddingAngle={3} dataKey="value" stroke="none">
                    {stats?.chartData.map((entry: any, index: number) => (<Cell key={index} fill={entry.color}/>))}
                  </Pie>
                  <RechartsTooltip contentStyle={{
            backgroundColor: theme.colors.surface,
            borderColor: theme.colors.border,
            borderRadius: "4px",
            fontSize: "12px",
        }} itemStyle={{ color: theme.colors.textMain }}/>
                </PieChart>
              </ResponsiveContainer>
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <div className="text-center space-y-0.5">
                  <span className="block text-4xl font-light" style={{ color: theme.colors.textMain }}>
                    {stats?.total}
                  </span>
                  <span className="text-[10px] uppercase tracking-widest" style={{ color: theme.colors.textMuted }}>
                    Issues
                  </span>
                </div>
              </div>
            </div>
            <div className="mt-6 flex flex-wrap gap-4">
              {stats?.chartData.map((d: any) => (<div key={d.name} className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-sm shrink-0" style={{ backgroundColor: d.color }}/>
                  <span className="text-xs" style={{ color: theme.colors.textMuted }}>
                    {d.name}{" "}
                    <span className="font-semibold" style={{ color: theme.colors.textMain }}>{d.value}</span>
                  </span>
                </div>))}
            </div>
          </div>

          
          <div className="p-6 border rounded-sm" style={{ backgroundColor: theme.colors.bg, borderColor: theme.colors.border }}>
            <SectionLabel>Security Context</SectionLabel>
            <div className="space-y-5">
              <div className="flex justify-between items-center pb-5 border-b" style={{ borderColor: theme.colors.border }}>
                <span className="text-sm" style={{ color: theme.colors.textMuted }}>Primary Language</span>
                <span className="font-mono px-2.5 py-1 text-xs rounded-sm border" style={{ backgroundColor: theme.colors.surface, borderColor: theme.colors.border, color: theme.colors.textMain }}>
                  {scanResult.project_analysis?.project_info?.language || "Unknown"}
                </span>
              </div>
              <div className="space-y-4">
                {scanResult.project_analysis?.security_context?.has_authentication && (<div className="flex items-center gap-3">
                    <div className="p-1.5 rounded-sm bg-green-50 dark:bg-green-950/30">
                      <Shield className="w-3.5 h-3.5 text-green-500"/>
                    </div>
                    <span className="text-sm" style={{ color: theme.colors.textMain }}>
                      Authentication Mechanisms Detected
                    </span>
                  </div>)}
                {scanResult.project_analysis?.security_context?.has_database && (<div className="flex items-center gap-3">
                    <div className="p-1.5 rounded-sm bg-blue-50 dark:bg-blue-950/30">
                      <Server className="w-3.5 h-3.5 text-blue-500"/>
                    </div>
                    <span className="text-sm" style={{ color: theme.colors.textMain }}>
                      Database Interactions Detected
                    </span>
                  </div>)}
              </div>
            </div>
          </div>
        </div>

        
        <div>
          <button onClick={() => setShowDocs(p => !p)} className="flex items-center justify-between w-full px-5 py-4 border rounded-sm text-xs font-semibold uppercase tracking-widest transition-colors hover:bg-black/5 dark:hover:bg-white/5" style={{ borderColor: theme.colors.border, backgroundColor: theme.colors.surface, color: theme.colors.textMain }}>
            <span className="flex items-center gap-2.5">
              <BookOpen className="w-4 h-4" style={{ color: theme.colors.accent }}/>
              Project Documentation
            </span>
            <span className="text-[10px]">{showDocs ? "▲ Hide" : "▼ Show"}</span>
          </button>

          {showDocs && (<div className="mt-3 border rounded-sm overflow-hidden flex flex-col md:flex-row h-[500px] md:h-[600px]" style={{ backgroundColor: theme.colors.bg, borderColor: theme.colors.border }}>
              {docsLoading && (<div className="p-10 w-full flex items-center justify-center italic text-sm" style={{ color: theme.colors.textMuted }}>
                  Loading project documentation...
                </div>)}
              {!docsLoading && docsError && (<div className="p-10 w-full flex items-center justify-center text-red-500 text-sm">{docsError}</div>)}
              {!docsLoading && !docsError && deepwikiDocs && (<>
                  <div className="w-full md:w-1/4 border-b md:border-b-0 md:border-r overflow-y-auto p-5 custom-scroll" style={{ borderColor: theme.colors.border, backgroundColor: theme.colors.surface }}>
                    <div className="flex items-center gap-2 mb-5">
                      <List className="w-3.5 h-3.5" style={{ color: theme.colors.textMuted }}/>
                      <span className="text-[10px] font-semibold uppercase tracking-widest" style={{ color: theme.colors.textMuted }}>
                        Contents
                      </span>
                    </div>
                    <ul className="space-y-1">
                      {docSections.map((section, idx) => (<li key={idx}>
                          <button onClick={() => scrollToSection(slugify(section))} className="text-xs text-left w-full py-2 px-2.5 rounded-sm hover:bg-black/5 dark:hover:bg-white/5 transition-colors truncate" style={{ color: theme.colors.textMain }}>
                            {section}
                          </button>
                        </li>))}
                      {docSections.length === 0 && (<li className="text-[10px] italic opacity-50 px-2.5" style={{ color: theme.colors.textMuted }}>
                          No sections found.
                        </li>)}
                    </ul>
                  </div>
                  <div className="w-full md:w-3/4 overflow-y-auto px-8 py-8 scroll-smooth custom-scroll">
                    <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponents}>
                      {deepwikiDocs}
                    </ReactMarkdown>
                  </div>
                </>)}
              {!docsLoading && !docsError && !deepwikiDocs && (<div className="p-10 w-full flex items-center justify-center text-sm" style={{ color: theme.colors.textMuted }}>
                  No DeepWiki documentation available for this project.
                </div>)}
            </div>)}
        </div>
      </div>
    </div>);
    const DetailContent = () => (<div className="flex-1 flex flex-col overflow-hidden">

      
      <div className="px-6 py-6 md:px-10 md:py-8 border-b shrink-0" style={{ backgroundColor: theme.colors.bg, borderColor: theme.colors.border }}>
        <div className="max-w-5xl mx-auto">
          <div className="flex items-center gap-2.5 mb-3">
            <SeverityBadge severity={selectedIssue.severity}/>
            <span className="text-[10px] font-mono border px-2 py-1 rounded-sm" style={{ color: theme.colors.textMuted, borderColor: theme.colors.border }}>
              {selectedIssue.cwe_id || "CWE-UNKNOWN"}
            </span>
          </div>
          <h2 className="text-2xl md:text-3xl font-semibold tracking-tight flex flex-wrap items-baseline gap-3" style={{ color: theme.colors.textMain }}>
            {selectedIssue.type}
            {selectedIssue.subtype && (<span className="text-lg md:text-xl font-normal opacity-40" style={{ color: theme.colors.textMuted }}>
                / {selectedIssue.subtype}
              </span>)}
          </h2>
        </div>
      </div>

      
      <div className="flex-1 overflow-y-auto px-6 py-8 md:px-10 md:py-10 custom-scroll">
        <div className="max-w-5xl mx-auto space-y-10">

          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">

            
            <div className="md:col-span-2 space-y-6">
              <div>
                <SectionLabel icon={Activity}>Vulnerability Description</SectionLabel>
                <p className="text-sm leading-7" style={{ color: theme.colors.textMain }}>
                  {selectedIssue.description}
                </p>
              </div>

              {(selectedIssue.impact_summary || selectedIssue.consequences) && (<div className="border-l-2 border-red-500 pl-5 space-y-4 py-1">
                  {selectedIssue.impact_summary && (<div>
                      <div className="flex items-center gap-1.5 mb-2">
                        <Zap className="w-3 h-3 text-red-500"/>
                        <span className="text-[11px] font-semibold uppercase tracking-widest text-red-700 dark:text-red-400">
                          Impact Analysis
                        </span>
                      </div>
                      <p className="text-sm leading-6 text-red-900 dark:text-red-200">
                        {selectedIssue.impact_summary}
                      </p>
                    </div>)}
                  {selectedIssue.consequences && (<div className="pt-4 border-t border-red-200 dark:border-red-900/30">
                      <span className="block mb-2 text-[11px] font-semibold uppercase tracking-widest text-red-700 dark:text-red-400">
                        Business Consequences
                      </span>
                      <p className="text-sm leading-6 text-red-900 dark:text-red-200">
                        {selectedIssue.consequences}
                      </p>
                    </div>)}
                </div>)}
            </div>

            
            <div className="md:col-span-1 grid grid-cols-3 md:grid-cols-1 gap-3">
              <div className="p-5 border rounded-sm space-y-2" style={{ borderColor: theme.colors.border, backgroundColor: theme.colors.surface }}>
                <span className="text-[10px] font-semibold uppercase tracking-widest block" style={{ color: theme.colors.textMuted }}>
                  CVSS Score
                </span>
                <div className="flex items-end gap-1">
                  <span className="text-3xl font-light" style={{ color: theme.colors.textMain }}>
                    {selectedIssue.cvss_score || "N/A"}
                  </span>
                  <span className="text-xs mb-1 opacity-40" style={{ color: theme.colors.textMuted }}>/10</span>
                </div>
                <div className="w-full h-1 bg-gray-200 dark:bg-gray-800 rounded-none mt-1">
                  <div className="h-full bg-red-500 transition-all duration-500" style={{ width: `${(selectedIssue.cvss_score || 0) * 10}%` }}/>
                </div>
              </div>

              <div className="p-5 border rounded-sm space-y-2" style={{ borderColor: theme.colors.border, backgroundColor: theme.colors.surface }}>
                <span className="text-[10px] font-semibold uppercase tracking-widest block" style={{ color: theme.colors.textMuted }}>
                  Confidence
                </span>
                <div className="text-3xl font-light" style={{ color: theme.colors.accent }}>
                  {selectedIssue.confidence_score != null
            ? `${Math.min(100, Math.round((Number(selectedIssue.confidence_score) / 10) * 100))}%`
            : "—"}
                </div>
              </div>

              <div className="p-5 border rounded-sm space-y-3" style={{ borderColor: theme.colors.border, backgroundColor: theme.colors.surface }}>
                <span className="text-[10px] font-semibold uppercase tracking-widest block" style={{ color: theme.colors.textMuted }}>
                  Fix Complexity
                </span>
                <span className="inline-block px-2.5 py-1 rounded-sm text-xs font-semibold border" style={{ backgroundColor: theme.colors.bg, borderColor: theme.colors.border, color: theme.colors.textMain }}>
                  {selectedIssue.fix_complexity || "UNKNOWN"}
                </span>
              </div>
            </div>
          </div>

          <div className="section-divider" style={{ color: theme.colors.textMuted }}/>

          
          <div className="space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <SectionLabel icon={FileCode}>Vulnerable Source</SectionLabel>
              <div className="flex flex-wrap items-center gap-3 mb-4">
                {selectedIssue.trigger && (<span className="text-[10px] font-mono px-2 py-1 rounded-sm border flex items-center gap-1.5" style={{ backgroundColor: theme.colors.surface, borderColor: theme.colors.border, color: theme.colors.textMain }}>
                    <Crosshair className="w-3 h-3"/> {selectedIssue.trigger}()
                  </span>)}
                <span className="text-[10px] font-mono" style={{ color: theme.colors.textMuted }}>
                  {selectedFileName}{selectedIssue.line ? `:${selectedIssue.line}` : ""}
                </span>
              </div>
            </div>
            {selectedFileCode && (<div className="rounded-sm overflow-hidden border shadow-sm" style={{ borderColor: theme.colors.border }}>
                <SyntaxHighlighter language="javascript" style={isDark ? vscDarkPlus : prism} showLineNumbers wrapLines customStyle={{ margin: 0, padding: "1.5rem 2rem", fontSize: "13px", background: isDark ? "#0a0a0a" : "#f8fafc" }} lineProps={(lineNumber: number) => {
                const style: React.CSSProperties = { display: "block" };
                if (lineNumber === selectedIssue.line) {
                    style.backgroundColor = isDark ? "rgba(239,68,68,0.15)" : "rgba(239,68,68,0.05)";
                    style.borderLeft = "3px solid #ef4444";
                    style.paddingLeft = "calc(2rem - 3px)";
                }
                return { style };
            }}>
                  {selectedFileCode}
                </SyntaxHighlighter>
              </div>)}
          </div>

          <div className="section-divider" style={{ color: theme.colors.textMuted }}/>

          
          <div className="space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <SectionLabel icon={Terminal}>Proof of Concept</SectionLabel>
              <div className="flex gap-2 items-center flex-wrap mb-4">
                <button onClick={handleGeneratePoc} disabled={generatingPoc} className="px-3 py-1.5 text-xs rounded-sm border flex items-center gap-1.5 disabled:opacity-60 transition-colors hover:bg-black/5 dark:hover:bg-white/5" style={{
            backgroundColor: theme.colors.surface,
            borderColor: theme.colors.border,
            color: theme.colors.textMain,
            cursor: generatingPoc ? "wait" : "pointer",
        }}>
                  {generatingPoc ? (<><span className="w-3 h-3 rounded-full border-2 border-t-transparent animate-spin"/> Generating...</>) : (<><Terminal className="w-3 h-3"/> Generate Script</>)}
                </button>
                {selectedIssue.poc?.script && (<>
                    <button onClick={handleCopyPoc} className="px-3 py-1.5 text-xs rounded-sm border transition-colors hover:bg-black/5 dark:hover:bg-white/5" style={{ backgroundColor: theme.colors.surface, borderColor: theme.colors.border, color: theme.colors.textMain }}>
                      Copy
                    </button>
                    {getPocDownloadUrl() && (<a href={getPocDownloadUrl()!} target="_blank" rel="noopener noreferrer" className="px-3 py-1.5 text-xs rounded-sm border transition-colors hover:bg-black/5 dark:hover:bg-white/5" style={{ backgroundColor: theme.colors.surface, borderColor: theme.colors.border, color: theme.colors.textMain }}>
                        Download
                      </a>)}
                  </>)}
              </div>
            </div>

            {pocError && <p className="text-xs text-red-500 mb-2">{pocError}</p>}

            <div className="rounded-sm border p-6 space-y-6" style={{ backgroundColor: isDark ? "#0a0a0a" : "#f8fafc", borderColor: theme.colors.border }}>
              {selectedIssue.poc?.instructions && (<div>
                  <span className="block mb-2.5 uppercase text-[10px] font-semibold tracking-widest" style={{ color: theme.colors.textMuted }}>
                    Instructions
                  </span>
                  <p className="whitespace-pre-line text-sm leading-7" style={{ color: theme.colors.textMain }}>
                    {selectedIssue.poc.instructions}
                  </p>
                </div>)}
              {selectedIssue.poc?.script && (<div>
                  <span className="block mb-2.5 uppercase text-[10px] font-semibold tracking-widest" style={{ color: theme.colors.textMuted }}>
                    PoC Script ({selectedIssue.poc.language || "code"})
                  </span>
                  <div className="rounded-sm overflow-hidden border" style={{ borderColor: theme.colors.border }}>
                    <SyntaxHighlighter language={selectedIssue.poc.language === "python" ? "python" : "bash"} style={isDark ? vscDarkPlus : prism} customStyle={{ margin: 0, padding: "1.25rem 1.5rem", fontSize: "12px", background: isDark ? "#050505" : "#ffffff" }}>
                      {selectedIssue.poc.script}
                    </SyntaxHighlighter>
                  </div>
                </div>)}
              {selectedIssue.poc?.expected_outcome && (<div>
                  <span className="block mb-2.5 uppercase text-[10px] font-semibold tracking-widest" style={{ color: theme.colors.textMuted }}>
                    Expected Outcome
                  </span>
                  <p className="whitespace-pre-line text-sm leading-7" style={{ color: theme.colors.textMain }}>
                    {selectedIssue.poc.expected_outcome}
                  </p>
                </div>)}
              {!selectedIssue.poc?.script && !selectedIssue.poc?.instructions && !generatingPoc && !pocError && (<p className="text-sm italic leading-6" style={{ color: theme.colors.textMuted }}>
                  No exploitation script generated yet. Click{" "}
                  <span className="font-semibold not-italic">Generate Script</span>{" "}
                  to have Sentinel craft a PoC.
                </p>)}
            </div>
          </div>

          {selectedIssue.remediation?.length > 0 && (<div className="section-divider" style={{ color: theme.colors.textMuted }}/>)}

          
          {selectedIssue.remediation?.length > 0 && (<div className="space-y-4">
              <SectionLabel icon={CheckCircle}>Recommended Fix</SectionLabel>
              <div className="border border-green-200 dark:border-green-900/50 bg-green-50 dark:bg-green-950/20 p-6 rounded-sm">
                <ul className="space-y-4">
                  {selectedIssue.remediation.map((step: string, idx: number) => (<li key={idx} className="flex items-start gap-4 text-green-900 dark:text-green-200">
                      <span className="mt-2 w-1.5 h-1.5 rounded-none bg-green-500 shrink-0"/>
                      <span className="text-sm leading-7">{step}</span>
                    </li>))}
                </ul>
              </div>
            </div>)}

          
          {selectedIssue.references?.length > 0 && (<div className="space-y-4">
              <SectionLabel icon={ExternalLink}>References</SectionLabel>
              <ul className="space-y-2.5">
                {selectedIssue.references.map((ref: string, idx: number) => (<li key={idx}>
                    <a href={ref} target="_blank" rel="noopener noreferrer" className="text-sm hover:underline truncate block transition-colors" style={{ color: theme.colors.accent }}>
                      {ref}
                    </a>
                  </li>))}
              </ul>
            </div>)}

          <div className="h-8"/>
        </div>
      </div>
    </div>);
    if (isLoading || loading)
        return (<div className="h-screen flex items-center justify-center animate-pulse" style={{ color: theme.colors.textMuted, backgroundColor: theme.colors.bg }}>
      Loading Analysis...
    </div>);
    if (!scanResult)
        return (<div className="h-screen flex items-center justify-center" style={{ color: theme.colors.textMuted, backgroundColor: theme.colors.bg }}>
      Scan not found.
    </div>);
    return (<div className="flex flex-col h-screen overflow-hidden font-sans" style={{ backgroundColor: theme.colors.bg }}>

      
      <header className="border-b shrink-0 h-16 flex items-center justify-between px-4 md:px-6 z-10" style={{ backgroundColor: theme.colors.bg, borderColor: theme.colors.border }}>
        <div className="flex items-center gap-3">
          <button onClick={() => setDrawerOpen(true)} className="md:hidden p-2 rounded-sm hover:bg-black/5 dark:hover:bg-white/5 transition-colors">
            <Menu className="w-4 h-4" style={{ color: theme.colors.textMuted }}/>
          </button>
          <button onClick={() => router.push("/dashboard")} className="p-2 rounded-sm hover:bg-black/5 dark:hover:bg-white/5 transition-colors">
            <ArrowLeft className="w-4 h-4" style={{ color: theme.colors.textMuted }}/>
          </button>
          <div className="flex items-center gap-3">
            <div className="p-2 border rounded-sm" style={{ backgroundColor: theme.colors.surface, borderColor: theme.colors.border }}>
              <Shield className="w-4 h-4" style={{ color: theme.colors.accent }}/>
            </div>
            <div className="flex flex-col md:flex-row md:items-baseline md:gap-3">
              <h1 className="font-semibold text-sm" style={{ color: theme.colors.textMain }}>
                {scanResult.project_name}
              </h1>
              <div className="hidden md:flex items-center gap-2 text-[11px] font-mono" style={{ color: theme.colors.textMuted }}>
                <span>{scanResult.scan_id}</span>
                <span className="opacity-40">/</span>
                <span style={{ color: theme.colors.accent }}>Tier {scanResult.scan_type}</span>
                {typeof scanResult.stats?.elapsed_seconds === "number" && (<>
                    <span className="opacity-40">/</span>
                    <span>Duration: {formatDuration(scanResult.stats.elapsed_seconds)}</span>
                  </>)}
              </div>
            </div>
          </div>
        </div>
      </header>
    
    <div className="flex-1 flex overflow-hidden relative">

  
  <div className="hidden md:flex flex-col border-r z-10 shrink-0" style={{ width: sidebarWidth, borderColor: theme.colors.border, backgroundColor: theme.colors.surface }}>
    <FileExplorer />
  </div>

  
  <div className="hidden md:block resize-handle" style={{ backgroundColor: theme.colors.border }} onMouseDown={onResizeStart}/>

  
  {drawerOpen && (<div className="md:hidden">
      <div className="drawer-overlay" onClick={() => setDrawerOpen(false)}/>
      <div className="drawer-panel open flex flex-col" style={{ backgroundColor: theme.colors.surface, borderRight: `1px solid ${theme.colors.border}` }}>
        <div className="flex items-center justify-between px-4 py-3 border-b shrink-0" style={{ borderColor: theme.colors.border }}>
          <span className="text-xs font-semibold uppercase tracking-widest" style={{ color: theme.colors.textMuted }}>
            Findings
          </span>
          <button onClick={() => setDrawerOpen(false)} className="p-1.5 rounded-sm hover:bg-black/5 dark:hover:bg-white/5 transition-colors">
            <X className="w-4 h-4" style={{ color: theme.colors.textMuted }}/>
          </button>
        </div>
        <FileExplorer />
      </div>
    </div>)}

  
  <div className="flex-1 flex flex-col overflow-hidden" style={{ backgroundColor: isDark ? "#050505" : "#F8F9FA" }}>
    
    <div className="hidden md:flex flex-1 flex-col overflow-hidden">
      {!selectedIssue ? (<OverviewDashboard />) : (<div className="flex-1 flex flex-col overflow-hidden animate-in fade-in slide-in-from-right-4 duration-300">
          <DetailContent />
        </div>)}
    </div>

    
    <div className="flex md:hidden flex-1 flex-col overflow-hidden">
      <OverviewDashboard />
    </div>
  </div>
    </div>

    
    <div className="md:hidden">
  {sheetOpen && (<div className="drawer-overlay" onClick={() => setSheetOpen(false)}/>)}
  <div className={`bottom-sheet ${sheetOpen ? "open" : ""} flex flex-col`} style={{ backgroundColor: theme.colors.bg, borderTop: `1px solid ${theme.colors.border}` }}>
    
    <div className="flex justify-center pt-3 pb-1 shrink-0">
      <div className="w-10 h-1 rounded-full" style={{ backgroundColor: theme.colors.border }}/>
    </div>
    
    <div className="flex items-center justify-between px-5 py-3 shrink-0 border-b" style={{ borderColor: theme.colors.border }}>
      <span className="text-xs font-semibold uppercase tracking-widest" style={{ color: theme.colors.textMuted }}>
        Issue Detail
      </span>
      <button onClick={() => setSheetOpen(false)} className="p-1.5 rounded-sm hover:bg-black/5 dark:hover:bg-white/5 transition-colors">
        <X className="w-4 h-4" style={{ color: theme.colors.textMuted }}/>
      </button>
    </div>
    
    {selectedIssue && (<div className="flex-1 overflow-hidden flex flex-col">
        <DetailContent />
      </div>)}
  </div>
    </div>

    </div>);
}
