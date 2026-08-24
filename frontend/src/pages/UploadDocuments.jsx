import { useState } from 'react'
import { Link } from 'react-router-dom'
import '../styles/upload.css'
import { uploadDocument, ApiError } from '../api/client'

function UploadDocuments() {
  const [file, setFile] = useState(null)
  const [status, setStatus] = useState('idle') // idle | uploading | success | error
  const [error, setError] = useState('')

  const handleFileChange = (e) => {
    setFile(e.target.files[0] || null)
    setStatus('idle')
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) return

    setStatus('uploading')
    setError('')
    try {
      await uploadDocument(file)
      setStatus('success')
      setFile(null)
    } catch (err) {
      setStatus('error')
      setError(err instanceof ApiError ? err.message : 'Upload failed. Please try again.')
    }
  }

  return (
    <div className="upload-page">
      <div className="upload-header">
        <h1>Upload Documents</h1>
        <div className="subtitle">Add a PDF, TXT, MD, PPT, PPTX, or DOCX file to your knowledge base.</div>
      </div>

      {status === 'success' && (
        <div className="upload-success">
          Uploaded successfully. <Link to="/documents">View My Documents</Link>
        </div>
      )}
      {status === 'error' && <div className="upload-error">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className={`upload-dropzone ${file ? 'has-file' : ''}`}>
          <p>Choose a file to upload</p>
          <input
            type="file"
            accept=".pdf,.txt,.md,.ppt,.pptx,.docx"
            onChange={handleFileChange}
          />
          {file && <div className="upload-filename">Selected: {file.name}</div>}
        </div>

        <button type="submit" className="upload-button" disabled={!file || status === 'uploading'}>
          {status === 'uploading' ? 'Uploading…' : 'Upload'}
        </button>
      </form>
    </div>
  )
}

export default UploadDocuments
