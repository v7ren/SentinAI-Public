"use client";
import { useTheme } from "@/context/ThemeContext";
import { useAuth } from "@/app/hooks/useAuth";
import { Lock, Mail, User, Settings, CheckCircle, Loader2, Shield } from "lucide-react";
import { useRouter } from "next/navigation";
import React, { useEffect, useState } from "react";
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001";
export default function SettingsPage() {
    const { theme } = useTheme();
    const { user, isAuthenticated, refreshUser } = useAuth();
    const router = useRouter();
    const [authMethods, setAuthMethods] = useState<string[]>([]);
    const [loading, setLoading] = useState(true);
    const [addPassword, setAddPassword] = useState("");
    const [addPasswordConfirm, setAddPasswordConfirm] = useState("");
    const [currentPassword, setCurrentPassword] = useState("");
    const [newPassword, setNewPassword] = useState("");
    const [newPasswordConfirm, setNewPasswordConfirm] = useState("");
    const [submitting, setSubmitting] = useState(false);
    const [message, setMessage] = useState<{
        type: "success" | "error";
        text: string;
    } | null>(null);
    const hasPassword = authMethods.includes("password");
    const hasGoogle = authMethods.includes("google");
    useEffect(() => {
        if (!isAuthenticated)
            return;
        const fetchConnections = async () => {
            try {
                const res = await fetch(`${API_BASE}/auth/connections`, { credentials: "include" });
                if (res.ok) {
                    const data = await res.json();
                    setAuthMethods(data.auth_methods || []);
                }
            }
            catch {
                setAuthMethods([]);
            }
            finally {
                setLoading(false);
            }
        };
        fetchConnections();
    }, [isAuthenticated]);
    const getCsrfToken = async () => {
        const res = await fetch(`${API_BASE}/api/csrf-token`, { credentials: "include" });
        const data = await res.json();
        return data.csrf_token;
    };
    const handleAddPassword = async (e: React.FormEvent) => {
        e.preventDefault();
        setMessage(null);
        if (addPassword.length < 6) {
            setMessage({ type: "error", text: "Password must be at least 6 characters" });
            return;
        }
        if (addPassword !== addPasswordConfirm) {
            setMessage({ type: "error", text: "Passwords do not match" });
            return;
        }
        setSubmitting(true);
        try {
            const csrfToken = await getCsrfToken();
            const res = await fetch(`${API_BASE}/auth/add-password`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRF-Token": csrfToken,
                },
                credentials: "include",
                body: JSON.stringify({ new_password: addPassword }),
            });
            const data = await res.json();
            if (res.ok) {
                setMessage({ type: "success", text: data.message || "Password added successfully. You can now sign in with email and password." });
                setAddPassword("");
                setAddPasswordConfirm("");
                setAuthMethods((m) => (m.includes("password") ? m : [...m, "password"]));
            }
            else {
                setMessage({ type: "error", text: data.error || "Failed to add password" });
            }
        }
        catch {
            setMessage({ type: "error", text: "Network error. Please try again." });
        }
        finally {
            setSubmitting(false);
        }
    };
    const handleChangePassword = async (e: React.FormEvent) => {
        e.preventDefault();
        setMessage(null);
        if (newPassword.length < 6) {
            setMessage({ type: "error", text: "New password must be at least 6 characters" });
            return;
        }
        if (newPassword !== newPasswordConfirm) {
            setMessage({ type: "error", text: "Passwords do not match" });
            return;
        }
        setSubmitting(true);
        try {
            const csrfToken = await getCsrfToken();
            const res = await fetch(`${API_BASE}/auth/change-password`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRF-Token": csrfToken,
                },
                credentials: "include",
                body: JSON.stringify({
                    current_password: currentPassword,
                    new_password: newPassword,
                }),
            });
            const data = await res.json();
            if (res.ok) {
                setMessage({ type: "success", text: "Password changed successfully." });
                setCurrentPassword("");
                setNewPassword("");
                setNewPasswordConfirm("");
            }
            else {
                setMessage({ type: "error", text: data.error || "Failed to change password" });
            }
        }
        catch {
            setMessage({ type: "error", text: "Network error. Please try again." });
        }
        finally {
            setSubmitting(false);
        }
    };
    if (!isAuthenticated)
        return null;
    return (<div className="h-full flex flex-col overflow-auto" style={{ backgroundColor: theme.colors.bg }}>
      
      <header className="h-14 px-6 flex items-center border-b shrink-0" style={{ borderColor: theme.colors.border, backgroundColor: theme.colors.bg }}>
        <div className="flex items-center gap-3">
          <Settings className="w-5 h-5" style={{ color: theme.colors.accent }}/>
          <h1 className="text-sm font-semibold tracking-wide" style={{ color: theme.colors.textMain }}>
            Account Settings
          </h1>
        </div>
      </header>

      
      <div className="flex-1 overflow-auto p-6 max-w-2xl">
        {loading ? (<div className="flex items-center justify-center py-12">
            <Loader2 className="w-6 h-6 animate-spin" style={{ color: theme.colors.textMuted }}/>
          </div>) : (<div className="space-y-8">
            
            <section className="p-5 border rounded-sm" style={{ backgroundColor: theme.colors.surface, borderColor: theme.colors.border }}>
              <h2 className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: theme.colors.textMuted }}>
                Profile
              </h2>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <User className="w-4 h-4" style={{ color: theme.colors.textMuted }}/>
                  <div>
                    <p className="text-xs" style={{ color: theme.colors.textMuted }}>Name</p>
                    <p className="text-sm font-medium" style={{ color: theme.colors.textMain }}>
                      {user?.name || user?.email?.split("@")[0] || "—"}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Mail className="w-4 h-4" style={{ color: theme.colors.textMuted }}/>
                  <div>
                    <p className="text-xs" style={{ color: theme.colors.textMuted }}>Email</p>
                    <p className="text-sm font-medium" style={{ color: theme.colors.textMain }}>
                      {user?.email || "—"}
                    </p>
                  </div>
                </div>
              </div>
            </section>

            
            <section className="p-5 border rounded-sm" style={{ backgroundColor: theme.colors.surface, borderColor: theme.colors.border }}>
              <h2 className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: theme.colors.textMuted }}>
                Sign-in methods
              </h2>
              <div className="space-y-2 mb-6">
                {hasGoogle && (<div className="flex items-center gap-3 py-2">
                    <div className="w-8 h-8 rounded border flex items-center justify-center" style={{ borderColor: theme.colors.border }}>
                      <svg className="w-4 h-4" viewBox="0 0 24 24">
                        <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                        <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                        <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                        <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                      </svg>
                    </div>
                    <div>
                      <p className="text-sm font-medium" style={{ color: theme.colors.textMain }}>Google</p>
                      <p className="text-xs" style={{ color: theme.colors.textMuted }}>Sign in with your Google account</p>
                    </div>
                    <CheckCircle className="w-4 h-4 ml-auto shrink-0" style={{ color: theme.colors.accent }}/>
                  </div>)}
                {hasPassword && (<div className="flex items-center gap-3 py-2">
                    <div className="w-8 h-8 rounded border flex items-center justify-center" style={{ borderColor: theme.colors.border }}>
                      <Lock className="w-4 h-4" style={{ color: theme.colors.textMuted }}/>
                    </div>
                    <div>
                      <p className="text-sm font-medium" style={{ color: theme.colors.textMain }}>Email & Password</p>
                      <p className="text-xs" style={{ color: theme.colors.textMuted }}>Sign in with email and password</p>
                    </div>
                    <CheckCircle className="w-4 h-4 ml-auto shrink-0" style={{ color: theme.colors.accent }}/>
                  </div>)}
              </div>

              
              {!hasPassword && (<div className="pt-4 border-t" style={{ borderColor: theme.colors.border }}>
                  <p className="text-xs mb-4" style={{ color: theme.colors.textMuted }}>
                    Add a password to sign in with email and password as well.
                  </p>
                  <form onSubmit={handleAddPassword} className="space-y-3">
                    <div>
                      <label className="block text-xs mb-1.5" style={{ color: theme.colors.textMuted }}>New password</label>
                      <input type="password" value={addPassword} onChange={(e) => setAddPassword(e.target.value)} minLength={6} placeholder="At least 6 characters" className="w-full px-3 py-2 text-sm border rounded-sm focus:outline-none focus:ring-1" style={{
                    backgroundColor: theme.colors.bg,
                    borderColor: theme.colors.border,
                    color: theme.colors.textMain,
                }}/>
                    </div>
                    <div>
                      <label className="block text-xs mb-1.5" style={{ color: theme.colors.textMuted }}>Confirm password</label>
                      <input type="password" value={addPasswordConfirm} onChange={(e) => setAddPasswordConfirm(e.target.value)} placeholder="Re-enter password" className="w-full px-3 py-2 text-sm border rounded-sm focus:outline-none focus:ring-1" style={{
                    backgroundColor: theme.colors.bg,
                    borderColor: theme.colors.border,
                    color: theme.colors.textMain,
                }}/>
                    </div>
                    <button type="submit" disabled={submitting} className="px-4 py-2 text-xs font-medium uppercase tracking-wider disabled:opacity-50 transition-colors" style={{ backgroundColor: theme.colors.accent, color: theme.colors.accentText }}>
                      {submitting ? <><Loader2 className="w-3.5 h-3.5 animate-spin inline"/> Adding…</> : "Add password"}
                    </button>
                  </form>
                </div>)}

              
              {hasPassword && (<div className="pt-4 border-t" style={{ borderColor: theme.colors.border }}>
                  <p className="text-xs mb-4" style={{ color: theme.colors.textMuted }}>
                    Update your password.
                  </p>
                  <form onSubmit={handleChangePassword} className="space-y-3">
                    <div>
                      <label className="block text-xs mb-1.5" style={{ color: theme.colors.textMuted }}>Current password</label>
                      <input type="password" value={currentPassword} onChange={(e) => setCurrentPassword(e.target.value)} required placeholder="Current password" className="w-full px-3 py-2 text-sm border rounded-sm focus:outline-none focus:ring-1" style={{
                    backgroundColor: theme.colors.bg,
                    borderColor: theme.colors.border,
                    color: theme.colors.textMain,
                }}/>
                    </div>
                    <div>
                      <label className="block text-xs mb-1.5" style={{ color: theme.colors.textMuted }}>New password</label>
                      <input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} minLength={6} placeholder="At least 6 characters" className="w-full px-3 py-2 text-sm border rounded-sm focus:outline-none focus:ring-1" style={{
                    backgroundColor: theme.colors.bg,
                    borderColor: theme.colors.border,
                    color: theme.colors.textMain,
                }}/>
                    </div>
                    <div>
                      <label className="block text-xs mb-1.5" style={{ color: theme.colors.textMuted }}>Confirm new password</label>
                      <input type="password" value={newPasswordConfirm} onChange={(e) => setNewPasswordConfirm(e.target.value)} placeholder="Re-enter new password" className="w-full px-3 py-2 text-sm border rounded-sm focus:outline-none focus:ring-1" style={{
                    backgroundColor: theme.colors.bg,
                    borderColor: theme.colors.border,
                    color: theme.colors.textMain,
                }}/>
                    </div>
                    <button type="submit" disabled={submitting} className="px-4 py-2 text-xs font-medium uppercase tracking-wider disabled:opacity-50 transition-colors" style={{ backgroundColor: theme.colors.accent, color: theme.colors.accentText }}>
                      {submitting ? <><Loader2 className="w-3.5 h-3.5 animate-spin inline"/> Updating…</> : "Change password"}
                    </button>
                  </form>
                </div>)}
            </section>

            
            {message && (<div className={`p-4 rounded-sm flex items-center gap-3 ${message.type === "success"
                    ? "bg-green-500/10 border border-green-500/30"
                    : "bg-red-500/10 border border-red-500/30"}`}>
                {message.type === "success" ? (<CheckCircle className="w-4 h-4 text-green-500 shrink-0"/>) : (<Shield className="w-4 h-4 text-red-500 shrink-0"/>)}
                <p className={`text-sm ${message.type === "success" ? "text-green-700 dark:text-green-400" : "text-red-700 dark:text-red-400"}`}>
                  {message.text}
                </p>
              </div>)}
          </div>)}
      </div>
    </div>);
}
