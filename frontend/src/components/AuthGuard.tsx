import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { ROUTE_PERMISSIONS } from '../auth/permissions'

export default function AuthGuard() {
  const { user, loading, defaultRoute, can } = useAuth()
  const location = useLocation()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-app-bg text-app-text-muted">
        Loading...
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }

  const required = ROUTE_PERMISSIONS[location.pathname]
  if (required && !can(required)) {
    return <Navigate to={defaultRoute} replace />
  }

  return <Outlet />
}
