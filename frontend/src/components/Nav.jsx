import { NavLink, useNavigate } from 'react-router-dom'
import '../styles/nav.css'
import { logout } from '../api/client'

const LINKS = [
  { to: '/dashboard', label: 'Dashboard', icon: '⌂' },
  { to: '/documents', label: 'Documents', icon: '▤' },
  { to: '/upload', label: 'Upload', icon: '↑' },
  { to: '/search', label: 'Search', icon: '⌕' },
  { to: '/settings', label: 'Settings', icon: '⚙' },
]

function Nav() {
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/')
  }

  return (
    <nav className="app-nav">
      <div className="app-nav-inner">
        <NavLink to="/dashboard" className="app-nav-brand">
          <span className="app-nav-brand-mark" />
          Personal Knowledge Base
        </NavLink>

        <div className="app-nav-links">
          {LINKS.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                'app-nav-link' + (isActive ? ' active' : '')
              }
            >
              <span className="app-nav-icon">{link.icon}</span>
              {link.label}
            </NavLink>
          ))}
        </div>

        <button className="app-nav-logout" onClick={handleLogout}>
          Logout
        </button>
      </div>
    </nav>
  )
}

export default Nav