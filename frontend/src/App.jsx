import { Routes, Route } from 'react-router-dom'
import Login from './pages/Login.jsx'
import Dashboard from './pages/Dashboard.jsx'
import UploadDocuments from './pages/UploadDocuments.jsx'
import MyDocuments from './pages/MyDocuments.jsx'
import Search from './pages/Search.jsx'
import SearchResults from './pages/SearchResults.jsx'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/upload" element={<UploadDocuments />} />
      <Route path="/documents" element={<MyDocuments />} />
      <Route path="/search" element={<Search />} />
      <Route path="/search-results" element={<SearchResults />} />
    </Routes>
  )
}

export default App