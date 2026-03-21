import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { API } from '../App'

export default function Register() {
  const [form, setForm] = useState({
    username: '',
    password: '',
    email: '',
    role: 'user',
  })
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const res = await fetch(`${API}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })
      const data = await res.json()
      if (res.ok) {
        localStorage.setItem('token', data.token)
        navigate('/dashboard')
      }
    } catch (err) {
      console.error(err)
    }
  }

  return (
    <div className="container">
      <h1>Register</h1>
      <form onSubmit={handleSubmit} className="card">
        <div>
          <label>Username </label>
          <input value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
        </div>
        <div>
          <label>Password </label>
          <input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
        </div>
        <div>
          <label>Email </label>
          <input value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        </div>
        <input type="hidden" name="role" value={form.role} />
        <button type="submit">Create account</button>
      </form>
    </div>
  )
}
