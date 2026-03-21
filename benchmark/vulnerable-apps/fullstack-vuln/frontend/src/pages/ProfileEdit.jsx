import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../api'

export default function ProfileEdit() {
  const { id } = useParams()
  const isNew = !id
  const [display_name, setDisplayName] = useState('')
  const [bio, setBio] = useState('')
  const [loading, setLoading] = useState(!isNew)
  const [error, setError] = useState('')
  const { fetchApi } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (isNew) return
    fetchApi(`/profile/${id}`)
      .then(data => {
        setDisplayName(data.display_name || '')
        setBio(data.bio || '')
      })
      .catch(() => setError('Profile not found'))
      .finally(() => setLoading(false))
  }, [id, isNew, fetchApi])

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    try {
      if (isNew) {
        await fetchApi('/profile', { method: 'POST', body: { display_name, bio } })
        navigate('/profiles')
      } else {
        await fetchApi(`/profile/${id}`, { method: 'PUT', body: { display_name, bio } })
        navigate('/profiles')
      }
    } catch (err) {
      setError(err.message || 'Save failed')
    }
  }

  if (loading) return <p>Loading…</p>

  return (
    <div className="card" style={{ maxWidth: 560 }}>
      <h1 className="page-title">{isNew ? 'New profile' : 'Edit profile'}</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Display name</label>
          <input
            type="text"
            className="input"
            value={display_name}
            onChange={e => setDisplayName(e.target.value)}
          />
        </div>
        <div className="form-group">
          <label>Bio</label>
          <textarea
            className="input"
            rows={4}
            value={bio}
            onChange={e => setBio(e.target.value)}
            style={{ resize: 'vertical' }}
          />
        </div>
        {error && <p style={{ color: 'var(--danger)', marginBottom: '1rem' }}>{error}</p>}
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button type="submit" className="btn btn-primary">Save</button>
          <button type="button" className="btn btn-ghost" onClick={() => navigate('/profiles')}>Cancel</button>
        </div>
      </form>
    </div>
  )
}
