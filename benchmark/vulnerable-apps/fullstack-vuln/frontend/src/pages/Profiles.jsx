import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../api'

export default function Profiles() {
  const [list, setList] = useState([])
  const [loading, setLoading] = useState(true)
  const { fetchApi } = useAuth()

  useEffect(() => {
    fetchApi('/profile')
      .then(setList)
      .catch(() => setList([]))
      .finally(() => setLoading(false))
  }, [fetchApi])

  if (loading) return <p>Loading profiles…</p>

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h1 className="page-title" style={{ margin: 0 }}>My profiles</h1>
        <Link to="/profiles/new" className="btn btn-primary">New profile</Link>
      </div>
      {list.length === 0 ? (
        <p style={{ color: 'var(--text-muted)' }}>No profiles yet. <Link to="/profiles/new">Create one</Link>.</p>
      ) : (
        <div className="table-wrap card" style={{ padding: 0 }}>
          <table>
            <thead>
              <tr>
                <th>Display name</th>
                <th>Bio</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {list.map(p => (
                <tr key={p.id}>
                  <td>{p.display_name}</td>
                  <td>{p.bio?.slice(0, 60)}{p.bio?.length > 60 ? '…' : ''}</td>
                  <td><Link to={`/profiles/${p.id}/edit`} className="btn btn-ghost">Edit</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  )
}
