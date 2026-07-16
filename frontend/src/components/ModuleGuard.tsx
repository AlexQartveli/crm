import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { useCrmConfig } from '../crm/CrmConfigContext'
import { ROUTE_MODULE } from '../crm/helpers'

export default function ModuleGuard() {
  const location = useLocation()
  const { defaultRoute } = useAuth()
  const { routeEnabled, loading, config } = useCrmConfig()

  const path = location.pathname === '' ? '/' : location.pathname
  const module = ROUTE_MODULE[path]

  if (loading && !config) {
    return <div className="p-8 text-app-text-muted">Loading...</div>
  }

  if (module && config && !routeEnabled(path)) {
    return <Navigate to={defaultRoute} replace />
  }

  return <Outlet />
}
