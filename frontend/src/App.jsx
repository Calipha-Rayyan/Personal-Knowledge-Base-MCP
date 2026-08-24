import { Routes, Route } from 'react-router-dom'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import Dashboard from './pages/Dashboard.jsx'
import UploadDocuments from './pages/UploadDocuments.jsx'
import MyDocuments from './pages/MyDocuments.jsx'
import Search from './pages/Search.jsx'
import SearchResults from './pages/SearchResults.jsx'
import RequireAuth from './components/RequireAuth.jsx'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        path="/dashboard"
        element={
          <RequireAuth>
            <Dashboard />
          </RequireAuth>
        }
      />
      <Route
        path="/upload"
        element={
          <RequireAuth>
            <UploadDocuments />
          </RequireAuth>
        }
      />
      <Route
        path="/documents"
        element={
          <RequireAuth>
            <MyDocuments />
          </RequireAuth>
        }
      />
      <Route
        path="/search"
        element={
          <RequireAuth>
            <Search />
          </RequireAuth>
        }
      />
      <Route
        path="/search-results"
        element={
          <RequireAuth>
            <SearchResults />
          </RequireAuth>
        }
      />
    </Routes>
  )
}

export default App
