import { Navigate } from 'react-router-dom'
import { isAuthenticated } from '../api/client'

function RequireAuth({ children }) {
  if (!isAuthenticated()) {
    return <Navigate to="/" replace />
  }
  return children
}

export default RequireAuth
