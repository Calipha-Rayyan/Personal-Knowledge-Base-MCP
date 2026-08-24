import { useEffect, useState } from 'react'
import '../styles/documents.css'
import { listDocuments, deleteDocument, ApiError } from '../api/client'

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

function MyDocuments() {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadDocuments = () => {
    setLoading(true)
    setError('')
    listDocuments()
      .then((data) => setDocuments(data))
      .catch((err) =>
        setError(err instanceof ApiError ? err.message : 'Could not load documents.')
      )
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    loadDocuments()
  }, [])

  const handleDelete = async (documentId) => {
    try {
      await deleteDocument(documentId)
      setDocuments((prev) => prev.filter((d) => d.document_id !== documentId))
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not delete document.')
    }
  }

  return (
    <div className="documents-page">
      <div className="documents-header">
        <h1>My Documents</h1>
        <div className="subtitle">Everything you've uploaded to your knowledge base.</div>
      </div>

      {error && <div className="documents-error">{error}</div>}

      {loading ? (
        <div className="documents-empty">Loading your documents…</div>
      ) : documents.length === 0 ? (
        <div className="documents-empty">You haven't uploaded any documents yet.</div>
      ) : (
        <div className="documents-list">
          {documents.map((doc) => (
            <div key={doc.document_id} className="documents-row">
              <div>
                <div className="doc-name">{doc.filename}</div>
                <div className="doc-meta">Uploaded {formatDate(doc.uploaded_at)}</div>
              </div>
              <div className="documents-row-actions">
                <div className="doc-type">{doc.file_type}</div>
                <button
                  className="doc-delete"
                  onClick={() => handleDelete(doc.document_id)}
                  aria-label={`Delete ${doc.filename}`}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default MyDocuments
