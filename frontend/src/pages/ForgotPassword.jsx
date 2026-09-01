import { useState } from 'react'
import { Link } from 'react-router-dom'
import '../styles/auth.css'
import { ApiError } from '../api/client'

async function requestPasswordReset(email) {
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'
  const response = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email }),
  })
  const data = await response.json().catch(() => null)
  if (!response.ok) {
    throw new ApiError(data?.detail || 'Something went wrong. Please try again.', response.status)
  }
  return data
}

function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [resetLink, setResetLink] = useState(null)
  const [submitted, setSubmitted] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const data = await requestPasswordReset(email)
      setResetLink(data.reset_link || null)
      setSubmitted(true)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleCopy = () => {
    if (!resetLink) return
    navigator.clipboard.writeText(resetLink).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  return (
    <div className="auth-page">
      <div className="auth-hero animate-in">
        <div className="auth-hero-glow" />
        <div className="auth-hero-mark" />
        <div className="auth-hero-content">
          <div className="auth-hero-eyebrow">Personal Knowledge Base</div>
          <h1>Forgot your<br />password?</h1>
          <p>No problem. Enter your email and we'll generate a link to reset it.</p>
        </div>
      </div>

      <div className="auth-form-panel">
        <div className="auth-card animate-scale-in">
          {submitted ? (
            <>
              <div className="auth-mark">
                {resetLink ? 'Reset link ready' : 'Request received'}
              </div>
              <h1>{resetLink ? 'Your reset link' : 'Check the details'}</h1>

              {resetLink ? (
                <>
                  <p className="auth-sub">
                    This project doesn't have an email service connected, so here's your reset link directly.
                    It expires in 30 minutes.
                  </p>
                  <div className="reset-link-box">
                    <code>{resetLink}</code>
                  </div>
                  <div className="reset-link-actions">
                    <button type="button" className="btn-outline reset-link-btn" onClick={handleCopy}>
                      {copied ? '✓ Copied' : 'Copy link'}
                    </button>
                    <Link to={resetLink.replace(window.location.origin, '')} className="btn-gradient reset-link-btn">
                      Open link
                    </Link>
                  </div>
                </>
              ) : (
                <p className="auth-sub">
                  If an account exists for <strong>{email}</strong>, a reset link has been generated for it.
                </p>
              )}

              <p className="auth-switch">
                <Link to="/">Back to Login</Link>
              </p>
            </>
          ) : (
            <>
              <div className="auth-mark">Reset password</div>
              <h1>Forgot your password?</h1>
              <p className="auth-sub">Enter the email associated with your account.</p>

              {error && <div className="auth-error animate-in">{error}</div>}

              <form onSubmit={handleSubmit} className="auth-form">
                <label htmlFor="email">Email</label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  autoComplete="email"
                />

                <button type="submit" className="btn-gradient auth-submit" disabled={loading}>
                  {loading ? <span className="spinner" /> : 'Generate reset link'}
                </button>
              </form>

              <p className="auth-switch">
                Remembered it? <Link to="/">Back to Login</Link>
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default ForgotPassword