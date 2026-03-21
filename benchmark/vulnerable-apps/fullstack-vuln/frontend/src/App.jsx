import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './api'
import Layout from './Layout'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Profiles from './pages/Profiles'
import ProfileEdit from './pages/ProfileEdit'
import Search from './pages/Search'
import Upload from './pages/Upload'
import Admin from './pages/Admin'

function PrivateRoute({ children }) {
  const { user } = useAuth()
  if (!user) return <Navigate to="/login" replace />
  return children
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/" element={<Layout />}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
            <Route path="profiles" element={<PrivateRoute><Profiles /></PrivateRoute>} />
            <Route path="profiles/new" element={<PrivateRoute><ProfileEdit /></PrivateRoute>} />
            <Route path="profiles/:id/edit" element={<PrivateRoute><ProfileEdit /></PrivateRoute>} />
            <Route path="search" element={<Search />} />
            <Route path="upload" element={<PrivateRoute><Upload /></PrivateRoute>} />
            <Route path="admin" element={<PrivateRoute><Admin /></PrivateRoute>} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
