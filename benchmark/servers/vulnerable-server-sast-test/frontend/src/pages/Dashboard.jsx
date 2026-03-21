import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { API } from '../App'

export default function Dashboard() {
  const [user, setUser] = useState(null)
  const [orders, setOrders] = useState([])
  const navigate = useNavigate()

  useEffect(() => {
    const token = localStorage.getItem('token')
    const u = localStorage.getItem('user')
    if (!token) {
      navigate('/login')
      return
    }
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      setUser({ ...JSON.parse(u || '{}'), ...payload })
    } catch (e) {
      navigate('/login')
    }
  }, [navigate])

  const loadOrders = async () => {
    const token = localStorage.getItem('token')
    const res = await fetch(`${API}/api/orders`, { headers: { Authorization: `Bearer ${token}` } })
    const data = await res.json()
    setOrders(Array.isArray(data) ? data : [])
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    navigate('/login')
  }

  if (!user) return <div className="container">Loading...</div>

  return (
    <div className="container">
      <h1>Dashboard</h1>
      <p>Welcome, {user.username || user.sub}</p>
      <button onClick={logout}>Logout</button>
      <div className="card">
        <h3>Your token (debug)</h3>
        <code style={{ wordBreak: 'break-all', fontSize: 12 }}>{localStorage.getItem('token')?.slice(0, 80)}...</code>
      </div>
      <div className="card">
        <button onClick={loadOrders}>Load orders</button>
        <pre>{JSON.stringify(orders, null, 2)}</pre>
      </div>
    </div>
  )
}
