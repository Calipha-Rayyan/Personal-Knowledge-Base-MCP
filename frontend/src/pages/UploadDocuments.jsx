import { useCallback, useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import Nav from '../components/Nav.jsx'
import { useToast } from '../components/Toast.jsx'
import '../styles/upload.css'
import { uploadDocument, listDocuments, ApiError } from '../api/client'

const ALLOWED = ['.pdf', '.txt', '.md', '.ppt', '.pptx', '.docx']
const MAX_MB = 25
const POLL_INTERVAL_MS = 1500
const POLL_TIMEOUT_MS = 60000

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function UploadDocuments() {
  const [file, setFile] = useState(null)
  const [dragOver, setDragOver] = useState(false)
  // idle | uploading | processing | success | error
  const [status, setStatus] = useState('idle')
  const [error, setError] = useState('')
  const toast = useToast()
  const pollTimer = useRef(null)

  useEffect(() => () => clearTimeout(pollTimer.current), [])

  const validateAndSet = (f) => {
    if (!f) return
    const ext = '.' + f.name.split('.').pop().toLowerCase()
    if (!ALLOWED.includes(ext)) {
      setError(`"${ext}" isn't supported. Allowed: ${ALLOWED.join(', ')}`)
      setStatus('error')
      return
    }
    if (f.size > MAX_MB * 1024 * 1024) {
      setError(`File exceeds the ${MAX_MB}MB limit.`)
      setStatus('error')
      return
    }
    setFile(f)
    setStatus('idle')
    setError('')
  }

  const handleFileChange = (e) => validateAndSet(e.target.files[0] || null)

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setDragOver(false)
    validateAndSet(e.dataTransfer.files[0] || null)
  }, [])

  // Polls GET /documents (rather than needing a new endpoint) to find
  // this document's current status, since the upload response only
  // reflects the initial "uploading" state before background
  // processing has had a chance to run.
  const pollUntilDone = (documentId, startedAt) => {
    listDocuments()
      .then((docs) => {
        const doc = docs.find((d) => d.document_id === documentId)
        if (!doc) return

        if (doc.status === 'indexed') {
          setStatus('success')
          toast(`"${doc.filename}" uploaded and indexed successfully.`, 'success')
          return
        }
        if (doc.status === 'failed') {
          setStatus('error')
          setError(doc.error_message || 'Processing failed.')
          toast(doc.error_message || 'Document processing failed.', 'error')
          return
        }

        if (Date.now() - startedAt > POLL_TIMEOUT_MS) {
          setStatus('error')
          setError('Processing is taking longer than expected. Check My Documents shortly.')
          return
        }

        pollTimer.current = setTimeout(() => pollUntilDone(documentId, startedAt), POLL_INTERVAL_MS)
      })
      .catch(() => {
        pollTimer.current = setTimeout(() => pollUntilDone(documentId, startedAt), POLL_INTERVAL_MS)
      })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) return
    setStatus('uploading')
    setError('')
    try {
      const result = await uploadDocument(file)
      setStatus('processing')
      pollUntilDone(result.document_id, Date.now())
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : 'Upload failed. Please try again.'
      setError(msg)
      setStatus('error')
      toast(msg, 'error')
    }
  }

  const reset = () => {
    clearTimeout(pollTimer.current)
    setFile(null)
    setStatus('idle')
    setError('')
  }

  return (
    <div className="upload-page">
      <Nav />
      <div className="upload-content">
        <div className="upload-header animate-in">
          <h1>Upload Documents</h1>
          <div className="subtitle">Add a PDF, TXT, MD, PPT, PPTX, or DOCX file to your knowledge base.</div>
        </div>

        {status === 'success' ? (
          <div className="upload-success-card animate-scale-in">
            <div className="upload-success-check">✓</div>
            <h2>Document uploaded successfully</h2>
            <p>{file?.name} has been processed and indexed.</p>
            <div className="upload-success-actions">
              <Link to="/documents" className="btn-gradient upload-success-btn">View Documents</Link>
              <button className="btn-outline upload-success-btn" onClick={reset}>Upload another</button>
            </div>
          </div>
        ) : status === 'processing' ? (
          <div className="upload-success-card animate-scale-in">
            <div className="upload-processing-spinner">
              <span className="spinner" style={{ width: 28, height: 28, borderWidth: 3 }} />
            </div>
            <h2>Processing your document…</h2>
            <p>{file?.name} is being extracted, chunked, and indexed. This usually takes a few seconds.</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="animate-in" style={{ animationDelay: '60ms' }}>
            {error && <div className="upload-error">{error}</div>}

            <div
              className={`upload-dropzone ${file ? 'has-file' : ''} ${dragOver ? 'drag-over' : ''}`}
              onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
            >
              {file ? (
                <div className="upload-file-preview">
                  <div className="upload-file-icon">📄</div>
                  <div className="upload-file-info">
                    <div className="upload-file-name">{file.name}</div>
                    <div className="upload-file-size">{formatSize(file.size)}</div>
                  </div>
                  <button type="button" className="upload-file-remove" onClick={reset} aria-label="Remove file">
                    ✕
                  </button>
                </div>
              ) : (
                <>
                  <div className="upload-dropzone-icon">↑</div>
                  <p className="upload-dropzone-title">Drag & drop your document here</p>
                  <p className="upload-dropzone-sub">or browse your computer</p>
                  <label className="btn-outline upload-browse-btn">
                    Browse files
                    <input type="file" accept={ALLOWED.join(',')} onChange={handleFileChange} hidden />
                  </label>
                  <div className="upload-dropzone-formats">
                    PDF · TXT · MD · DOCX · PPT · PPTX &nbsp;·&nbsp; Max {MAX_MB}MB
                  </div>
                </>
              )}
            </div>

            <button type="submit" className="btn-gradient upload-button" disabled={!file || status === 'uploading'}>
              {status === 'uploading' ? (
                <>
                  <span className="spinner" /> Uploading…
                </>
              ) : (
                'Upload Document'
              )}
            </button>
          </form>
        )}
      </div>
    </div>
  )
}

export default UploadDocuments