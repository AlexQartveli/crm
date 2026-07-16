import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { api, AuthUser, clearAuthToken, clearCompanySlug, getAuthToken, setAuthToken, setCompanySlug } from '../api/client'
import { canAccess, firstAllowedRoute, type Permission } from './permissions'

interface AuthContextValue {
  user: AuthUser | null
  loading: boolean
  login: (companySlug: string, username: string, password: string) => Promise<AuthUser>
  logout: () => void
  can: (permission: Permission | string) => boolean
  defaultRoute: string
  refresh: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [loading, setLoading] = useState(true)

  const refresh = useCallback(async () => {
    const token = getAuthToken()
    if (!token) {
      setUser(null)
      return
    }
    const me = await api.auth.me()
    setUser(me)
  }, [])

  useEffect(() => {
    refresh()
      .catch(() => {
        clearAuthToken()
        setUser(null)
      })
      .finally(() => setLoading(false))
  }, [refresh])

  const login = useCallback(async (companySlug: string, username: string, password: string) => {
    const result = await api.auth.login(companySlug, username, password)
    setAuthToken(result.access_token)
    setCompanySlug(companySlug)
    setUser(result.user)
    return result.user
  }, [])

  const logout = useCallback(() => {
    clearAuthToken()
    clearCompanySlug()
    setUser(null)
    window.location.hash = '#/login'
  }, [])

  const can = useCallback(
    (permission: Permission | string) => {
      if (!user) return false
      return canAccess(user.permissions, permission)
    },
    [user],
  )

  const defaultRoute = useMemo(
    () => (user ? firstAllowedRoute(user.permissions) : '/login'),
    [user],
  )

  const value = useMemo(
    () => ({ user, loading, login, logout, can, defaultRoute, refresh }),
    [user, loading, login, logout, can, defaultRoute, refresh],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
