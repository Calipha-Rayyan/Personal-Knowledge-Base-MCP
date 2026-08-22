import '../styles/documents.css'

const mockDocuments = [
  { id: 1, name: 'OOP_Course_Breakup.pdf', type: 'PDF', uploaded: 'Aug 12, 2026' },
  { id: 2, name: 'Data_Structures_Notes.docx', type: 'DOCX', uploaded: 'Aug 10, 2026' },
  { id: 3, name: 'Project_Plan.md', type: 'MD', uploaded: 'Aug 8, 2026' },
]

function MyDocuments() {
  const documents = mockDocuments

  return (
    <div className="documents-page">
      <div className="documents-header">
        <h1>My Documents</h1>
        <div className="subtitle">Everything you've uploaded to your knowledge base.</div>
      </div>

      {documents.length === 0 ? (
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