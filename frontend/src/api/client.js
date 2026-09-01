const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

const ACCESS_TOKEN_KEY = 'pkb_access_token'
const REFRESH_TOKEN_KEY = 'pkb_refresh_token'

export function getToken() {
  return localStorage.getItem(ACCESS_TOKEN_KEY)
}

export function getRefreshToken() {
  return localStorage.getItem(REFRESH_TOKEN_KEY)
}

export function setTokens({ access_token, refresh_token }) {
  if (access_token) localStorage.setItem(ACCESS_TOKEN_KEY, access_token)
  if (refresh_token) localStorage.setItem(REFRESH_TOKEN_KEY, refresh_token)
}

export function setToken(accessToken) {
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken)
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
}

export function clearToken() {
  clearTokens()
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

const SESSION_EXPIRED_EVENT = 'pkb:session-expired'

// Endpoints where a 401 means "these credentials/inputs were wrong",
// NOT "your previously-valid session has expired". These are called
// without an existing session, so there is no session to have expired —
// misclassifying them was the bug that showed "Your session has
// expired" on a plain wrong-password login attempt.
const AUTH_ENDPOINTS_WITHOUT_SESSION = ['/auth/login', '/auth/register', '/auth/refresh']

let refreshInFlight = null

async function doRefresh() {
  const refreshToken = getRefreshToken()
  if (!refreshToken) return false

  try {
    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    })
    if (!response.ok) return false

    const data = await response.json()
    setTokens({ access_token: data.access_token, refresh_token: data.refresh_token })
    return true
  } catch {
    return false
  }
}

async function rawRequest(path, { method, headers, body }) {
  return fetch(`${API_BASE_URL}${path}`, { method, headers, body })
}

function extractErrorMessage(data, fallback) {
  if (data?.detail) {
    return Array.isArray(data.detail)
      ? data.detail.map((d) => d.msg || JSON.stringify(d)).join('; ')
      : data.detail
  }
  return fallback
}

async function request(path, { method = 'GET', body, isFormData = false, _isRetry = false } = {}) {
  const headers = {}
  const token = getToken()
  if (token) headers['Authorization'] = `Bearer ${token}`
  if (!isFormData && body !== undefined) headers['Content-Type'] = 'application/json'

  const requestBody = isFormData ? body : body !== undefined ? JSON.stringify(body) : undefined

  let response
  try {
    response = await rawRequest(path, { method, headers, body: requestBody })
  } catch (err) {
    throw new ApiError('Could not reach the server. Please check your connection.', 0)
  }

  const isSessionlessAuthCall = AUTH_ENDPOINTS_WITHOUT_SESSION.includes(path)

  // Only attempt a silent refresh / treat 401 as "session expired" for
  // requests that were actually using a session (i.e. sent a bearer
  // token for a protected route). A 401 from /auth/login itself just
  // means the credentials were wrong — handled below with the real
  // backend message instead.
  if (response.status === 401 && !_isRetry && !isSessionlessAuthCall) {
    if (!refreshInFlight) {
      refreshInFlight = doRefresh().finally(() => {
        refreshInFlight = null
      })
    }
    const refreshed = await refreshInFlight

    if (refreshed) {
      return request(path, { method, body, isFormData, _isRetry: true })
    }

    clearTokens()
    window.dispatchEvent(new CustomEvent(SESSION_EXPIRED_EVENT))
    throw new ApiError('Your session has expired. Please log in again.', 401)
  }

  let data = null
  try {
    data = await response.json()
  } catch {
    // no JSON body
  }

  if (!response.ok) {
    // For login/register/refresh, a 401/400 is a normal validation
    // outcome (wrong credentials) — surface the backend's actual
    // message, never the "session expired" framing.
    if (isSessionlessAuthCall) {
      throw new ApiError(extractErrorMessage(data, `Request failed (${response.status})`), response.status)
    }

    if (response.status === 401) {
      clearTokens()
      window.dispatchEvent(new CustomEvent(SESSION_EXPIRED_EVENT))
      throw new ApiError('Your session has expired. Please log in again.', 401)
    }

    let message = extractErrorMessage(data, `Request failed (${response.status})`)
    if (!data?.detail) {
      if (response.status === 403) message = "You don't have permission to do that."
      else if (response.status === 404) message = 'Not found.'
      else if (response.status === 429) message = 'Too many attempts. Please wait a moment and try again.'
      else if (response.status === 500) message = 'Something went wrong on the server. Please try again.'
    }

    throw new ApiError(message, response.status)
  }

  return data
}

export function onSessionExpired(callback) {
  window.addEventListener(SESSION_EXPIRED_EVENT, callback)
  return () => window.removeEventListener(SESSION_EXPIRED_EVENT, callback)
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

export function changePassword(currentPassword, newPassword) {
  return request('/auth/change-password', {
    method: 'POST',
    body: { current_password: currentPassword, new_password: newPassword },
  })
}

export async function logout() {
  const refreshToken = getRefreshToken()
  clearTokens()
  if (refreshToken) {
    try {
      await rawRequest('/auth/logout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      })
    } catch {
      // Token is already cleared client-side.
    }
  }
}

// ---- Documents ----
export function uploadDocument(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request('/documents/upload', { method: 'POST', body: formData, isFormData: true })
}

export function listDocuments({ limit = 20, offset = 0, fileType, status } = {}) {
  const params = new URLSearchParams()
  params.set('limit', limit)
  params.set('offset', offset)
  if (fileType) params.set('file_type', fileType)
  if (status) params.set('status', status)
  return request(`/documents?${params.toString()}`)
}

export function getDocument(documentId) {
  return request(`/documents/${documentId}`)
}

export function deleteDocument(documentId) {
  return request(`/documents/${documentId}`, { method: 'DELETE' })
}

// ---- Search ----
export function search(query, { topK = 5, fileType, documentId } = {}) {
  return request('/search', {
    method: 'POST',
    body: { query, top_k: topK, file_type: fileType, document_id: documentId },
  })
}

export { ApiError }