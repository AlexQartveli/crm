import { useState } from 'react'
import { Navigate } from 'react-router-dom'
import { LogIn } from 'lucide-react'
import { useAuth } from '../auth/AuthContext'
import { firstAllowedRoute } from '../auth/permissions'
import { useI18n } from '../i18n/I18nContext'

export default function Login() {
  const { t } = useI18n()
  const { user, login } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  if (user) {
    return <Navigate to={firstAllowedRoute(user.permissions)} replace />
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      const loggedIn = await login(username.trim(), password)
      window.location.hash = `#${firstAllowedRoute(loggedIn.permissions)}`
    } catch (err) {
      setError(err instanceof Error ? err.message : t.auth.loginError)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-app-bg p-4">
      <div className="w-full max-w-md card p-8">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-app-text">KINETIKS</h1>
          <p className="text-app-text-muted mt-1">{t.auth.subtitle}</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="text-sm text-red-600 bg-red-50 dark:bg-red-900/20 dark:text-red-300 rounded-lg p-3">
              {error}
            </div>
          )}
          <div>
            <label className="label">{t.auth.username}</label>
            <input
              className="input"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              required
            />
          </div>
          <div>
            <label className="label">{t.auth.password}</label>
            <input
              className="input"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              required
            />
          </div>
          <button type="submit" className="btn-primary w-full flex items-center justify-center gap-2" disabled={submitting}>
            <LogIn size={18} />
            {submitting ? t.common.loading : t.auth.login}
          </button>
        </form>

        <div className="mt-8 pt-6 border-t border-app-border">
          <p className="text-xs text-app-text-muted mb-3">{t.auth.demoAccounts}</p>
          <div className="grid grid-cols-2 gap-2 text-xs text-app-text-secondary">
            <div><strong>admin</strong> / admin123</div>
            <div><strong>sales</strong> / sales123</div>
            <div><strong>operator</strong> / operator123</div>
            <div><strong>warehouse</strong> / warehouse123</div>
            <div><strong>accountant</strong> / accountant123</div>
            <div><strong>director</strong> / director123</div>
          </div>
        </div>
      </div>
    </div>
  )
}
