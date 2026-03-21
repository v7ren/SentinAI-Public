import { useState } from 'react'
import { useAuth } from '../api'

export default function Upload() {
  const [file, setFile] = useState(null)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const { fetchApi } = useAuth()

  async function handleSubmit(e) {
    e.preventDefault()
    if (!file) {
      setError('Choose a file')
      return
    }
    setError('')
    setMessage('')
    const form = new FormData()
    form.append('file', file)
    try {
      const res = await fetch('/api/upload', {
        method: 'POST',
        credentials: 'include',
        body: form,
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) throw new Error(data.error || res.statusText)
      setMessage(`Uploaded: ${data.path} (${data.size} bytes)`)
      setFile(null)
      e.target.reset()
    } catch (err) {
      setError(err.message || 'Upload failed')
    }
  }

  return (
    <>
      <h1 className="page-title">Upload file</h1>
      <div className="card" style={{ maxWidth: 480 }}>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>File</label>
            <input
              type="file"
              className="input"
              onChange={e => setFile(e.target.files?.[0] || null)}
            />
          </div>
          {error && <p style={{ color: 'var(--danger)', marginBottom: '1rem' }}>{error}</p>}
          {message && <p style={{ color: 'var(--success)', marginBottom: '1rem' }}>{message}</p>}
          <button type="submit" className="btn btn-primary">Upload</button>
        </form>
      </div>
    </>
  )
}
