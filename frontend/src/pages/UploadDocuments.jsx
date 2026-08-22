import { useState } from 'react'
import '../styles/upload.css'

function UploadDocuments() {
  const [file, setFile] = useState(null)

  const handleFileChange = (e) => {
    setFile(e.target.files[0] || null)
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    console.log('Upload attempt:', file)
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

        <button type="submit" className="upload-button" disabled={!file}>
          Upload
        </button>
      </form>
    </div>
  )
}

export default UploadDocuments