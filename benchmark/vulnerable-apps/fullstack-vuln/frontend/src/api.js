import { useState, useEffect, createContext, useContext } from 'react'

const API = '/api'

async function fetchApi(path, options = {}) {
  const res = await fetch(API + path, {
    ...options,
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...(options.body && typeof options.body === 'object' && !(options.body instanceof FormData)
      ? { body: JSON.stringify(options.body) }
      : { body: options.body }),
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(data.error || res.statusText)
  return data
}

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchApi('/auth/me')
      .then(({ user: u }) => setUser(u))
      .catch(() => setUser(null))
      .finally(() => setLoading(false))
  }, [])

  const login = async (username, password) => {
    const data = await fetchApi('/auth/login', { method: 'POST', body: { username, password } })
    setUser(data.user)
    return data
  }

  const register = async (username, password, email, role = 'user') => {
    const data = await fetchApi('/auth/register', { method: 'POST', body: { username, password, email, role } })
    setUser({ id: data.id, username, email, role })
    return data
  }

  const logout = async () => {
    await fetchApi('/auth/logout', { method: 'POST' })
    setUser(null)
  }

  if (loading) return <div className="main">Loading…</div>
  return (
    <AuthContext.Provider value={{ user, login, register, logout, fetchApi }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
