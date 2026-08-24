// In development, requests go to /api/* which Vite proxies to the
// FastAPI backend (see vite.config.js). This avoids the browser making
// a real cross-origin request, so CORS cannot cause a false
// "could not reach the server" error.
//
// If you deploy the frontend and backend separately, set
// VITE_API_BASE_URL to the full backend URL (e.g. https://api.example.com)
// and requests will go there directly instead of through the proxy.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

const TOKEN_KEY = 'pkb_access_token'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
}

export function isAuthenticated() {
  return !!getToken()
}

class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.status = status
  }
}

async function request(path, { method = 'GET', body, isFormData = false } = {}) {
  const headers = {}
  const token = getToken()
  if (token) headers['Authorization'] = `Bearer ${token}`
  if (!isFormData && body !== undefined) headers['Content-Type'] = 'application/json'

  let response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers,
      body: isFormData ? body : body !== undefined ? JSON.stringify(body) : undefined,
    })
  } catch (err) {
    // This catch block ONLY runs for genuine network failures:
    // backend is down, DNS failure, no internet, etc. A CORS block
    // would also land here in a direct cross-origin setup, which is
    // exactly why we route through the Vite proxy instead — so this
    // message is reserved for real connectivity problems.
    throw new ApiError('Could not reach the server. Please check your connection.', 0)
  }

  // Try to parse a JSON body regardless of status code, since FastAPI
  // returns JSON error bodies (e.g. {"detail": "..."}) for 4xx/5xx too.
  let data = null
  try {
    data = await response.json()
  } catch {
    // Response had no JSON body (e.g. some 204/500 responses) — fine.
  }

  if (!response.ok) {
    // Surface the ACTUAL backend error message for real HTTP errors
    // (401, 403, 404, 422, 500, etc.) instead of the generic
    // "could not reach the server" message.
    let message = `Request failed (${response.status})`

    if (data?.detail) {
      // FastAPI validation errors (422) return detail as an array of
      // objects; everything else returns detail as a plain string.
      if (Array.isArray(data.detail)) {
        message = data.detail.map((d) => d.msg || JSON.stringify(d)).join('; ')
      } else {
        message = data.detail
      }
    }

    throw new ApiError(message, response.status)
  }

  return data
}

// ---- Auth ----
export function login(email, password) {
  return request('/auth/login', { method: 'POST', body: { email, password } })
}

export function register(username, email, password) {
  return request('/auth/register', { method: 'POST', body: { username, email, password } })
}

export function getMe() {
  return request('/auth/me')
}

// ---- Documents ----
export function uploadDocument(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request('/documents/upload', { method: 'POST', body: formData, isFormData: true })
}

export function listDocuments() {
  return request('/documents')
}

export function getDocument(documentId) {
  return request(`/documents/${documentId}`)
}

export function deleteDocument(documentId) {
  return request(`/documents/${documentId}`, { method: 'DELETE' })
}

// ---- Search ----
export function search(query, topK = 5) {
  return request('/search', { method: 'POST', body: { query, top_k: topK } })
}

export { ApiError }