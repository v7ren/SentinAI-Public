"use client";
import React, { createContext, useCallback, useContext, useEffect, useRef, useState, } from "react";
import { useRouter } from "next/navigation";
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001";
const SCAN_PROXY_BASE = typeof window !== "undefined" ? "" : "";
const ACTIVE_SCAN_STORAGE_KEY = "dashboard_active_scan_id";
type Ctx = {
    isScanning: boolean;
    scanMinimized: boolean;
    scanProgress: number;
    scanStatus: string;
    scanActivityLog: string[];
    foundVulns: number;
    activeScanId: string | null;
    cacheChoicePending: boolean;
    startScan: (args: {
        formData: FormData;
        getUsernameSlug: () => string;
        fetchProjects: () => Promise<void>;
    }) => Promise<void>;
    abortScan: () => void;
    minimizeScan: () => void;
    expandScan: () => void;
    sendCacheChoice: (useCache: boolean) => Promise<void>;
};
const DashboardScanContext = createContext<Ctx | null>(null);
export function DashboardScanProvider({ children }: {
    children: React.ReactNode;
}) {
    const router = useRouter();
    const esRef = useRef<EventSource | null>(null);
    const reconnectAttempted = useRef(false);
    const [isScanning, setIsScanning] = useState(false);
    const [scanMinimized, setScanMinimized] = useState(false);
    const [scanProgress, setScanProgress] = useState(0);
    const [scanStatus, setScanStatus] = useState("");
    const [scanActivityLog, setScanActivityLog] = useState<string[]>([]);
    const [foundVulns, setFoundVulns] = useState(0);
    const [activeScanId, setActiveScanIdState] = useState<string | null>(() => {
        if (typeof window === "undefined")
            return null;
        return sessionStorage.getItem(ACTIVE_SCAN_STORAGE_KEY);
    });
    const [cacheChoicePending, setCacheChoicePending] = useState(false);
    const setActiveScanId = useCallback((id: string | null) => {
        setActiveScanIdState(id);
        if (typeof window !== "undefined") {
            if (id)
                sessionStorage.setItem(ACTIVE_SCAN_STORAGE_KEY, id);
            else
                sessionStorage.removeItem(ACTIVE_SCAN_STORAGE_KEY);
        }
    }, []);
    const cleanupEs = useCallback(() => {
        if (esRef.current) {
            esRef.current.close();
            esRef.current = null;
        }
    }, []);
    const finishScan = useCallback(() => {
        cleanupEs();
        setIsScanning(false);
        setScanMinimized(false);
        setActiveScanId(null);
        setScanProgress(0);
        setScanStatus("");
        setScanActivityLog([]);
        setFoundVulns(0);
        setCacheChoicePending(false);
    }, [cleanupEs, setActiveScanId]);
    const sendCacheChoice = useCallback(async (useCache: boolean) => {
        const scanId = typeof window !== "undefined" ? sessionStorage.getItem(ACTIVE_SCAN_STORAGE_KEY) : null;
        if (!scanId)
            return;
        setCacheChoicePending(false);
        try {
            await fetch("/api/proxy/scan/cache-choice", {
                method: "POST",
                credentials: "include",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ scan_id: scanId, use_cache: useCache }),
            });
        }
        catch {
        }
    }, []);
    const startScan = useCallback(async (args: {
        formData: FormData;
        getUsernameSlug: () => string;
        fetchProjects: () => Promise<void>;
    }) => {
        const { formData, getUsernameSlug, fetchProjects } = args;
        cleanupEs();
        setIsScanning(true);
        setScanMinimized(false);
        setScanProgress(0);
        setFoundVulns(0);
        setScanStatus("Starting scan…");
        setScanActivityLog([]);
        setActiveScanId(null);
        let scanId = "";
        let eventsBase = SCAN_PROXY_BASE;
        const proxyStartUrl = `${SCAN_PROXY_BASE}/api/proxy/scan-start`;
        let res = await fetch(proxyStartUrl, {
            method: "POST",
            credentials: "include",
            body: formData,
        });
        if (res.status === 404) {
            eventsBase = API_BASE;
            res = await fetch(`${API_BASE}/api/scan/start`, {
                method: "POST",
                credentials: "include",
                body: formData,
            });
        }
        if (!res.ok) {
            if (res.status === 401) {
                router.push("/login");
                finishScan();
                return;
            }
            const err = await res.json().catch(() => ({}));
            setScanStatus(err?.error || `Scan failed: ${res.status}`);
            setIsScanning(false);
            return;
        }
        const data = await res.json();
        scanId = data.scan_id;
        if (!scanId) {
            setScanStatus("No scan_id returned");
            setIsScanning(false);
            return;
        }
        setActiveScanId(scanId);
        const eventsUrl = eventsBase
            ? `${eventsBase}/api/scan/events/${encodeURIComponent(scanId)}`
            : `/api/proxy/scan/events?scan_id=${encodeURIComponent(scanId)}`;
        const es = new EventSource(eventsUrl);
        esRef.current = es;
        let resolved = false;
        let connectionLostAt: number | null = null;
        const done = () => {
            if (resolved)
                return;
            resolved = true;
            es.close();
            esRef.current = null;
        };
        const pushLog = (line: string) => {
            setScanActivityLog((prev) => [...prev.slice(-13), line]);
        };
        es.onmessage = (e) => {
            connectionLostAt = null;
            try {
                const event = JSON.parse(e.data);
                if (event.type === "vuln_found") {
                    setFoundVulns((prev) => prev + (event.count || 0));
                    const msg = `Found ${event.count} issue${event.count !== 1 ? "s" : ""} in ${event.filename}`;
                    setScanStatus(msg);
                    pushLog(msg);
                }
                else if (event.type === "file_safe") {
                    setScanStatus(`Scanned ${event.filename}`);
                    pushLog(`✓ ${event.filename}`);
                }
                else if (event.type === "complete") {
                    setScanProgress(100);
                    setScanStatus("Scan complete!");
                    pushLog("Scan complete!");
                    fetchProjects();
                    const sid = event.scan_id || scanId;
                    setTimeout(() => {
                        done();
                        finishScan();
                        router.push(`/dashboard/${getUsernameSlug()}/${sid}`);
                    }, 800);
                }
                else if (event.type === "log") {
                    setScanStatus(event.msg);
                    pushLog(event.msg);
                    const msg = (event.msg || "").toString();
                    if (msg.includes("Indexing project") || msg.includes("scan context"))
                        setScanProgress(2);
                    else if (msg.includes("DeepWiki") || msg.includes("documentation"))
                        setScanProgress(5);
                    else if (msg.includes("Scanning files"))
                        setScanProgress(8);
                }
                else if (event.type === "progress") {
                    if (event.files_scanned != null &&
                        event.total_files != null &&
                        event.total_files > 0) {
                        const pct = Math.min((event.files_scanned / event.total_files) * 100, 95);
                        setScanProgress(pct);
                        const n = event.files_scanned, t = event.total_files;
                        if (n % 5 === 0 || n === t)
                            pushLog(`Files: ${n}/${t}`);
                    }
                }
                else if (event.type === "file_start" && event.filename) {
                    setScanStatus(`Scanning ${event.filename}…`);
                    pushLog(`→ ${event.filename}`);
                }
                else if (event.type === "cache_detected") {
                    setCacheChoicePending(true);
                    setScanStatus(event.msg || "Cached project data found. Choose an option below.");
                    pushLog("Cached data detected — waiting for your choice…");
                }
                else if (event.type === "start" && event.msg) {
                    setScanStatus(event.msg);
                    pushLog(event.msg);
                    if (event.msg && String(event.msg).includes("Compiling report"))
                        setScanProgress(95);
                }
                else if (event.type === "_final" && event.data) {
                    setScanProgress(100);
                    setScanStatus("Scan complete!");
                    pushLog("Scan complete!");
                    fetchProjects();
                    const sid = event.data.scan_id || scanId;
                    setTimeout(() => {
                        done();
                        finishScan();
                        router.push(`/dashboard/${getUsernameSlug()}/${sid}`);
                    }, 800);
                }
                else if (event.type === "_final" && event.error) {
                    setScanStatus(`Error: ${event.error}`);
                    pushLog(`Error: ${event.error}`);
                    done();
                    setIsScanning(false);
                    setActiveScanId(null);
                }
            }
            catch {
            }
        };
        es.onerror = () => {
            if (resolved)
                return;
            if (es.readyState === EventSource.CLOSED) {
                setScanStatus("Connection closed.");
                return;
            }
            const now = Date.now();
            if (connectionLostAt === null) {
                connectionLostAt = now;
                setScanStatus("Connection lost. Reconnecting…");
            }
            else if (now - connectionLostAt > 8000) {
                done();
                setScanStatus("Connection lost. Check Recent Scans for results.");
                setIsScanning(false);
                setActiveScanId(null);
            }
        };
    }, [router, cleanupEs, finishScan, setActiveScanId]);
    useEffect(() => {
        if (typeof window === "undefined")
            return;
        if (reconnectAttempted.current)
            return;
        const stored = sessionStorage.getItem(ACTIVE_SCAN_STORAGE_KEY);
        if (!stored || esRef.current)
            return;
        reconnectAttempted.current = true;
        setIsScanning(true);
        setScanStatus("Reconnecting…");
        setScanProgress(0);
        const eventsUrl = `/api/proxy/scan/events?scan_id=${encodeURIComponent(stored)}`;
        const es = new EventSource(eventsUrl);
        esRef.current = es;
        let resolved = false;
        let connectionLostAt: number | null = null;
        const done = () => {
            if (resolved)
                return;
            resolved = true;
            es.close();
            esRef.current = null;
        };
        const pushLog = (line: string) => {
            setScanActivityLog((prev) => [...prev.slice(-13), line]);
        };
        es.onmessage = (e: MessageEvent) => {
            connectionLostAt = null;
            try {
                const event = JSON.parse(e.data);
                if (event.type === "vuln_found") {
                    setFoundVulns((prev) => prev + (event.count || 0));
                    const msg = `Found ${event.count} issue${event.count !== 1 ? "s" : ""} in ${event.filename}`;
                    setScanStatus(msg);
                    pushLog(msg);
                }
                else if (event.type === "file_safe") {
                    setScanStatus(`Scanned ${event.filename}`);
                    pushLog(`✓ ${event.filename}`);
                }
                else if (event.type === "complete" || (event.type === "_final" && event.data)) {
                    setScanProgress(100);
                    setScanStatus("Scan complete!");
                    pushLog("Scan complete!");
                    setTimeout(() => {
                        done();
                        finishScan();
                        router.push("/dashboard");
                    }, 800);
                }
                else if (event.type === "log") {
                    setScanStatus(event.msg);
                    pushLog(event.msg);
                    const msg = (event.msg || "").toString();
                    if (msg.includes("Indexing project") || msg.includes("scan context"))
                        setScanProgress(2);
                    else if (msg.includes("DeepWiki") || msg.includes("documentation"))
                        setScanProgress(5);
                    else if (msg.includes("Scanning files"))
                        setScanProgress(8);
                }
                else if (event.type === "progress" && event.files_scanned != null && event.total_files != null && event.total_files > 0) {
                    const pct = Math.min((event.files_scanned / event.total_files) * 100, 95);
                    setScanProgress(pct);
                    if (event.files_scanned % 5 === 0 || event.files_scanned === event.total_files) {
                        pushLog(`Files: ${event.files_scanned}/${event.total_files}`);
                    }
                }
                else if (event.type === "file_start" && event.filename) {
                    setScanStatus(`Scanning ${event.filename}…`);
                    pushLog(`→ ${event.filename}`);
                }
                else if (event.type === "cache_detected") {
                    setCacheChoicePending(true);
                    setScanStatus(event.msg || "Cached project data found. Choose an option below.");
                    pushLog("Cached data detected — waiting for your choice…");
                }
                else if (event.type === "_final" && event.error) {
                    setScanStatus(`Error: ${event.error}`);
                    pushLog(`Error: ${event.error}`);
                    done();
                    setIsScanning(false);
                    setActiveScanId(null);
                }
            }
            catch {
            }
        };
        es.onerror = () => {
            if (resolved)
                return;
            if (es.readyState === EventSource.CLOSED)
                return;
            const now = Date.now();
            if (connectionLostAt === null) {
                connectionLostAt = now;
                setScanStatus("Connection lost. Reconnecting…");
            }
            else if (now - connectionLostAt > 8000) {
                done();
                setScanStatus("Connection lost. Check Recent Scans for results.");
                setIsScanning(false);
                setActiveScanId(null);
            }
        };
        return () => {
            if (!resolved) {
                es.close();
                esRef.current = null;
            }
        };
    }, [finishScan, router, setActiveScanId]);
    const abortScan = useCallback(() => {
        cleanupEs();
        setIsScanning(false);
        setScanMinimized(false);
        setActiveScanId(null);
        setScanProgress(0);
        setScanStatus("");
        setScanActivityLog([]);
        setFoundVulns(0);
    }, [cleanupEs, setActiveScanId]);
    const minimizeScan = useCallback(() => setScanMinimized(true), []);
    const expandScan = useCallback(() => setScanMinimized(false), []);
    return (<DashboardScanContext.Provider value={{
            isScanning,
            scanMinimized,
            scanProgress,
            scanStatus,
            scanActivityLog,
            foundVulns,
            activeScanId,
            cacheChoicePending,
            startScan,
            abortScan,
            minimizeScan,
            expandScan,
            sendCacheChoice,
        }}>
      {children}
    </DashboardScanContext.Provider>);
}
export function useDashboardScan() {
    const ctx = useContext(DashboardScanContext);
    if (!ctx)
        throw new Error("useDashboardScan must be used within DashboardScanProvider");
    return ctx;
}
