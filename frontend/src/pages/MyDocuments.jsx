import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import Nav from '../components/Nav.jsx'
import Modal from '../components/Modal.jsx'
import { useToast } from '../components/Toast.jsx'
import '../styles/documents.css'
import { listDocuments, deleteDocument, ApiError } from '../api/client'

const PAGE_SIZE = 10

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
  return <span className="file-icon">{label}</span>
}

function StatusBadge({ status, errorMessage }) {
  if (status === 'indexed') return <span className="status-badge status-indexed">Indexed</span>
  if (status === 'failed') return <span className="status-badge status-failed" title={errorMessage || ''}>Failed</span>
  if (status === 'processing') return <span className="status-badge status-processing"><span className="spinner" style={{ width: 10, height: 10, borderWidth: 1.5 }} /> Processing</span>
  return <span className="status-badge status-uploading">Uploading</span>
}

const FILE_TYPES = ['', 'pdf', 'txt', 'md', 'docx', 'ppt', 'pptx']

function MyDocuments() {
  const [documents, setDocuments] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(0)
  const [fileType, setFileType] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [refreshing, setRefreshing] = useState(false)
  const [pendingDelete, setPendingDelete] = useState(null)
  const [deleting, setDeleting] = useState(false)
  const toast = useToast()
  const pollTimer = useRef(null)

  const loadDocuments = (isRefresh = false) => {
    if (isRefresh) setRefreshing(true)
    else setLoading(true)
    setError('')
    return listDocuments({ limit: PAGE_SIZE, offset: page * PAGE_SIZE, fileType: fileType || undefined })
      .then((data) => {
        setDocuments(data.documents)
        setTotal(data.total)
        return data
      })
      .catch((err) => {
        setError(err instanceof ApiError ? err.message : 'Could not load documents.')
        return null
      })
      .finally(() => {
        setLoading(false)
        setRefreshing(false)
      })
  }

  useEffect(() => {
    loadDocuments()
    return () => clearTimeout(pollTimer.current)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, fileType])

  useEffect(() => {
    const hasInFlight = documents.some((d) => d.status === 'uploading' || d.status === 'processing')
    if (hasInFlight) {
      pollTimer.current = setTimeout(() => loadDocuments(), 2000)
    }
    return () => clearTimeout(pollTimer.current)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [documents])

  const confirmDelete = async () => {
    if (!pendingDelete) return
    setDeleting(true)
    try {
      await deleteDocument(pendingDelete.document_id)
      toast(`"${pendingDelete.filename}" deleted.`, 'success')
      setPendingDelete(null)
      loadDocuments(true)
    } catch (err) {
      toast(err instanceof ApiError ? err.message : 'Could not delete document.', 'error')
    } finally {
      setDeleting(false)
    }
  }

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  return (
    <div className="documents-page">
      <Nav />
      <div className="documents-content">
        <div className="documents-header animate-in">
          <div>
            <h1>My Documents</h1>
            <div className="subtitle">
              {loading ? 'Loading…' : `${total} document${total === 1 ? '' : 's'} in your knowledge base`}
            </div>
          </div>
          <div className="documents-header-actions">
            <select
              className="documents-filter-select"
              value={fileType}
              onChange={(e) => { setFileType(e.target.value); setPage(0) }}
            >
              {FILE_TYPES.map((t) => (
                <option key={t} value={t}>{t ? t.toUpperCase() : 'All types'}</option>
              ))}
            </select>
            <button
              className="btn-outline documents-refresh"
              onClick={() => loadDocuments(true)}
              disabled={refreshing}
            >
              {refreshing ? <span className="spinner spinner-dark" /> : '⟳'} Refresh
            </button>
            <Link to="/upload" className="btn-gradient documents-upload-btn">
              + Upload
            </Link>
          </div>
        </div>

        {error && <div className="documents-error animate-in">{error}</div>}

        {loading ? (
          <div className="documents-list">
            {[0, 1, 2].map((i) => (
              <div key={i} className="documents-row">
                <div className="skeleton" style={{ width: '40%', height: 16 }} />
                <div className="skeleton" style={{ width: 60, height: 20 }} />
              </div>
            ))}
          </div>
        ) : documents.length === 0 ? (
          <div className="documents-empty animate-in">
            <div className="documents-empty-icon">▤</div>
            <h2>{fileType ? `No ${fileType.toUpperCase()} documents` : 'No documents yet'}</h2>
            <p>
              {fileType
                ? 'Try a different filter, or upload one.'
                : 'Upload your first document to start building your knowledge base.'}
            </p>
            <Link to="/upload" className="btn-gradient documents-empty-btn">
              Upload a document
            </Link>
          </div>
        ) : (
          <>
            <div className="documents-list">
              {documents.map((doc, idx) => (
                <div
                  key={doc.document_id}
                  className="documents-row animate-in"
                  style={{ animationDelay: `${idx * 40}ms` }}
                >
                  <div className="documents-row-main">
                    <FileIcon type={doc.file_type} />
                    <div>
                      <div className="doc-name">{doc.filename}</div>
                      <div className="doc-meta">
                        Uploaded {formatDate(doc.uploaded_at)}
                        {doc.status === 'indexed' && ` · ${doc.chunk_count} chunks`}
                        {doc.status === 'failed' && doc.error_message && (
                          <span className="doc-meta-error"> · {doc.error_message}</span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="documents-row-actions">
                    <StatusBadge status={doc.status} errorMessage={doc.error_message} />
                    <span className="doc-type">{doc.file_type}</span>
                    {doc.status === 'indexed' && (
                        <>
                          <Link to={`/documents/${doc.document_id}`} className="doc-action-btn" title="View">
                            👁
                          </Link>
                          <Link
                            to={`/search-results?q=${encodeURIComponent(doc.filename)}`}
                            className="doc-action-btn"
                            title="Search this document"
                          >
                            ⌕
                          </Link>
                        </>
                      )}
                    <button
                      className="doc-action-btn doc-action-danger"
                      onClick={() => setPendingDelete(doc)}
                      aria-label={`Delete ${doc.filename}`}
                      title="Delete"
                    >
                      🗑
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {totalPages > 1 && (
              <div className="documents-pagination">
                <button
                  className="btn-outline documents-page-btn"
                  onClick={() => setPage((p) => Math.max(0, p - 1))}
                  disabled={page === 0}
                >
                  ← Previous
                </button>
                <span className="documents-page-label">
                  Page {page + 1} of {totalPages}
                </span>
                <button
                  className="btn-outline documents-page-btn"
                  onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                  disabled={page >= totalPages - 1}
                >
                  Next →
                </button>
              </div>
            )}
          </>
        )}
      </div>

      <Modal
        open={!!pendingDelete}
        title="Delete document?"
        description={pendingDelete ? `"${pendingDelete.filename}" and all of its indexed chunks will be permanently removed. This action cannot be undone.` : ''}
        confirmLabel="Delete"
        danger
        loading={deleting}
        onConfirm={confirmDelete}
        onCancel={() => setPendingDelete(null)}
      />
    </div>
  )
}

export default MyDocuments