import { useState, useEffect } from 'react'
import { getDocuments } from '../services/api'
import '../styles/documents.css'

function MyDocuments() {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getDocuments()
      .then((docs) => setDocuments(docs))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="documents-page">
      <div className="documents-header">
        <h1>My Documents</h1>
        <div className="subtitle">Everything you've uploaded to your knowledge base.</div>
      </div>

      {loading ? (
        <div className="documents-empty">Loading your documents...</div>
      ) : documents.length === 0 ? (
        <div className="documents-empty">You haven't uploaded any documents yet.</div>
      ) : (
        <div className="documents-list">
          {documents.map((doc) => (
            <div key={doc.id} className="documents-row">
              <div>
                <div className="doc-name">{doc.name}</div>
                <div className="doc-meta">Uploaded {doc.uploaded}</div>
              </div>
              <div className="doc-type">{doc.type}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default MyDocuments