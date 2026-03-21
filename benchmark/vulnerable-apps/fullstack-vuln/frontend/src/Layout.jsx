import { Outlet } from 'react-router-dom'
import { useAuth } from './api'
import { Link } from 'react-router-dom'

export default function Layout() {
  const { user, logout } = useAuth()

  return (
    <div className="app">
      <div className="banner">
        WARNING: This application is for SAST benchmarking only. Do not deploy publicly or expose to the internet.
      </div>
      <nav className="nav">
        <Link to="/" className="nav-brand">Portal</Link>
        <div className="nav-links">
          {user ? (
            <>
              <Link to="/dashboard">Dashboard</Link>
              <Link to="/profiles">Profiles</Link>
              <Link to="/search">Search</Link>
              <Link to="/upload">Upload</Link>
              <Link to="/admin">Admin</Link>
              <button type="button" className="btn btn-ghost" onClick={logout}>Log out</button>
            </>
          ) : (
            <>
              <Link to="/search">Search</Link>
              <Link to="/login">Log in</Link>
              <Link to="/register">Register</Link>
            </>
          )}
        </div>
      </nav>
      <main className="main">
        <Outlet />
      </main>
    </div>
  )
}
