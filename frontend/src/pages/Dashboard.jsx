import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import Nav from '../components/Nav.jsx'
import '../styles/dashboard.css'
import { listDocuments, getMe, ApiError } from '../api/client'

function formatDate(isoString) {
  if (!isoString) return ''
  try {
    return new Date(isoString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  } catch {
    return isoString
  }
}

function FileIcon({ type }) {
  const t = (type || '').toLowerCase()
  const label = t === 'pdf' ? '📄' : t === 'docx' ? '📝' : t.startsWith('ppt') ? '📊' : '📃'
  return <span className="file-icon-sm">{label}</span>
}

function Dashboard() {
  const [documents, setDocuments] = useState([])
  const [username, setUsername] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
   Promise.all([listDocuments({ limit: 100 }), getMe().catch(() => null)])
      .then(([docsResponse, me]) => {
        setDocuments(docsResponse.documents)
        if (me?.username) setUsername(me.username)
      })
      .catch((err) =>
        setError(err instanceof ApiError ? err.message : 'Could not load your documents.')
      )
      .finally(() => setLoading(false))
  }, [])

  const totalChunks = documents.reduce((sum, d) => sum + (d.chunk_count || 0), 0)
  const recentDocuments = documents.slice(0, 5)

  const greeting = (() => {
    const h = new Date().getHours()
    if (h < 12) return 'Good morning'
    if (h < 18) return 'Good afternoon'
    return 'Good evening'
  })()

  return (
    <div className="dashboard-page">
      <Nav />

      <div className="dashboard-hero">
        <div className="dashboard-hero-glow" />
        <div className="dashboard-hero-content animate-in">
          <div className="dashboard-hero-eyebrow">Your knowledge base</div>
          <h1>
            {greeting}{username ? `, ${username}` : ''} <span className="wave">👋</span>
          </h1>
          <p>Your personal knowledge, organized and searchable.</p>
          <div className="dashboard-hero-actions">
            <Link to="/upload" className="btn-gradient dashboard-hero-btn">Upload Document</Link>
            <Link to="/search" className="btn-outline dashboard-hero-btn dashboard-hero-btn-light">Search Knowledge</Link>
          </div>
        </div>
      </div>

      <div className="dashboard-content">
        {error && <div className="dashboard-error animate-in">{error}</div>}

        <div className="dashboard-stats animate-in" style={{ animationDelay: '40ms' }}>
          <div className="stat-card">
            <div className="stat-icon">▤</div>
            <div>
              <div className="stat-value">{loading ? <span className="skeleton" style={{ width: 32, height: 26, display: 'inline-block' }} /> : documents.length}</div>
              <div className="stat-label">Documents</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">◆</div>
            <div>
              <div className="stat-value">{loading ? <span className="skeleton" style={{ width: 32, height: 26, display: 'inline-block' }} /> : totalChunks}</div>
              <div className="stat-label">Indexed chunks</div>
            </div>
          </div>
        </div>

        <div className="dashboard-grid animate-in" style={{ animationDelay: '80ms' }}>
          <Link to="/upload" className="dashboard-card">
            <div className="dashboard-card-icon">↑</div>
            <h2>Upload Documents</h2>
            <p>Add PDFs, notes, or slides to your knowledge base.</p>
            <span className="dashboard-card-arrow">→</span>
          </Link>

          <Link to="/documents" className="dashboard-card">
            <div className="dashboard-card-icon">▤</div>
            <h2>My Documents</h2>
            <p>Browse and manage everything you've uploaded.</p>
            <span className="dashboard-card-arrow">→</span>
          </Link>

          <Link to="/search" className="dashboard-card">
            <div className="dashboard-card-icon">⌕</div>
            <h2>Search</h2>
            <p>Ask a question and search across your documents.</p>
            <span className="dashboard-card-arrow">→</span>
          </Link>
        </div>

        <div className="dashboard-recent animate-in" style={{ animationDelay: '120ms' }}>
          <div className="dashboard-recent-header">
            <h2>Recent documents</h2>
            <Link to="/documents" className="dashboard-recent-link">View all →</Link>
          </div>

          {loading ? (
            <div className="dashboard-recent-list">
              {[0, 1].map((i) => (
                <div key={i} className="dashboard-recent-row">
                  <div className="skeleton" style={{ width: '40%', height: 16 }} />
                </div>
              ))}
            </div>
          ) : recentDocuments.length === 0 ? (
            <div className="dashboard-recent-empty">
              You haven't uploaded any documents yet.{' '}
              <Link to="/upload">Upload your first document</Link>.
            </div>
          ) : (
            <div className="dashboard-recent-list">
              {recentDocuments.map((doc) => (
                <div key={doc.document_id} className="dashboard-recent-row">
                  <div className="dashboard-recent-row-main">
                    <FileIcon type={doc.file_type} />
                    <div>
                      <div className="doc-name">{doc.filename}</div>
                      <div className="doc-meta">
                        Uploaded {formatDate(doc.uploaded_at)} · {doc.chunk_count} chunks
                      </div>
                    </div>
                  </div>
                  <div className="doc-type">{doc.file_type}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard