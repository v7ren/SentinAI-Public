import { useState, useEffect } from 'react'
import { useAuth } from '../api'

export default function Admin() {
  const [apiKey, setApiKey] = useState('')
  const [users, setUsers] = useState(null)
  const [error, setError] = useState('')
  const { fetchApi } = useAuth()

  async function loadUsers() {
    if (!apiKey.trim()) {
      setError('Enter API key')
      return
    }
    setError('')
    setUsers(null)
    try {
      const data = await fetch('/api/admin/users', {
        headers: { 'X-API-Key': apiKey },
        credentials: 'include',
      })
      const json = await data.json().catch(() => ({}))
      if (!data.ok) throw new Error(json.error || 'Forbidden')
      setUsers(Array.isArray(json) ? json : [])
    } catch (err) {
      setError(err.message || 'Failed to load users')
      setUsers([])
    }
  }

  return (
    <>
      <h1 className="page-title">Admin — Users</h1>
      <div className="card" style={{ marginBottom: '1rem', maxWidth: 480 }}>
        <div className="form-group">
          <label>API key</label>
          <input
            type="password"
            className="input"
            placeholder="Admin API key"
            value={apiKey}
            onChange={e => setApiKey(e.target.value)}
          />
        </div>
        {error && <p style={{ color: 'var(--danger)', marginBottom: '1rem' }}>{error}</p>}
        <button type="button" className="btn btn-primary" onClick={loadUsers}>Load users</button>
      </div>
      {users !== null && (
        <div className="table-wrap card" style={{ padding: 0 }}>
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Username</th>
                <th>Email</th>
                <th>Role</th>
              </tr>
            </thead>
            <tbody>
              {users.map(u => (
                <tr key={u.id}>
                  <td>{u.id}</td>
                  <td>{u.username}</td>
                  <td>{u.email}</td>
                  <td>{u.role}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  )
}
