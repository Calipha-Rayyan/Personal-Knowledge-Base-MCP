import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import Nav from '../components/Nav.jsx'
import '../styles/documentview.css'
import { getDocument, ApiError } from '../api/client'

function DocumentView() {
  const { documentId } = useParams()
  const navigate = useNavigate()
  const [doc, setDoc] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    setLoading(true)
    setError('')
    getDocument(documentId)
      .then(setDoc)
      .catch((err) => setError(err instanceof ApiError ? err.message : 'Could not load document.'))
      .finally(() => setLoading(false))
  }, [documentId])

  return (
    <div className="docview-page">
      <Nav />
      <div className="docview-content">
        <button className="docview-back" onClick={() => navigate('/documents')}>
          ← Back to Documents
        </button>

        {loading ? (
          <div className="docview-card animate-in">
            <div className="skeleton" style={{ width: '50%', height: 22, marginBottom: 16 }} />
            <div className="skeleton" style={{ width: '100%', height: 14, marginBottom: 8 }} />
            <div className="skeleton" style={{ width: '90%', height: 14, marginBottom: 8 }} />
            <div className="skeleton" style={{ width: '95%', height: 14 }} />
          </div>
        ) : error ? (
          <div className="docview-error animate-in">
            <h2>Couldn't load this document</h2>
            <p>{error}</p>
            <Link to="/documents" className="btn-gradient docview-error-btn">Back to Documents</Link>
          </div>
        ) : (
          <div className="docview-card animate-in">
            <div className="docview-header">
              <h1>{doc.filename}</h1>
              {doc.status && <span className={`status-badge status-${doc.status}`}>{doc.status}</span>}
            </div>

            {doc.status !== 'indexed' ? (
              <div className="docview-not-ready">
                {doc.status === 'failed'
                  ? `This document failed to process${doc.error_message ? `: ${doc.error_message}` : '.'}`
                  : 'This document is still being processed. Check back shortly.'}
              </div>
            ) : (
              <>
                <div className="docview-actions">
                  <Link
                    to={`/search-results?q=${encodeURIComponent(doc.filename)}`}
                    className="btn-outline docview-search-btn"
                  >
                    ⌕ Search within this document
                  </Link>
                </div>
                <div className="docview-body">
                  {doc.content ? (
                    doc.content.split('\n\n').map((para, i) => (
                      <p key={i}>{para}</p>
                    ))
                  ) : (
                    <p className="docview-empty">No extracted content available.</p>
                  )}
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default DocumentView