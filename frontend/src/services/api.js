// Mock API service layer.
// Mimics the real backend contract so pages work end-to-end today.
// TODO: Replace each function body with a real fetch() call once
// Member 3's endpoints are live. Keep the function names/signatures
// the same so no page code needs to change.

const DELAY_MS = 500

function delay(data) {
  return new Promise((resolve) => setTimeout(() => resolve(data), DELAY_MS))
}

function getStoredDocuments() {
  const raw = localStorage.getItem('pkb_documents')
  return raw ? JSON.parse(raw) : []
}

function saveStoredDocuments(docs) {
  localStorage.setItem('pkb_documents', JSON.stringify(docs))
}

// POST /auth/login
export async function login(email, password) {
  if (!email || !password) {
    throw new Error('Email and password are required')
  }
  return delay({ token: 'mock-token', user: { email } })
}

// POST /documents/upload
export async function uploadDocument(file) {
  const docs = getStoredDocuments()
  const newDoc = {
    id: Date.now(),
    name: file.name,
    type: file.name.split('.').pop().toUpperCase(),
    uploaded: new Date().toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    }),
  }
  docs.unshift(newDoc)
  saveStoredDocuments(docs)
  return delay(newDoc)
}

// GET /documents
export async function getDocuments() {
  return delay(getStoredDocuments())
}

// GET /documents/{id}
export async function getDocument(id) {
  const docs = getStoredDocuments()
  const doc = docs.find((d) => d.id === Number(id))
  if (!doc) throw new Error('Document not found')
  return delay(doc)
}

// POST /search
export async function searchDocuments(query) {
  const docs = getStoredDocuments()
  if (docs.length === 0) return delay([])

  const results = docs.map((doc) => ({
    id: doc.id,
    source: doc.name,
    snippet: `Mock result: this is a simulated snippet from "${doc.name}" relevant to "${query}".`,
  }))
  return delay(results)
}