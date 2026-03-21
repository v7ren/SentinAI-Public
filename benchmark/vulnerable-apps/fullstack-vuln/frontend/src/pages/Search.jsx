import { useState } from 'react'
import { useAuth } from '../api'

export default function Search() {
  const [q, setQ] = useState('')
  const [results, setResults] = useState([])
  const [searched, setSearched] = useState(false)
  const { fetchApi } = useAuth()

  async function handleSearch(e) {
    e.preventDefault()
    if (!q.trim()) return
    setSearched(true)
    try {
      const data = await fetchApi(`/search?q=${encodeURIComponent(q)}`)
      setResults(Array.isArray(data) ? data : [])
    } catch {
      setResults([])
    }
  }

  return (
    <>
      <h1 className="page-title">Search profiles</h1>
      <form onSubmit={handleSearch} style={{ marginBottom: '1.5rem', display: 'flex', gap: '0.5rem' }}>
        <input
          type="text"
          className="input"
          placeholder="Search by display name or bio…"
          value={q}
          onChange={e => setQ(e.target.value)}
          style={{ flex: 1 }}
        />
        <button type="submit" className="btn btn-primary">Search</button>
      </form>
      {searched && (
        <div className="card">
          <h3 style={{ marginTop: 0 }}>Results</h3>
          {results.length === 0 ? (
            <p style={{ color: 'var(--text-muted)' }}>No profiles found.</p>
          ) : (
            <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
              {results.map(p => (
                <li key={p.id} style={{ padding: '0.75rem 0', borderBottom: '1px solid var(--border)' }}>
                  <strong>{p.display_name}</strong>
                  <p style={{ margin: '0.25rem 0 0', color: 'var(--text-muted)', fontSize: '0.9rem' }}>{p.bio}</p>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </>
  )
}
