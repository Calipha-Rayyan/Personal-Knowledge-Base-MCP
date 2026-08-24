import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { uploadDocument } from '../services/api'
import '../styles/upload.css'

function UploadDocuments() {
  const [file, setFile] = useState(null)
  const [status, setStatus] = useState('idle') // idle | uploading | success | error
  const [errorMsg, setErrorMsg] = useState('')
  const navigate = useNavigate()

  const handleFileChange = (e) => {
    setFile(e.target.files[0] || null)
    setStatus('idle')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) return

    setStatus('uploading')
    setErrorMsg('')

    try {
      await uploadDocument(file)
      setStatus('success')
      setTimeout(() => navigate('/documents'), 800)
    } catch (err) {
      setStatus('error')
      setErrorMsg(err.message || 'Upload failed. Please try again.')
    }
  }

  return (
    <div className="upload-page">
      <div className="upload-header">
        <h1>Upload Documents</h1>
        <div className="subtitle">Add a PDF, TXT, MD, PPT, PPTX, or DOCX file to your knowledge base.</div>
      </div>

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
          {status === 'uploading' ? 'Uploading...' : 'Upload'}
        </button>

        {status === 'success' && (
          <div className="upload-filename">Upload successful! Redirecting...</div>
        )}
        {status === 'error' && (
          <div className="upload-filename" style={{ color: 'var(--error)' }}>{errorMsg}</div>
        )}
      </form>
    </div>
  )
}

export default UploadDocuments