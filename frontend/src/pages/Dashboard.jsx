import { Link, useNavigate } from 'react-router-dom'
import '../styles/dashboard.css'
import { clearToken } from '../api/client'

function Dashboard() {
  const navigate = useNavigate()

  const handleLogout = () => {
    clearToken()
    navigate('/')
  }

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <div>
          <h1>Your Knowledge Base</h1>
          <div className="subtitle">Upload, browse, and search your documents.</div>
        </div>
        <button className="logout-button" onClick={handleLogout}>
          Log out
        </button>
      </div>

      <div className="dashboard-grid">
        <Link to="/upload" className="dashboard-card">
          <h2>Upload Documents</h2>
          <p>Add PDFs, notes, or slides to your knowledge base.</p>
        </Link>

        <Link to="/documents" className="dashboard-card">
          <h2>My Documents</h2>
          <p>Browse and manage everything you've uploaded.</p>
        </Link>

        <Link to="/search" className="dashboard-card">
          <h2>Search</h2>
          <p>Ask a question and search across your documents.</p>
        </Link>
      </div>
    </div>
  )
}

export default Dashboard
