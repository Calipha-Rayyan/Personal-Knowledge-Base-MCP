import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import '../styles/auth.css'
import { login, setTokens, ApiError } from '../api/client'

function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const data = await login(email, password)
      setTokens(data)
      navigate('/dashboard')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Login failed. Please try again.')
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
          <h1>Your knowledge,<br />organized and searchable.</h1>
          <p>Upload your documents, and find exactly what you need using semantic search — powered by real vector retrieval, not keyword matching.</p>
          <div className="auth-hero-features">
            <div className="auth-hero-feature">
              <span className="dot" /> Semantic search across your own documents
            </div>
            <div className="auth-hero-feature">
              <span className="dot" /> Private, isolated per account
            </div>
            <div className="auth-hero-feature">
              <span className="dot" /> Connects to MCP-compatible AI clients
            </div>
          </div>
        </div>
      </div>

      <div className="auth-form-panel">
        <div className="auth-card animate-scale-in">
          <div className="auth-mark">Sign in</div>
          <h1>Welcome back</h1>
          <p className="auth-sub">Sign in to search your notes and documents.</p>

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

            <label htmlFor="password">Password</label>
            <div className="auth-password-field">
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="current-password"
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

            <div className="auth-forgot-link">
              <Link to="/forgot-password">Forgot password?</Link>
            </div>

            <button type="submit" className="btn-gradient auth-submit" disabled={loading}>
              {loading ? <span className="spinner" /> : 'Sign In'}
            </button>
          </form>

          <p className="auth-switch">
            Don't have an account? <Link to="/register">Register</Link>
          </p>
        </div>
      </div>
    </div>
  )
}

export default Login