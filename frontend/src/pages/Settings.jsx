import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Nav from '../components/Nav.jsx'
import { useToast } from '../components/Toast.jsx'
import '../styles/settings.css'
import { getMe, changePassword, logout, ApiError } from '../api/client'

function passwordChecks(pw) {
  return {
    length: pw.length >= 8,
    upper: /[A-Z]/.test(pw),
    lower: /[a-z]/.test(pw),
    number: /[0-9]/.test(pw),
    special: /[^A-Za-z0-9]/.test(pw),
  }
}

function Settings() {
  const [me, setMe] = useState(null)
  const [loadingMe, setLoadingMe] = useState(true)

  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPasswords, setShowPasswords] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const toast = useToast()
  const navigate = useNavigate()

  useEffect(() => {
    getMe()
      .then(setMe)
      .catch(() => {})
      .finally(() => setLoadingMe(false))
  }, [])

  const checks = passwordChecks(newPassword)
  const allMet = Object.values(checks).every(Boolean)
  const passwordsMatch = newPassword && newPassword === confirmPassword

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (!allMet) {
      setError('Please meet all new password requirements.')
      return
    }
    if (!passwordsMatch) {
      setError('New passwords do not match.')
      return
    }

    setLoading(true)
    try {
      await changePassword(currentPassword, newPassword)
      toast('Password changed. Please sign in again with your new password.', 'success')
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
      // Backend revokes all sessions on password change (including this
      // one's refresh token), so send the user back to login rather than
      // leaving them on a page that will start failing requests.
      await logout()
      navigate('/')
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : 'Could not change password.'
      setError(msg)
      toast(msg, 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="settings-page">
      <Nav />
      <div className="settings-content">
        <div className="settings-header animate-in">
          <h1>Settings</h1>
          <div className="subtitle">Manage your account and security.</div>
        </div>

        <div className="settings-card animate-in" style={{ animationDelay: '40ms' }}>
          <h2>Account</h2>
          {loadingMe ? (
            <div className="settings-skeleton-row">
              <div className="skeleton" style={{ width: '60%', height: 16 }} />
            </div>
          ) : me ? (
            <div className="settings-info-grid">
              <div>
                <div className="settings-info-label">Username</div>
                <div className="settings-info-value">{me.username}</div>
              </div>
              <div>
                <div className="settings-info-label">Email</div>
                <div className="settings-info-value">{me.email}</div>
              </div>
            </div>
          ) : (
            <p className="settings-error-text">Could not load account info.</p>
          )}
        </div>

        <div className="settings-card animate-in" style={{ animationDelay: '80ms' }}>
          <h2>Change password</h2>
          <p className="settings-card-sub">
            Changing your password will sign you out of all devices, including this one.
          </p>

          {error && <div className="settings-error">{error}</div>}

          <form onSubmit={handleSubmit} className="settings-form">
            <label htmlFor="currentPassword">Current password</label>
            <input
              id="currentPassword"
              type={showPasswords ? 'text' : 'password'}
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              required
              autoComplete="current-password"
            />

            <label htmlFor="newPassword">New password</label>
            <input
              id="newPassword"
              type={showPasswords ? 'text' : 'password'}
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
              autoComplete="new-password"
            />

            {newPassword && (
              <div className="settings-requirements">
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
              type={showPasswords ? 'text' : 'password'}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              autoComplete="new-password"
            />
            {confirmPassword && !passwordsMatch && (
              <div className="settings-mismatch">Passwords don't match</div>
            )}

            <label className="settings-show-toggle">
              <input
                type="checkbox"
                checked={showPasswords}
                onChange={(e) => setShowPasswords(e.target.checked)}
              />
              Show passwords
            </label>

            <button type="submit" className="btn-gradient settings-submit" disabled={loading}>
              {loading ? <span className="spinner" /> : 'Change Password'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

export default Settings