import { useEffect } from 'react'
import { Routes, Route, useNavigate } from 'react-router-dom'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import ForgotPassword from './pages/ForgotPassword.jsx'
import ResetPassword from './pages/ResetPassword.jsx'
import Dashboard from './pages/Dashboard.jsx'
import UploadDocuments from './pages/UploadDocuments.jsx'
import MyDocuments from './pages/MyDocuments.jsx'
import DocumentView from './pages/DocumentView.jsx'
import Search from './pages/Search.jsx'
import SearchResults from './pages/SearchResults.jsx'
import Settings from './pages/Settings.jsx'
import RequireAuth from './components/RequireAuth.jsx'
import { onSessionExpired } from './api/client'

function App() {
  const navigate = useNavigate()

  useEffect(() => {
    const unsubscribe = onSessionExpired(() => {
      navigate('/', { replace: true })
    })
    return unsubscribe
  }, [navigate])

  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/reset-password" element={<ResetPassword />} />
      <Route path="/dashboard" element={<RequireAuth><Dashboard /></RequireAuth>} />
      <Route path="/upload" element={<RequireAuth><UploadDocuments /></RequireAuth>} />
      <Route path="/documents" element={<RequireAuth><MyDocuments /></RequireAuth>} />
      <Route path="/documents/:documentId" element={<RequireAuth><DocumentView /></RequireAuth>} />
      <Route path="/search" element={<RequireAuth><Search /></RequireAuth>} />
      <Route path="/search-results" element={<RequireAuth><SearchResults /></RequireAuth>} />
      <Route path="/settings" element={<RequireAuth><Settings /></RequireAuth>} />
    </Routes>
  )
}

export default App