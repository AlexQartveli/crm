import { useState } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { Building2 } from 'lucide-react'
import { api, setAuthToken, setCompanySlug } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import { firstAllowedRoute } from '../auth/permissions'
import { useI18n } from '../i18n/I18nContext'

export default function Register() {
  const { t } = useI18n()
  const { user, refresh } = useAuth()
  const [form, setForm] = useState({
    company_name: '',
    company_slug: '',
    admin_full_name: '',
    admin_username: '',
    admin_password: '',
    admin_email: '',
  })
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
      const result = await api.auth.register({
        company_name: form.company_name,
        company_slug: form.company_slug,
        admin_username: form.admin_username,
        admin_password: form.admin_password,
        admin_full_name: form.admin_full_name,
        admin_email: form.admin_email || undefined,
      })
      setAuthToken(result.access_token)
      setCompanySlug(result.user.tenant.slug)
      await refresh()
      window.location.hash = `#${firstAllowedRoute(result.user.permissions)}`
    } catch (err) {
      setError(err instanceof Error ? err.message : t.auth.registerError)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-app-bg p-4">
      <div className="w-full max-w-lg card p-8">
        <div className="text-center mb-8">
          <Building2 className="mx-auto text-kinetix-600 mb-3" size={36} />
          <h1 className="text-2xl font-bold text-app-text">{t.auth.registerTitle}</h1>
          <p className="text-app-text-muted mt-1">{t.auth.registerSubtitle}</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="text-sm text-red-600 bg-red-50 dark:bg-red-900/20 dark:text-red-300 rounded-lg p-3">{error}</div>
          )}
          <div>
            <label className="label">{t.auth.companyName} *</label>
            <input className="input" required value={form.company_name}
              onChange={(e) => setForm({ ...form, company_name: e.target.value })} />
          </div>
          <div>
            <label className="label">{t.auth.companyCode} *</label>
            <input className="input" required value={form.company_slug} placeholder="my-company"
              onChange={(e) => setForm({ ...form, company_slug: e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, '-') })} />
            <p className="text-xs text-app-text-muted mt-1">{t.auth.companyCodeHint}</p>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">{t.common.name} *</label>
              <input className="input" required value={form.admin_full_name}
                onChange={(e) => setForm({ ...form, admin_full_name: e.target.value })} />
            </div>
            <div>
              <label className="label">{t.auth.username} *</label>
              <input className="input" required value={form.admin_username}
                onChange={(e) => setForm({ ...form, admin_username: e.target.value })} />
            </div>
          </div>
          <div>
            <label className="label">{t.common.email}</label>
            <input className="input" type="email" value={form.admin_email}
              onChange={(e) => setForm({ ...form, admin_email: e.target.value })} />
          </div>
          <div>
            <label className="label">{t.auth.password} *</label>
            <input className="input" type="password" required minLength={4} value={form.admin_password}
              onChange={(e) => setForm({ ...form, admin_password: e.target.value })} />
          </div>
          <button type="submit" className="btn-primary w-full" disabled={submitting}>
            {submitting ? t.common.loading : t.auth.register}
          </button>
        </form>

        <p className="text-center text-sm text-app-text-muted mt-6">
          {t.auth.hasAccount}{' '}
          <Link to="/login" className="text-kinetix-600 hover:underline">{t.auth.login}</Link>
        </p>
      </div>
    </div>
  )
}
