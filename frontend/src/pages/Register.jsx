import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import '../styles/auth.css'
import { register, login, setTokens, ApiError } from '../api/client'

function passwordChecks(pw) {
  return {
    length: pw.length >= 8,
    upper: /[A-Z]/.test(pw),
    lower: /[a-z]/.test(pw),
    number: /[0-9]/.test(pw),
    special: /[^A-Za-z0-9]/.test(pw),
  }
}

function passwordStrength(checks) {
  const score = Object.values(checks).filter(Boolean).length
  const levels = [
    { label: 'Weak', pct: 20 },
    { label: 'Weak', pct: 20 },
    { label: 'Fair', pct: 45 },
    { label: 'Good', pct: 70 },
    { label: 'Strong', pct: 90 },
    { label: 'Strong', pct: 100 },
  ]
  return levels[score]
}

function Register() {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const checks = passwordChecks(password)
  const strength = passwordStrength(checks)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await register(username, email, password)
      const data = await login(email, password)
      setTokens(data)
      navigate('/dashboard')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Registration failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-hero animate-in">
        <div className="auth-hero-glow" />
        <div className="auth-hero-mark" />
        <div className="auth-hero-content">
          <div className="auth-hero-eyebrow">Personal Knowledge Base</div>
          <h1>Start building your<br />knowledge base today.</h1>
          <p>Create an account and turn your documents into a searchable, private knowledge base in minutes.</p>
        </div>
      </div>

      <div className="auth-form-panel">
        <div className="auth-card animate-scale-in">
          <div className="auth-mark">Get started</div>
          <h1>Create an account</h1>
          <p className="auth-sub">Start building your personal knowledge base.</p>

          {error && <div className="auth-error animate-in">{error}</div>}

          <form onSubmit={handleSubmit} className="auth-form">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoComplete="username"
            />

            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />

            <label htmlFor="password">Password</label>
            <div className="auth-password-field">
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={8}
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
              <>
                <div className="auth-strength">
                  <div className="auth-strength-track">
                    <div className="auth-strength-fill" style={{ width: `${strength.pct}%` }} />
                  </div>
                  <span>{strength.label}</span>
                </div>
                <div className="auth-requirements">
                  <span className={checks.length ? 'met' : ''}>{checks.length ? '✓' : '○'} 8+ characters</span>
                  <span className={checks.upper ? 'met' : ''}>{checks.upper ? '✓' : '○'} Uppercase letter</span>
                  <span className={checks.lower ? 'met' : ''}>{checks.lower ? '✓' : '○'} Lowercase letter</span>
                  <span className={checks.number ? 'met' : ''}>{checks.number ? '✓' : '○'} Number</span>
                  <span className={checks.special ? 'met' : ''}>{checks.special ? '✓' : '○'} Special character</span>
                </div>
              </>
            )}

            <button type="submit" className="btn-gradient auth-submit" disabled={loading}>
              {loading ? <span className="spinner" /> : 'Register'}
            </button>
          </form>

          <p className="auth-switch">
            Already have an account? <Link to="/">Login</Link>
          </p>
        </div>
      </div>
    </div>
  )
}

export default Register