"use client";
import { useTheme } from "@/context/ThemeContext";
import { useAuth } from "@/app/hooks/useAuth";
import { useDashboardScan } from "@/context/DashboardScanContext";
import { AlertTriangle, CheckCircle, ChevronDown, ChevronRight, ChevronUp, Clock, FileCode, Search, Shield, ShieldAlert, Upload, X, Zap, Brain, Activity, FolderOpen, } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import React, { useEffect, useRef, useState } from 'react';
interface ScanResult {
    scan_id: string;
    scan_type?: string;
    timestamp: string;
    stats: {
        vulnerabilities: number;
    };
}
interface ProjectHistory {
    id: string;
    name: string;
    created_at: string;
    scans?: ScanResult[];
}
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001";
const TIER_CONFIG: Record<string, {
    label: string;
    description: string;
    icon: React.ReactNode;
    time: string;
}> = {
    '1': { label: 'Fast Scan', description: 'Tier 1 · Fast triage (worker CHEAP_MODEL)', icon: <Zap className="w-4 h-4"/>, time: '~1 min' },
    '2': { label: 'Standard', description: 'Tier 2 · Deeper analysis (worker TIER2_MODEL)', icon: <Search className="w-4 h-4"/>, time: '~3 min' },
    '3': { label: 'Advanced Audit', description: 'Full static + semantic analysis', icon: <ShieldAlert className="w-4 h-4"/>, time: '~8 min' },
    '4': { label: 'Intelligence', description: 'LLM-centric · Maximum coverage', icon: <Brain className="w-4 h-4"/>, time: '~15 min' },
};
const SMART_FILTER = {
    maxFileSizeBytes: 512 * 1024,
    unscannableExt: ['.min.js', '.min.css', '.bundle.js', '.map', '.woff', '.woff2', '.ttf', '.eot', '.otf', '.wasm', '.dll', '.exe', '.so', '.dylib', '.pyc', '.pyo', '.class', '.jar', '.war'],
    configPatterns: [
        /\.env(\.|$)/i,
        /package-lock\.json$/i, /yarn\.lock$/i, /pnpm-lock\.yaml$/i, /Cargo\.lock$/i, /go\.sum$/i,
        /tsconfig\.json$/i, /jsconfig\.json$/i, /\.eslintrc/i, /\.prettierrc/i, /babel\.config/i,
        /\.dockerignore$/i, /\.gitignore$/i, /\.editorconfig$/i, /\.nvmrc$/i, /\.node-version$/i,
        /benchmark\.json$/i, /benchmark\.yaml$/i, /docker-compose\.ya?ml$/i,
    ],
    lowValueConfig: [
        /package\.json$/i, /requirements\.txt$/i, /pyproject\.toml$/i, /go\.mod$/i,
        /README\.md$/i, /CHANGELOG/i, /LICENSE/i, /\.md$/i,
    ],
};
export default function DashboardHub() {
    const { user, isAuthenticated, loading } = useAuth();
    const { theme, isDark } = useTheme();
    const router = useRouter();
    const [showUploadModal, setShowUploadModal] = useState(false);
    const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null);
    const [fileCount, setFileCount] = useState(0);
    const [excludedPaths, setExcludedPaths] = useState<Set<string>>(new Set());
    const [exclusionReasons, setExclusionReasons] = useState<Map<string, string>>(new Map());
    const [showFileList, setShowFileList] = useState(false);
    const [scanTier, setScanTier] = useState("1");
    const { isScanning: isProcessing, scanMinimized, scanProgress, scanStatus, foundVulns, scanActivityLog, startScan, minimizeScan, expandScan, } = useDashboardScan();
    const [projects, setProjects] = useState<ProjectHistory[]>([]);
    const [isLoadingHistory, setIsLoadingHistory] = useState(true);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const getUsernameSlug = () => {
        if (!user)
            return 'user';
        return user.email.split('@')[0];
    };
    useEffect(() => {
        if (isAuthenticated) {
            fetchProjects();
        }
        else if (!loading) {
            setIsLoadingHistory(false);
        }
    }, [isAuthenticated, loading]);
    const fetchProjects = async () => {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 15000);
            const res = await fetch(`${API_BASE}/api/projects`, {
                credentials: "include",
                signal: controller.signal,
            });
            clearTimeout(timeoutId);
            if (res.ok) {
                const data = await res.json();
                const list = Array.isArray(data) ? data : (data?.projects ?? []);
                const normalized = list.map((p: any) => ({
                    ...p,
                    scans: Array.isArray(p?.scans) ? p.scans : [],
                }));
                setProjects(normalized);
            }
            else if (res.status === 401) {
                router.push("/login");
            }
        }
        catch (error) {
            if (error instanceof Error && error.name === "AbortError") {
                console.warn("Projects request timed out");
            }
            else {
                console.error(error);
            }
            setProjects([]);
        }
        finally {
            setIsLoadingHistory(false);
        }
    };
    useEffect(() => {
        if (!loading && !isAuthenticated) {
            router.push("/login");
        }
    }, [loading, isAuthenticated, router]);
    const filterJunkFiles = (fileList: FileList) => {
        const IGNORED = ['node_modules', '.git', 'dist', 'build', '.next', 'vendor', 'bin', 'obj', '.png', '.jpg', '.jpeg', '.svg', '.ico', '.pdf'];
        const dt = new DataTransfer();
        Array.from(fileList).forEach(file => {
            const path = file.webkitRelativePath || file.name;
            const isZip = path.toLowerCase().endsWith('.zip');
            if (isZip || !IGNORED.some(i => path.includes(i) || path.endsWith(i)))
                dt.items.add(file);
        });
        return dt.files;
    };
    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            const cleanFiles = filterJunkFiles(e.target.files);
            if (cleanFiles.length === 0) {
                alert("No valid source code found.");
                return;
            }
            setSelectedFiles(cleanFiles);
            setFileCount(cleanFiles.length);
            setExcludedPaths(new Set());
            setExclusionReasons(new Map());
            setShowUploadModal(true);
            setTimeout(() => applySmartFilter(cleanFiles), 0);
        }
    };
    const applySmartFilter = (files: FileList | null = selectedFiles) => {
        if (!files)
            return;
        const next = new Set<string>();
        const reasons = new Map<string, string>();
        Array.from(files).forEach(file => {
            const path = file.webkitRelativePath || file.name;
            const lower = path.toLowerCase();
            const ext = lower.slice(lower.lastIndexOf('.'));
            let reason: string | null = null;
            if (file.size > SMART_FILTER.maxFileSizeBytes) {
                reason = `Too large (${(file.size / 1024).toFixed(0)}KB)`;
            }
            else if (SMART_FILTER.unscannableExt.some(e => lower.endsWith(e) || lower.includes(e))) {
                reason = "Unscannable (binary/minified)";
            }
            else if (SMART_FILTER.configPatterns.some(p => p.test(path))) {
                reason = "Config/lock file";
            }
            else if (SMART_FILTER.lowValueConfig.some(p => p.test(path))) {
                reason = "Low-value config";
            }
            if (reason) {
                next.add(path);
                reasons.set(path, reason);
            }
        });
        setExcludedPaths(next);
        setExclusionReasons(reasons);
    };
    const clearAllExclusions = () => {
        setExcludedPaths(new Set());
        setExclusionReasons(new Map());
    };
    const toggleFileExcluded = (path: string) => {
        setExcludedPaths(prev => {
            const next = new Set(prev);
            const willBeExcluded = !next.has(path);
            if (willBeExcluded)
                next.add(path);
            else
                next.delete(path);
            setExclusionReasons(r => {
                const m = new Map(r);
                if (willBeExcluded)
                    m.set(path, "Manual");
                else
                    m.delete(path);
                return m;
            });
            return next;
        });
    };
    const applyPresetExclusion = (pattern: string | ((path: string) => boolean), label?: string) => {
        if (!selectedFiles)
            return;
        const matcher = typeof pattern === "function" ? pattern : (p: string) => {
            const lower = p.toLowerCase();
            if (pattern.startsWith("*."))
                return lower.endsWith(pattern.slice(1));
            if (pattern.startsWith("."))
                return lower.includes(pattern) || lower.endsWith(pattern);
            return lower.includes(pattern);
        };
        const toExclude: string[] = [];
        Array.from(selectedFiles).forEach(file => {
            const path = file.webkitRelativePath || file.name;
            if (matcher(path))
                toExclude.push(path);
        });
        setExcludedPaths(prev => new Set([...prev, ...toExclude]));
        setExclusionReasons(prev => {
            const m = new Map(prev);
            toExclude.forEach(p => m.set(p, label ?? "Preset"));
            return m;
        });
    };
    const includedFileCount = selectedFiles ? Array.from(selectedFiles).filter(f => !excludedPaths.has(f.webkitRelativePath || f.name)).length : 0;
    const getCsrfToken = async () => {
        const res = await fetch(`${API_BASE}/api/csrf-token`, { credentials: "include" });
        const data = await res.json();
        return data.csrf_token;
    };
    const handleConfirmScan = async () => {
        if (!selectedFiles || selectedFiles.length === 0)
            return;
        if (includedFileCount === 0) {
            alert("No files selected. Exclude fewer files or add some to include.");
            return;
        }
        if (!isAuthenticated) {
            router.push("/login");
            return;
        }
        const deriveProjectName = (): string => {
            if (!selectedFiles || selectedFiles.length === 0)
                return 'New Scan';
            const first = selectedFiles[0];
            const path = first.webkitRelativePath || first.name;
            if (first.webkitRelativePath) {
                const topDir = first.webkitRelativePath.split('/')[0];
                return topDir || first.name;
            }
            return first.name;
        };
        const buildFormData = (projectName?: string): FormData | null => {
            const filesToSend = selectedFiles
                ? Array.from(selectedFiles).filter(f => !excludedPaths.has(f.webkitRelativePath || f.name))
                : [];
            if (filesToSend.length === 0)
                return null;
            const fd = new FormData();
            fd.append('project_name', projectName ?? deriveProjectName());
            fd.append('scan_type', scanTier);
            fd.append('user_id', user?.email ?? 'anonymous');
            filesToSend.forEach(file => {
                fd.append('files', file, file.webkitRelativePath || file.name);
            });
            return fd;
        };
        const formData = buildFormData();
        if (!formData)
            return;
        setShowUploadModal(false);
        expandScan();
        await startScan({
            formData,
            getUsernameSlug,
            fetchProjects,
        });
    };
    if (loading) {
        return (<div className="h-screen flex items-center justify-center font-sans" style={{ backgroundColor: theme.colors.bg }}>
        <div className="animate-pulse text-sm tracking-widest uppercase" style={{ color: theme.colors.textMuted }}>
          Loading Workspace...
        </div>
      </div>);
    }
    if (!isAuthenticated)
        return null;
    const totalVulns = projects.reduce((acc, p) => acc + (p.scans?.[0]?.stats?.vulnerabilities ?? 0), 0);
    const cleanProjects = projects.filter(p => (p.scans?.[0]?.stats?.vulnerabilities ?? 0) === 0).length;
    return (<div className="flex-1 overflow-y-auto font-sans" style={{ backgroundColor: isDark ? "#050505" : "#F8F9FA" }}>
      <input ref={fileInputRef} type="file" multiple className="hidden" onChange={handleFileChange} webkitdirectory="" directory=""/>

      <div className="max-w-5xl mx-auto px-8 py-10 space-y-10">

        
        <div className="flex items-end justify-between flex-wrap gap-3">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-widest mb-1" style={{ color: theme.colors.textMuted }}>
              Security Platform
            </p>
            <h1 className="text-2xl font-semibold tracking-tight" style={{ color: theme.colors.textMain }}>
              Welcome back, {user?.name || user?.email?.split('@')[0] || 'User'}
            </h1>
          </div>
          <div className="flex items-center gap-2">
          {isProcessing ? (<span className="flex items-center gap-2 px-3 py-1.5 rounded-sm border text-xs font-semibold animate-pulse" style={{
                borderColor: theme.colors.accent,
                backgroundColor: `${theme.colors.accent}18`,
                color: theme.colors.textMain,
            }}>
              <Activity className="w-3.5 h-3.5" style={{ color: theme.colors.accent }}/>
              Scan running
            </span>) : (<span className="flex items-center gap-2 px-3 py-1.5 rounded-sm border text-xs font-medium" style={{
                borderColor: theme.colors.border,
                backgroundColor: theme.colors.surface,
                color: theme.colors.textMuted,
            }}>
              <Activity className="w-3.5 h-3.5" style={{ color: theme.colors.textMuted }}/>
              Nothing processing
            </span>)}
          <Link href="/admin" className="flex items-center gap-2 px-3 py-1.5 border rounded-sm text-xs font-medium transition-colors hover:bg-black/5 dark:hover:bg-white/5" style={{ backgroundColor: theme.colors.surface, borderColor: theme.colors.border, color: theme.colors.textMuted }}>
            <Activity className="w-3.5 h-3.5" style={{ color: theme.colors.accent }}/>
            Worker Admin
          </Link>
          </div>
        </div>

        
        <div className="grid grid-cols-3 gap-4">
          {[
            { label: 'Total Projects', value: projects.length, icon: FolderOpen },
            { label: 'Total Issues Found', value: totalVulns, icon: AlertTriangle, alert: totalVulns > 0 },
            { label: 'Clean Projects', value: cleanProjects, icon: CheckCircle, clean: true },
        ].map(({ label, value, icon: Icon, alert, clean }) => (<div key={label} className="p-5 border rounded-sm" style={{ backgroundColor: theme.colors.surface, borderColor: theme.colors.border }}>
              <p className="text-[11px] font-semibold uppercase tracking-wider mb-2" style={{ color: theme.colors.textMuted }}>
                {label}
              </p>
              <div className="flex items-end justify-between">
                <span className={`text-3xl font-light tracking-tight ${alert ? 'text-red-500' : clean ? 'text-green-500' : ''}`} style={{ color: alert || clean ? undefined : theme.colors.textMain }}>
                  {value}
                </span>
                <Icon className={`w-5 h-5 ${alert ? 'text-red-400' : clean ? 'text-green-400' : ''}`} style={{ color: alert || clean ? undefined : theme.colors.textMuted }}/>
              </div>
            </div>))}
        </div>

        
        <div>
          <button onClick={() => fileInputRef.current?.click()} className="group w-full border rounded-sm flex flex-col items-center justify-center gap-4 transition-all duration-200 hover:shadow-sm relative overflow-hidden" style={{
            backgroundColor: theme.colors.surface,
            borderColor: theme.colors.border,
            height: '200px',
        }}>
            
            <div className="absolute inset-0 opacity-[0.03] pointer-events-none" style={{
            backgroundImage: `linear-gradient(${theme.colors.textMain} 1px, transparent 1px), linear-gradient(90deg, ${theme.colors.textMain} 1px, transparent 1px)`,
            backgroundSize: '40px 40px',
        }}/>
            
            <div className="absolute top-0 left-0 right-0 h-[2px]" style={{ backgroundColor: theme.colors.accent }}/>

            <div className="p-4 border rounded-sm transition-transform duration-200 group-hover:scale-105" style={{ backgroundColor: theme.colors.bg, borderColor: theme.colors.border }}>
              <Upload className="w-6 h-6" style={{ color: theme.colors.accent }}/>
            </div>
            <div className="text-center space-y-1 z-10">
              <p className="text-sm font-semibold" style={{ color: theme.colors.textMain }}>
                Upload Project for Analysis
              </p>
              <p className="text-xs" style={{ color: theme.colors.textMuted }}>
                Node · Python · React · Vue · Go · and more
              </p>
            </div>
            <div className="px-3 py-1 border rounded-sm text-[11px] font-semibold uppercase tracking-widest z-10 transition-colors" style={{ borderColor: theme.colors.border, color: theme.colors.textMuted, backgroundColor: theme.colors.bg }}>
              Select Folder
            </div>
          </button>
        </div>

        
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-[11px] font-semibold uppercase tracking-widest flex items-center gap-2" style={{ color: theme.colors.textMuted }}>
              <Clock className="w-3.5 h-3.5"/>
              Recent Scans
            </h2>
            <span className="text-[11px]" style={{ color: theme.colors.textMuted }}>
              {projects.length} project{projects.length !== 1 ? 's' : ''}
            </span>
          </div>

          {isLoadingHistory ? (<div className="space-y-2">
              {[1, 2, 3].map(i => (<div key={i} className="h-16 border rounded-sm animate-pulse" style={{ backgroundColor: theme.colors.surface, borderColor: theme.colors.border }}/>))}
            </div>) : projects.length === 0 ? (<div className="border rounded-sm p-12 text-center" style={{ borderColor: theme.colors.border, backgroundColor: theme.colors.surface }}>
              <Shield className="w-8 h-8 mx-auto mb-3 opacity-20" style={{ color: theme.colors.textMuted }}/>
              <p className="text-sm" style={{ color: theme.colors.textMuted }}>No scans yet. Upload a project to get started.</p>
            </div>) : (<div className="border rounded-sm overflow-hidden divide-y" style={{ borderColor: theme.colors.border, borderTopColor: theme.colors.border }}>
              {projects.map((project, idx) => {
                const scans = project.scans ?? [];
                const latest = scans[0];
                const vulnCount = latest?.stats?.vulnerabilities ?? 0;
                const scanId = latest?.scan_id;
                const isClean = vulnCount === 0;
                return (<div key={project.id} onClick={() => { if (!scanId)
                    return; router.push(`/dashboard/${getUsernameSlug()}/${scanId}`); }} className={`group flex items-center justify-between px-5 py-4 transition-colors ${scanId ? 'cursor-pointer hover:bg-black/2 dark:hover:bg-white/2' : 'opacity-50 cursor-not-allowed'}`} style={{ backgroundColor: theme.colors.surface }}>
                    
                    <div className="flex items-center gap-4">
                      <span className="text-[11px] font-mono w-5 text-right shrink-0" style={{ color: theme.colors.textMuted }}>
                        {String(idx + 1).padStart(2, '0')}
                      </span>
                      <div className="w-px h-8 shrink-0" style={{ backgroundColor: theme.colors.border }}/>
                      <div>
                        <p className="text-sm font-medium" style={{ color: theme.colors.textMain }}>
                          {project.name}
                        </p>
                        <div className="flex items-center gap-2 mt-0.5">
                          <span className="text-[11px] font-mono" style={{ color: theme.colors.textMuted }}>
                            {new Date(project.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                          </span>
                          {latest?.scan_type && (<>
                              <span className="text-[11px]" style={{ color: theme.colors.textMuted }}>·</span>
                              <span className="text-[11px] font-mono" style={{ color: theme.colors.textMuted }}>
                                Tier {latest.scan_type}
                              </span>
                            </>)}
                        </div>
                      </div>
                    </div>

                    
                    <div className="flex items-center gap-4">
                      {isClean ? (<span className="flex items-center gap-1.5 text-[11px] font-semibold text-green-600 dark:text-green-400">
                          <CheckCircle className="w-3.5 h-3.5"/>
                          Clean
                        </span>) : (<span className="flex items-center gap-1.5 text-[11px] font-semibold text-red-600 dark:text-red-400">
                          <AlertTriangle className="w-3.5 h-3.5"/>
                          {vulnCount} {vulnCount === 1 ? 'Issue' : 'Issues'}
                        </span>)}
                      <ChevronRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity -translate-x-1 group-hover:translate-x-0 duration-150" style={{ color: theme.colors.textMuted }}/>
                    </div>
                  </div>);
            })}
            </div>)}
        </div>
      </div>

      
      {showUploadModal && !isProcessing && (<div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="border rounded-sm w-full max-w-md mx-4 shadow-2xl overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-300" style={{ backgroundColor: theme.colors.bg, borderColor: theme.colors.border }}>
              
              <>
                
                <div className="flex items-center justify-between px-6 py-4 border-b" style={{ borderColor: theme.colors.border }}>
                  <div>
                    <h3 className="text-sm font-semibold" style={{ color: theme.colors.textMain }}>Configure Scan</h3>
                    <p className="text-[11px] mt-0.5" style={{ color: theme.colors.textMuted }}>
                      {includedFileCount} of {fileCount} file{fileCount !== 1 ? 's' : ''} included
                    </p>
                  </div>
                  <button onClick={() => setShowUploadModal(false)} className="p-1.5 rounded-sm hover:bg-black/5 dark:hover:bg-white/5 transition-colors">
                    <X className="w-4 h-4" style={{ color: theme.colors.textMuted }}/>
                  </button>
                </div>

                
                <div className="p-4 space-y-2">
                  <p className="text-[10px] font-semibold uppercase tracking-widest px-1 mb-3" style={{ color: theme.colors.textMuted }}>
                    Analysis Depth
                  </p>
                  {Object.entries(TIER_CONFIG).map(([tier, config]) => {
                const isSelected = scanTier === tier;
                return (<div key={tier} onClick={() => setScanTier(tier)} className="flex items-center gap-4 px-4 py-3 border cursor-pointer transition-all duration-150 relative" style={{
                        backgroundColor: isSelected ? (isDark ? `${theme.colors.accent}10` : `${theme.colors.accent}08`) : theme.colors.surface,
                        borderColor: isSelected ? theme.colors.accent : theme.colors.border,
                    }}>
                        {isSelected && (<div className="absolute left-0 top-0 bottom-0 w-[3px]" style={{ backgroundColor: theme.colors.accent }}/>)}
                        <div className="w-8 h-8 border rounded-sm flex items-center justify-center shrink-0" style={{
                        backgroundColor: isSelected ? theme.colors.accent : theme.colors.bg,
                        borderColor: isSelected ? theme.colors.accent : theme.colors.border,
                        color: isSelected ? '#fff' : theme.colors.textMuted,
                    }}>
                          {config.icon}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-semibold" style={{ color: isSelected ? theme.colors.textMain : theme.colors.textMuted }}>
                              Tier {tier} — {config.label}
                            </span>
                          </div>
                          <p className="text-[11px] mt-0.5" style={{ color: theme.colors.textMuted }}>
                            {config.description}
                          </p>
                        </div>
                        <span className="text-[10px] font-mono shrink-0" style={{ color: theme.colors.textMuted }}>
                          {config.time}
                        </span>
                      </div>);
            })}
                </div>

                
                <div className="px-4 pb-2">
                  <button type="button" onClick={() => setShowFileList(!showFileList)} className="flex items-center justify-between w-full py-2 px-3 border rounded-sm text-left transition-colors hover:bg-black/5 dark:hover:bg-white/5" style={{ borderColor: theme.colors.border, color: theme.colors.textMain }}>
                    <span className="text-[11px] font-semibold uppercase tracking-widest" style={{ color: theme.colors.textMuted }}>
                      Exclude files
                    </span>
                    {showFileList ? <ChevronUp className="w-4 h-4"/> : <ChevronDown className="w-4 h-4"/>}
                  </button>
                  {showFileList && selectedFiles && (<div className="mt-2 space-y-2">
                      <div className="flex flex-wrap gap-1.5 items-center">
                        <button type="button" onClick={() => applySmartFilter()} className="px-2 py-1 text-[10px] font-semibold rounded border transition-colors" style={{ borderColor: theme.colors.accent, color: theme.colors.accent, backgroundColor: `${theme.colors.accent}15` }}>
                          Apply smart filter
                        </button>
                        <button type="button" onClick={clearAllExclusions} className="px-2 py-1 text-[10px] font-mono rounded border transition-colors" style={{ borderColor: theme.colors.border, color: theme.colors.textMuted, backgroundColor: theme.colors.surface }}>
                          Clear exclusions
                        </button>
                        <span className="text-[10px] ml-1" style={{ color: theme.colors.textMuted }}>
                          {exclusionReasons.size > 0 && `${exclusionReasons.size} auto-excluded`}
                        </span>
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {[
                    { label: ".env", pattern: (p: string) => /\.env(\.|$)/i.test(p) },
                    { label: "__pycache__", pattern: (p: string) => p.includes("__pycache__") },
                    { label: "*.lock", pattern: (p: string) => p.toLowerCase().endsWith(".lock") },
                    { label: "*.log", pattern: (p: string) => p.toLowerCase().endsWith(".log") },
                ].map(({ label, pattern }) => (<button key={label} type="button" onClick={() => applyPresetExclusion(pattern, label)} className="px-2 py-1 text-[10px] font-mono rounded border transition-colors" style={{ borderColor: theme.colors.border, color: theme.colors.textMuted, backgroundColor: theme.colors.surface }}>
                            Exclude {label}
                          </button>))}
                      </div>
                      <div className="max-h-32 overflow-y-auto border rounded-sm divide-y" style={{ borderColor: theme.colors.border, backgroundColor: theme.colors.surface }}>
                        {Array.from(selectedFiles).map(file => {
                    const path = file.webkitRelativePath || file.name;
                    const excluded = excludedPaths.has(path);
                    const reason = exclusionReasons.get(path);
                    return (<label key={path} className="flex items-center gap-2 px-3 py-1.5 cursor-pointer hover:bg-black/2 dark:hover:bg-white/2">
                              <input type="checkbox" checked={!excluded} onChange={() => toggleFileExcluded(path)} className="rounded border" style={{ borderColor: theme.colors.border }}/>
                              <span className="text-[11px] font-mono truncate flex-1" style={{ color: excluded ? theme.colors.textMuted : theme.colors.textMain, opacity: excluded ? 0.6 : 1 }}>
                                {path}
                              </span>
                              {excluded && reason && (<span className="text-[9px] font-medium shrink-0 px-1.5 py-0.5 rounded" style={{ backgroundColor: theme.colors.surface, color: theme.colors.textMuted }}>
                                  {reason}
                                </span>)}
                            </label>);
                })}
                      </div>
                    </div>)}
                </div>

                
                <div className="flex gap-3 px-4 pb-4">
                  <button onClick={() => setShowUploadModal(false)} className="flex-1 px-4 py-2.5 border rounded-sm text-sm font-medium transition-colors hover:bg-black/5 dark:hover:bg-white/5" style={{ backgroundColor: theme.colors.surface, borderColor: theme.colors.border, color: theme.colors.textMuted }}>
                    Cancel
                  </button>
                  <button onClick={handleConfirmScan} disabled={includedFileCount === 0} className="flex-1 px-4 py-2.5 rounded-sm text-sm font-semibold transition-all flex items-center justify-center gap-2 hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed" style={{ backgroundColor: theme.colors.accent, color: '#fff' }}>
                    <Zap className="w-4 h-4"/>
                    Start Scan
                  </button>
                </div>
              </>
          </div>
        </div>)}
    </div>);
}
