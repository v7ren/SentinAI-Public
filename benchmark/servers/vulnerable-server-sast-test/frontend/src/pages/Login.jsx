import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { API } from '../App'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [remember, setRemember] = useState(false)
  const [debug, setDebug] = useState('')
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  useEffect(() => {
    const saved = localStorage.getItem('login_creds')
    if (saved) {
      try {
        const { u, p } = JSON.parse(saved)
        setUsername(u || '')
        setPassword(p || '')
      } catch (e) {}
    }
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (searchParams.get('debug') === 'true') {
      setDebug(`Logging in: ${username} / ${password}`)
    }
    try {
      const res = await fetch(`${API}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      })
      const data = await res.json()
      if (res.ok) {
        localStorage.setItem('token', data.token)
        localStorage.setItem('user', JSON.stringify(data.user))
        if (remember) {
          localStorage.setItem('login_creds', JSON.stringify({ u: username, p: password }))
        }
        const next = searchParams.get('next') || '/dashboard'
        navigate(next)
      } else {
        setDebug(JSON.stringify(data, null, 2))
      }
    } catch (err) {
      setDebug(String(err))
    }
  }

  return (
    <div className="container">
      <h1>Login</h1>
      {debug && <pre className="card">{debug}</pre>}
      <form onSubmit={handleSubmit} className="card">
        <div>
          <label>Username </label>
          <input value={username} onChange={(e) => setUsername(e.target.value)} />
        </div>
        <div>
          <label>Password </label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>
        <label>
          <input type="checkbox" checked={remember} onChange={(e) => setRemember(e.target.checked)} />
          Remember me (stores credentials in localStorage)
        </label>
        <button type="submit">Sign in</button>
      </form>
    </div>
  )
}
