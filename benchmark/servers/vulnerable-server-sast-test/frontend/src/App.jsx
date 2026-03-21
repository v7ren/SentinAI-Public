import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Admin from './pages/Admin'
import Export from './pages/Export'

const API = 'http://localhost:5008'

export { API }

export default function App() {
  return (
    <BrowserRouter>
      <nav style={{ padding: '12px 24px', background: '#0f0f1a', borderBottom: '1px solid #333' }}>
        <Link to="/" style={{ marginRight: 16 }}>Home</Link>
        <Link to="/login" style={{ marginRight: 16 }}>Login</Link>
        <Link to="/register" style={{ marginRight: 16 }}>Register</Link>
        <Link to="/dashboard" style={{ marginRight: 16 }}>Dashboard</Link>
        <Link to="/admin" style={{ marginRight: 16 }}>Admin</Link>
        <Link to="/export">Export</Link>
      </nav>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/admin" element={<Admin />} />
        <Route path="/export" element={<Export />} />
      </Routes>
    </BrowserRouter>
  )
}
