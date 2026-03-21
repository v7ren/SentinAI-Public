import { useAuth } from '../api'
import { Link } from 'react-router-dom'

export default function Dashboard() {
  const { user } = useAuth()

  return (
    <>
      <h1 className="page-title">Dashboard</h1>
      <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
        Welcome back, {user?.username}.
      </p>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '1rem' }}>
        <Link to="/profiles" className="card" style={{ textDecoration: 'none', color: 'inherit' }}>
          <h3 style={{ margin: '0 0 0.5rem' }}>Profiles</h3>
          <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.9rem' }}>Manage your profiles</p>
        </Link>
        <Link to="/search" className="card" style={{ textDecoration: 'none', color: 'inherit' }}>
          <h3 style={{ margin: '0 0 0.5rem' }}>Search</h3>
          <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.9rem' }}>Search profiles</p>
        </Link>
        <Link to="/upload" className="card" style={{ textDecoration: 'none', color: 'inherit' }}>
          <h3 style={{ margin: '0 0 0.5rem' }}>Upload</h3>
          <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.9rem' }}>Upload files</p>
        </Link>
        {user?.role === 'admin' && (
          <Link to="/admin" className="card" style={{ textDecoration: 'none', color: 'inherit' }}>
            <h3 style={{ margin: '0 0 0.5rem' }}>Admin</h3>
            <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.9rem' }}>User management</p>
          </Link>
        )}
      </div>
    </>
  )
}
