import { useEffect, useState } from 'react'
import { Link, Navigate } from 'react-router-dom'
import {
  Building2,
  Briefcase,
  GraduationCap,
  Factory,
  ShoppingBag,
  Hotel,
  HardHat,
  Wheat,
  Stethoscope,
  Truck,
  Users,
  type LucideIcon,
} from 'lucide-react'
import { api, CrmType, setAuthToken, setCompanySlug } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import { firstAllowedRoute } from '../auth/permissions'
import { FALLBACK_CRM_TYPES } from '../crm/defaultCrmTypes'
import { useI18n } from '../i18n/I18nContext'
import type { Locale } from '../i18n/translations'

const ICONS: Record<string, LucideIcon> = {
  briefcase: Briefcase,
  'graduation-cap': GraduationCap,
  factory: Factory,
  'shopping-bag': ShoppingBag,
  hotel: Hotel,
  'hard-hat': HardHat,
  wheat: Wheat,
  stethoscope: Stethoscope,
  truck: Truck,
  users: Users,
}

function crmLabel(type: CrmType, locale: Locale) {
  if (locale === 'en') return type.label_en
  if (locale === 'ka') return type.label_ka
  return type.label_ru
}

function crmDesc(type: CrmType, locale: Locale) {
  if (locale === 'en') return type.desc_en
  if (locale === 'ka') return type.desc_ka
  return type.desc_ru
}

export default function Register() {
  const { t, locale } = useI18n()
  const { user, refresh } = useAuth()
  const [crmTypes, setCrmTypes] = useState<CrmType[]>(FALLBACK_CRM_TYPES)
  const [typesLoading, setTypesLoading] = useState(true)
  const [form, setForm] = useState({
    crm_type: 'general',
    company_name: '',
    company_slug: '',
    admin_full_name: '',
    admin_username: '',
    admin_password: '',
    admin_email: '',
  })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    api.auth.crmTypes()
      .then((types) => { if (types.length) setCrmTypes(types) })
      .catch(() => setCrmTypes(FALLBACK_CRM_TYPES))
      .finally(() => setTypesLoading(false))
  }, [])

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
        crm_type: form.crm_type,
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

  const selected = crmTypes.find((c) => c.id === form.crm_type)

  return (
    <div className="min-h-screen flex items-center justify-center bg-app-bg p-4">
      <div className="w-full max-w-3xl card p-8">
        <div className="text-center mb-8">
          <Building2 className="mx-auto text-kinetix-600 mb-3" size={36} />
          <h1 className="text-2xl font-bold text-app-text">{t.auth.registerTitle}</h1>
          <p className="text-app-text-muted mt-1">{t.auth.registerSubtitle}</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="text-sm text-red-600 bg-red-50 dark:bg-red-900/20 dark:text-red-300 rounded-lg p-3">{error}</div>
          )}

          <div>
            <label className="label">{t.auth.crmType} *</label>
            {typesLoading && (
              <p className="text-xs text-app-text-muted mt-1">{t.common.loading}</p>
            )}
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3 mt-2">
              {crmTypes.map((type) => {
                const Icon = ICONS[type.icon] || Briefcase
                const active = form.crm_type === type.id
                return (
                  <button
                    key={type.id}
                    type="button"
                    onClick={() => setForm({ ...form, crm_type: type.id })}
                    className={`text-left p-4 rounded-xl border-2 transition-all ${
                      active
                        ? 'border-kinetix-600 bg-kinetix-50 dark:bg-kinetix-900/20'
                        : 'border-app-border hover:border-kinetix-400 bg-app-surface'
                    }`}
                  >
                    <Icon size={22} className={active ? 'text-kinetix-600' : 'text-app-text-muted'} />
                    <div className="font-medium text-sm mt-2">{crmLabel(type, locale)}</div>
                    <div className="text-xs text-app-text-muted mt-1 line-clamp-2">{crmDesc(type, locale)}</div>
                  </button>
                )
              })}
            </div>
            {selected && selected.services && selected.services.length > 0 && (
              <div className="mt-3 p-4 rounded-xl bg-kinetix-50 dark:bg-kinetix-900/20 border border-kinetix-200 dark:border-kinetix-800">
                <p className="text-sm font-medium text-app-text mb-2">{t.auth.includedServices}</p>
                <ul className="grid sm:grid-cols-2 gap-1.5 text-xs text-app-text-muted">
                  {selected.services.map((s) => (
                    <li key={s.id} className="flex items-start gap-1.5">
                      <span className="text-kinetix-600 shrink-0">✓</span>
                      <span>{locale === 'en' ? s.label_en : locale === 'ka' ? s.label_ka : s.label_ru}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="label">{t.auth.companyName} *</label>
              <input className="input" required value={form.company_name}
                onChange={(e) => setForm({ ...form, company_name: e.target.value })} />
            </div>
            <div>
              <label className="label">{t.auth.companyCode} *</label>
              <input className="input" required value={form.company_slug} placeholder="my-company"
                onChange={(e) => setForm({ ...form, company_slug: e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, '-') })} />
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
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

          <div className="grid md:grid-cols-2 gap-4">
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
