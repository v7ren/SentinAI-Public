import { createContext, useContext, useState, useCallback, useEffect } from 'react';
import * as authApi from '../api/auth';
import { saveSession, clearSession, getStoredUser } from '../utils/authUtils';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(getStoredUser());
  const [loading, setLoading] = useState(true);

  const login = useCallback(async (email, password) => {
    const res = await authApi.login(email, password);
    const { user: u, token, refreshToken } = res.data;
    saveSession(token, u, refreshToken);
    setUser(u);
    return res;
  }, []);

  const register = useCallback(async (email, password, fullName) => {
    const res = await authApi.register(email, password, fullName);
    const { user: u, token, refreshToken } = res.data;
    saveSession(token, u, refreshToken);
    setUser(u);
    return res;
  }, []);

  const logout = useCallback(() => {
    clearSession();
    setUser(null);
  }, []);

  useEffect(() => {
    setLoading(false);
  }, []);

  const value = { user, loading, login, register, logout };
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
