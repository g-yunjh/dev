import { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { isAuthenticated } from '../lib/auth'

interface ProtectedRouteProps {
  children: ReactNode
}

const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  return isAuthenticated() ? <>{children}</> : <Navigate to="/login" replace />
}

export default ProtectedRoute
