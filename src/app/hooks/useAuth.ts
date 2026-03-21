"use client";
import { useState, useEffect, useCallback } from "react";
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001";
interface User {
    email: string;
    name: string;
}
interface AuthState {
    user: User | null;
    loading: boolean;
    error: string | null;
}
export function useAuth() {
    const [state, setState] = useState<AuthState>({
        user: null,
        loading: true,
        error: null,
    });
    const fetchUser = useCallback(async () => {
        try {
            const res = await fetch(`${API_BASE}/auth/me`, {
                credentials: "include",
            });
            if (res.ok) {
                const data = await res.json();
                setState({ user: data.user, loading: false, error: null });
            }
            else {
                setState({ user: null, loading: false, error: null });
            }
        }
        catch (err) {
            setState({ user: null, loading: false, error: "Failed to check auth status" });
        }
    }, []);
    useEffect(() => {
        fetchUser();
    }, [fetchUser]);
    const getCsrfToken = async () => {
        const res = await fetch(`${API_BASE}/api/csrf-token`, {
            credentials: "include",
        });
        const data = await res.json();
        return data.csrf_token;
    };
    const login = async (email: string, password: string): Promise<boolean> => {
        try {
            const csrfToken = await getCsrfToken();
            const res = await fetch(`${API_BASE}/auth/login`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRF-Token": csrfToken,
                },
                credentials: "include",
                body: JSON.stringify({ email, password }),
            });
            if (res.ok) {
                const data = await res.json();
                setState({ user: data.user, loading: false, error: null });
                return true;
            }
            else {
                const data = await res.json();
                setState((prev) => ({ ...prev, error: data.error || "Login failed" }));
                return false;
            }
        }
        catch (err) {
            setState((prev) => ({ ...prev, error: "Network error" }));
            return false;
        }
    };
    const register = async (email: string, password: string, name: string): Promise<boolean> => {
        try {
            const csrfToken = await getCsrfToken();
            const res = await fetch(`${API_BASE}/auth/register`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRF-Token": csrfToken,
                },
                credentials: "include",
                body: JSON.stringify({ email, password, name }),
            });
            if (res.ok) {
                const data = await res.json();
                setState({ user: data.user, loading: false, error: null });
                return true;
            }
            else {
                const data = await res.json();
                setState((prev) => ({ ...prev, error: data.error || "Registration failed" }));
                return false;
            }
        }
        catch (err) {
            setState((prev) => ({ ...prev, error: "Network error" }));
            return false;
        }
    };
    const logout = async (): Promise<void> => {
        try {
            const csrfToken = await getCsrfToken();
            await fetch(`${API_BASE}/auth/logout`, {
                method: "POST",
                headers: { "X-CSRF-Token": csrfToken },
                credentials: "include",
            });
            setState({ user: null, loading: false, error: null });
        }
        catch (err) {
            console.error("Logout error:", err);
        }
    };
    const googleLogin = () => {
        window.location.href = `${API_BASE}/auth/google`;
    };
    return {
        user: state.user,
        loading: state.loading,
        error: state.error,
        isAuthenticated: !!state.user,
        login,
        register,
        logout,
        googleLogin,
        refreshUser: fetchUser,
    };
}
