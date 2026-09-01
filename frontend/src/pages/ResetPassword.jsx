import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import '../styles/auth.css'
import { ApiError } from '../api/client'

function passwordChecks(pw) {
  return {
    length: pw.length >= 8,
    upper: /[A-Z]/.test(pw),
    lower: /[a-z]/.test(pw),
    number: /[0-9]/.test(pw),
    special: /[^A-Za-z0-9]/.test(pw),
  }
}

async function submitReset(token, newPassword) {
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'
  const response = await fetch(`${API_BASE_URL}/auth/reset-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token, new_password: newPassword }),
  })
  const data = await response.json().catch(() => null)
  if (!response.ok) {
    throw new ApiError(data?.detail || 'This reset link is invalid or has expired.', response.status)
  }
  return data
}

function ResetPassword() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token') || ''
  const navigate = useNavigate()

  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)

  const checks = passwordChecks(password)
  const allMet = Object.values(checks).every(Boolean)
  const passwordsMatch = password && password === confirmPassword

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!allMet) {
      setError('Please meet all password requirements.')
      return
    }
    if (!passwordsMatch) {
      setError('Passwords do not match.')
      return
    }
    setError('')
    setLoading(true)
    try {
      await submitReset(token, password)
      setSuccess(true)
      setTimeout(() => navigate('/'), 2500)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  if (!token) {
    return (
      <div className="auth-page">
        <div className="auth-form-panel" style={{ flex: 1, width: '100%' }}>
          <div className="auth-card animate-scale-in">
            <div className="auth-mark">Invalid link</div>
            <h1>Missing reset token</h1>
            <p className="auth-sub">This reset link is missing its token. Please request a new one.</p>
            <Link to="/forgot-password" className="btn-gradient auth-submit" style={{ display: 'flex', justifyContent: 'center', textDecoration: 'none' }}>
              Request new link
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="auth-page">
      <div className="auth-hero animate-in">
        <div className="auth-hero-glow" />
        <div className="auth-hero-mark" />
        <div className="auth-hero-content">
          <div className="auth-hero-eyebrow">Personal Knowledge Base</div>
          <h1>Choose a new<br />password.</h1>
          <p>Make it strong — you'll be signed out of other devices once it's changed.</p>
        </div>
      </div>

      <div className="auth-form-panel">
        <div className="auth-card animate-scale-in">
          {success ? (
            <>
              <div className="auth-mark">Success</div>
              <h1>Password reset</h1>
              <p className="auth-sub">Your password has been changed. Redirecting you to login…</p>
            </>
          ) : (
            <>
              <div className="auth-mark">Reset password</div>
              <h1>Choose a new password</h1>
              <p className="auth-sub">Enter and confirm your new password below.</p>

              {error && <div className="auth-error animate-in">{error}</div>}

              <form onSubmit={handleSubmit} className="auth-form">
                <label htmlFor="password">New password</label>
                <div className="auth-password-field">
                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    autoComplete="new-password"
                  />
                  <button
                    type="button"
                    className="auth-password-toggle"
                    onClick={() => setShowPassword((s) => !s)}
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? '🙈' : '👁'}
                  </button>
                </div>

                {password && (
                  <div className="auth-requirements">
                    <span className={checks.length ? 'met' : ''}>{checks.length ? '✓' : '○'} 8+ characters</span>
                    <span className={checks.upper ? 'met' : ''}>{checks.upper ? '✓' : '○'} Uppercase letter</span>
                    <span className={checks.lower ? 'met' : ''}>{checks.lower ? '✓' : '○'} Lowercase letter</span>
                    <span className={checks.number ? 'met' : ''}>{checks.number ? '✓' : '○'} Number</span>
                    <span className={checks.special ? 'met' : ''}>{checks.special ? '✓' : '○'} Special character</span>
                  </div>
                )}

                <label htmlFor="confirmPassword">Confirm new password</label>
                <input
                  id="confirmPassword"
                  type={showPassword ? 'text' : 'password'}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  autoComplete="new-password"
                />
                {confirmPassword && !passwordsMatch && (
                  <div style={{ fontSize: 11, color: 'var(--error)', marginTop: 6 }}>Passwords don't match</div>
                )}

                <button type="submit" className="btn-gradient auth-submit" disabled={loading}>
                  {loading ? <span className="spinner" /> : 'Reset Password'}
                </button>
              </form>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default ResetPassword