"use client";
import { useTheme } from "@/context/ThemeContext";
import { DashboardScanProvider, useDashboardScan } from "@/context/DashboardScanContext";
import { useAuth } from "@/app/hooks/useAuth";
import { Activity, AlertTriangle, Layout, Loader2, LogOut, Maximize2, Minimize2, Settings, Shield, Square, User } from 'lucide-react';
import { usePathname, useRouter } from 'next/navigation';
import React, { useEffect, useRef, useState } from 'react';
function DashboardScanChrome({ children }: {
    children: React.ReactNode;
}) {
    const { theme } = useTheme();
    const { user, isAuthenticated, loading, logout } = useAuth();
    const router = useRouter();
    const pathname = usePathname();
    const { isScanning, scanMinimized, scanProgress, scanStatus, scanActivityLog, foundVulns, activeScanId, cacheChoicePending, expandScan, minimizeScan, abortScan, sendCacheChoice, } = useDashboardScan();
    const [panelOpen, setPanelOpen] = useState(false);
    const sidebarScanRef = useRef<HTMLDivElement>(null);
    const flyoutRef = useRef<HTMLDivElement>(null);
    useEffect(() => {
        if (!isScanning)
            setPanelOpen(false);
    }, [isScanning]);
    useEffect(() => {
        if (!panelOpen)
            return;
        const handleClickOutside = (e: MouseEvent | TouchEvent) => {
            const target = e.target as Node;
            if (sidebarScanRef.current?.contains(target) || flyoutRef.current?.contains(target))
                return;
            setPanelOpen(false);
            if (isScanning)
                minimizeScan();
        };
        document.addEventListener('mousedown', handleClickOutside);
        document.addEventListener('touchstart', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
            document.removeEventListener('touchstart', handleClickOutside);
        };
    }, [panelOpen, isScanning, minimizeScan]);
    const isDetailPage = pathname.split('/').length > 3;
    const isSettingsPage = pathname.includes('/settings');
    useEffect(() => {
        if (!loading && !isAuthenticated) {
            router.push(`/login?redirect=${encodeURIComponent(pathname)}`);
        }
    }, [loading, isAuthenticated, router, pathname]);
    const handleLogout = async () => {
        await logout();
        router.push('/');
    };
    if (loading) {
        return (<div className="min-h-screen w-full flex items-center justify-center font-sans" style={{ backgroundColor: theme.colors.bg }}>
        <div className="animate-pulse text-sm tracking-widest uppercase" style={{ color: theme.colors.textMuted }}>
          Loading Workspace...
        </div>
      </div>);
    }
    if (!isAuthenticated) {
        return null;
    }
    return (<div className="min-h-screen w-full flex font-sans transition-colors duration-300" style={{ backgroundColor: theme.colors.bg, color: theme.colors.textMain }}>
      
      <aside className="w-[260px] shrink-0 border-r hidden md:flex flex-col z-20" style={{
            backgroundColor: theme.colors.surface,
            borderColor: theme.colors.border
        }}>
        
        <div className="h-14 px-6 flex items-center gap-3 border-b shrink-0" style={{ borderColor: theme.colors.border, backgroundColor: theme.colors.bg }}>
          <img src="/logo.svg" alt="" className="w-5 h-5 rounded-sm object-contain shrink-0" aria-hidden/>
          <span className="font-semibold text-sm tracking-widest" style={{ color: theme.colors.textMain }}>
            SENTINAI
          </span>
        </div>
        
        
        <div className="p-3 space-y-1 flex-1 overflow-y-auto">
          <button onClick={() => router.push('/dashboard')} className="w-full px-3 py-2 text-sm flex items-center gap-3 transition-colors relative group" style={{
            backgroundColor: !isDetailPage && !isSettingsPage ? theme.colors.bg : 'transparent',
            color: !isDetailPage && !isSettingsPage ? theme.colors.textMain : theme.colors.textMuted,
        }}>
            
            {!isDetailPage && !isSettingsPage && (<>
                <div className="absolute left-0 top-0 bottom-0 w-1" style={{ backgroundColor: theme.colors.accent }}/>
                <div className="absolute left-0 top-0 right-0 h-[1px]" style={{ backgroundColor: theme.colors.border }}/>
                <div className="absolute left-0 bottom-0 right-0 h-[1px]" style={{ backgroundColor: theme.colors.border }}/>
              </>)}
            
            <Layout className="w-4 h-4 transition-colors" style={{ color: !isDetailPage && !isSettingsPage ? theme.colors.accent : theme.colors.textMuted }}/>
            <span className="font-medium">Dashboard</span>
          </button>

          <button onClick={() => router.push('/dashboard/settings')} className="w-full px-3 py-2 text-sm flex items-center gap-3 transition-colors relative group" style={{
            backgroundColor: isSettingsPage ? theme.colors.bg : 'transparent',
            color: isSettingsPage ? theme.colors.textMain : theme.colors.textMuted,
        }}>
            {isSettingsPage && (<>
                <div className="absolute left-0 top-0 bottom-0 w-1" style={{ backgroundColor: theme.colors.accent }}/>
                <div className="absolute left-0 top-0 right-0 h-[1px]" style={{ backgroundColor: theme.colors.border }}/>
                <div className="absolute left-0 bottom-0 right-0 h-[1px]" style={{ backgroundColor: theme.colors.border }}/>
              </>)}
            
            <Settings className="w-4 h-4 transition-colors" style={{ color: isSettingsPage ? theme.colors.accent : theme.colors.textMuted }}/>
            <span className="font-medium">Settings</span>
          </button>

          
          <div ref={sidebarScanRef} className="mt-2 mx-1 p-3 rounded-sm border" style={{
            backgroundColor: isScanning ? `${theme.colors.accent}12` : theme.colors.bg,
            borderColor: isScanning ? theme.colors.accent : theme.colors.border,
        }}>
            <div className="flex items-center gap-2 mb-2">
              {isScanning ? (<>
                  <Loader2 className="w-4 h-4 animate-spin shrink-0" style={{ color: theme.colors.accent }}/>
                  <span className="text-xs font-semibold" style={{ color: theme.colors.textMain }}>
                    Scan in progress
                  </span>
                </>) : (<>
                  <Activity className="w-4 h-4 shrink-0" style={{ color: theme.colors.textMuted }}/>
                  <span className="text-xs font-semibold" style={{ color: theme.colors.textMain }}>
                    Currently doing
                  </span>
                </>)}
            </div>
            {isScanning ? (<>
                <div className="h-1 rounded-full overflow-hidden mb-2" style={{ backgroundColor: theme.colors.surface }}>
                  <div className="h-full transition-all duration-300 rounded-full" style={{
                width: `${Math.max(1, scanProgress)}%`,
                backgroundColor: foundVulns > 0 ? "#ef4444" : theme.colors.accent,
            }}/>
                </div>
                <p className="text-[10px] font-mono truncate mb-2" style={{ color: theme.colors.textMuted }} title={scanStatus}>
                  {scanStatus || "…"}
                </p>
                <button type="button" onClick={() => {
                if (panelOpen) {
                    setPanelOpen(false);
                    if (isScanning)
                        minimizeScan();
                }
                else {
                    setPanelOpen(true);
                    if (isScanning)
                        expandScan();
                    router.push("/dashboard");
                }
            }} className="w-full flex items-center justify-center gap-1.5 py-1.5 text-[11px] font-semibold rounded-sm border transition-colors hover:opacity-90" style={{
                borderColor: theme.colors.border,
                backgroundColor: theme.colors.surface,
                color: theme.colors.textMain,
            }}>
                  {panelOpen ? (<>
                      <Minimize2 className="w-3.5 h-3.5"/>
                      Close panel
                    </>) : (<>
                      <Maximize2 className="w-3.5 h-3.5"/>
                      Show panel
                    </>)}
                </button>
                <button type="button" onClick={() => {
                abortScan();
                setPanelOpen(false);
            }} className="w-full flex items-center justify-center gap-1.5 py-1.5 mt-1.5 text-[10px] font-semibold rounded-sm border transition-colors hover:opacity-90" style={{
                borderColor: "rgba(239,68,68,0.5)",
                backgroundColor: "rgba(239,68,68,0.1)",
                color: "#ef4444",
            }} title="Stop scan and close connection (stops reconnecting)" aria-label="Abort scan">
                  <Square className="w-3 h-3"/>
                  Abort scan
                </button>
                {activeScanId && (<p className="text-[9px] font-mono mt-1.5 truncate text-center" style={{ color: theme.colors.textMuted }} title={activeScanId}>
                    {activeScanId.slice(0, 14)}…
                  </p>)}
              </>) : (<>
                <p className="text-[10px] mb-2" style={{ color: theme.colors.textMuted }}>
                  No scan in progress
                </p>
                <button type="button" onClick={() => {
                setPanelOpen(true);
                router.push("/dashboard");
            }} className="w-full flex items-center justify-center gap-1.5 py-1.5 text-[11px] font-semibold rounded-sm border transition-colors hover:opacity-90" style={{
                borderColor: theme.colors.border,
                backgroundColor: theme.colors.surface,
                color: theme.colors.textMain,
            }}>
                  <Maximize2 className="w-3.5 h-3.5"/>
                  Show panel
                </button>
              </>)}
          </div>

          {isDetailPage && (<div className="px-3 pt-6 pb-2">
              <span className="text-[10px] font-semibold uppercase tracking-widest flex items-center gap-2" style={{ color: theme.colors.textMuted }}>
                <span className="w-2 h-[1px]" style={{ backgroundColor: theme.colors.border }}></span>
                Active Context
              </span>
            </div>)}
        </div>

        
        <div className="p-4 border-t shrink-0" style={{ borderColor: theme.colors.border, backgroundColor: theme.colors.bg }}>
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-sm border flex items-center justify-center shrink-0" style={{ borderColor: theme.colors.border, backgroundColor: theme.colors.surface }}>
              <User className="w-4 h-4" style={{ color: theme.colors.textMuted }}/>
            </div>
            <div className="flex flex-col flex-1 min-w-0">
              <span className="text-xs font-semibold truncate" style={{ color: theme.colors.textMain }}>
                {user?.name || user?.email?.split('@')[0] || 'User'}
              </span>
              <span className="text-[10px] font-mono uppercase tracking-wider" style={{ color: theme.colors.accent }}>
                Pro Plan
              </span>
            </div>
            <button onClick={handleLogout} className="p-1.5 rounded-sm hover:bg-black/5 dark:hover:bg-white/5 transition-colors shrink-0" style={{ color: theme.colors.textMuted }} title="Logout">
              <LogOut className="w-4 h-4"/>
            </button>
          </div>
        </div>
      </aside>

      
      {panelOpen && (<div ref={flyoutRef} className="fixed top-0 bottom-0 w-[min(100vw-260px,22rem)] border-r shadow-2xl z-30 flex flex-col overflow-hidden max-md:hidden" style={{
                left: 260,
                backgroundColor: theme.colors.bg,
                borderColor: theme.colors.border,
                color: theme.colors.textMain,
                boxShadow: "8px 0 24px rgba(0,0,0,0.15)",
            }}>
          <div className="p-4 pb-2 flex items-center justify-between border-b shrink-0 gap-2" style={{ borderColor: theme.colors.border }}>
            <span className="text-xs font-bold uppercase tracking-wider" style={{ color: theme.colors.textMuted }}>
              Currently doing
            </span>
            <div className="flex items-center gap-1">
              {isScanning && (<button type="button" onClick={() => {
                    abortScan();
                    setPanelOpen(false);
                }} className="flex items-center gap-1.5 px-2 py-1.5 rounded-md text-[10px] font-semibold uppercase tracking-wide transition-colors hover:opacity-90" style={{ backgroundColor: "rgba(239,68,68,0.15)", color: "#ef4444", border: "1px solid rgba(239,68,68,0.4)" }} title="Stop scan and close connection" aria-label="Abort scan">
                  <Square className="w-3.5 h-3.5"/>
                  Abort
                </button>)}
              <button type="button" onClick={() => {
                setPanelOpen(false);
                if (isScanning)
                    minimizeScan();
            }} className="p-1.5 rounded-md transition-colors hover:bg-black/5 dark:hover:bg-white/5" style={{ color: theme.colors.textMuted }} title="Close" aria-label="Close panel">
                <Minimize2 className="w-4 h-4"/>
              </button>
            </div>
          </div>
          <div className="p-5 flex flex-col items-center gap-4 overflow-y-auto flex-1">
            {isScanning ? (<>
                <div className="relative w-28 h-28 flex items-center justify-center shrink-0">
                  <svg className="absolute inset-0 w-full h-full -rotate-90" viewBox="0 0 100 100">
                    <circle cx="50" cy="50" r="42" fill="none" stroke={theme.colors.border} strokeWidth="3"/>
                    <circle cx="50" cy="50" r="42" fill="none" stroke={foundVulns > 0 ? "#ef4444" : theme.colors.accent} strokeWidth="3" strokeLinecap="round" strokeDasharray={2 * Math.PI * 42} strokeDashoffset={2 * Math.PI * 42 * (1 - scanProgress / 100)} className="transition-all duration-500"/>
                  </svg>
                  <div className="w-14 h-14 border rounded-lg flex items-center justify-center" style={{
                    backgroundColor: foundVulns > 0 ? "rgba(239,68,68,0.1)" : `${theme.colors.accent}15`,
                    borderColor: foundVulns > 0 ? "rgba(239,68,68,0.3)" : `${theme.colors.accent}30`,
                }}>
                    {foundVulns > 0 ? (<AlertTriangle className="w-6 h-6 text-red-500"/>) : (<Shield className="w-6 h-6" style={{ color: theme.colors.accent }}/>)}
                  </div>
                </div>
                <div className="text-center w-full space-y-1">
                  <p className="text-sm font-semibold" style={{ color: theme.colors.textMain }}>
                    {foundVulns > 0 ? `${foundVulns} issue${foundVulns !== 1 ? "s" : ""} found` : "Scanning…"}
                  </p>
                  <p className="text-[11px] font-mono truncate" style={{ color: theme.colors.textMuted }} title={scanStatus}>
                    {scanStatus || "…"}
                  </p>
                </div>
                {scanActivityLog.length > 0 && (<div className="w-full max-h-20 overflow-y-auto rounded border px-2 py-1.5 font-mono text-[10px] leading-relaxed space-y-0.5" style={{ backgroundColor: theme.colors.surface, borderColor: theme.colors.border, color: theme.colors.textMuted }}>
                    {scanActivityLog.slice(-8).map((line, i) => (<div key={i} className="truncate">{line}</div>))}
                  </div>)}
                <div className="w-full space-y-1">
                  <div className="flex justify-between text-[10px] font-mono" style={{ color: theme.colors.textMuted }}>
                    <span>Progress</span>
                    <span>{Math.round(scanProgress)}%</span>
                  </div>
                  <div className="w-full h-1.5 rounded-full overflow-hidden" style={{ backgroundColor: theme.colors.surface }}>
                    <div className="h-full rounded-full transition-all duration-300" style={{
                    width: `${scanProgress}%`,
                    backgroundColor: foundVulns > 0 ? "#ef4444" : theme.colors.accent,
                }}/>
                  </div>
                </div>
                {activeScanId && (<p className="text-[9px] font-mono truncate w-full text-center" style={{ color: theme.colors.textMuted }} title={activeScanId}>
                    {activeScanId.slice(0, 18)}…
                  </p>)}
              </>) : (<>
                <div className="w-16 h-16 rounded-xl border flex items-center justify-center shrink-0" style={{ backgroundColor: theme.colors.surface, borderColor: theme.colors.border }}>
                  <Activity className="w-8 h-8" style={{ color: theme.colors.textMuted }}/>
                </div>
                <p className="text-sm font-semibold text-center" style={{ color: theme.colors.textMain }}>
                  No scan in progress
                </p>
                <p className="text-[11px] text-center" style={{ color: theme.colors.textMuted }}>
                  Start a scan from the dashboard to see progress here.
                </p>
              </>)}
          </div>
        </div>)}

      
      <main className="flex-1 flex flex-col h-screen overflow-hidden relative">
        {children}
      </main>

      
      {cacheChoicePending && (<div className="fixed inset-0 z-[100] flex items-center justify-center p-4" style={{ backgroundColor: "rgba(0,0,0,0.5)" }} role="dialog" aria-modal="true" aria-labelledby="cache-choice-title">
          <div className="w-full max-w-md rounded-xl border-2 shadow-2xl p-6 flex flex-col gap-4" style={{
                backgroundColor: theme.colors.bg,
                borderColor: theme.colors.border,
                color: theme.colors.textMain,
            }}>
            <h2 id="cache-choice-title" className="text-base font-semibold" style={{ color: theme.colors.textMain }}>
              This project was scanned before
            </h2>
            <p className="text-sm" style={{ color: theme.colors.textMuted }}>
              Use cached context (faster) or rescan from scratch to rebuild all indexes?
            </p>
            <div className="flex gap-3 pt-2">
              <button type="button" onClick={() => sendCacheChoice(true)} className="flex-1 py-2.5 px-4 rounded-lg font-semibold text-sm transition-colors" style={{
                backgroundColor: theme.colors.accent,
                color: theme.colors.bg,
            }}>
                Use cached data
              </button>
              <button type="button" onClick={() => sendCacheChoice(false)} className="flex-1 py-2.5 px-4 rounded-lg font-semibold text-sm border transition-colors" style={{
                borderColor: theme.colors.border,
                backgroundColor: theme.colors.surface,
                color: theme.colors.textMain,
            }}>
                Rescan from 0
              </button>
            </div>
          </div>
        </div>)}
    </div>);
}
export default function DashboardLayout({ children }: {
    children: React.ReactNode;
}) {
    return (<DashboardScanProvider>
      <DashboardScanChrome>{children}</DashboardScanChrome>
    </DashboardScanProvider>);
}
