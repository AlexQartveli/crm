import { useEffect, useState } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { ArrowLeft, LogIn, Sparkles } from 'lucide-react'
import { api, DemoAccount } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import { firstAllowedRoute } from '../auth/permissions'
import { crmTypeIcon } from '../crm/crmTypeIcons'
import { FALLBACK_CRM_TYPES } from '../crm/defaultCrmTypes'
import { useI18n } from '../i18n/I18nContext'
import type { Locale } from '../i18n/translations'

function label(account: DemoAccount, locale: Locale) {
  if (locale === 'en') return account.label_en
  if (locale === 'ka') return account.label_ka
  return account.label_ru
}

function desc(account: DemoAccount, locale: Locale) {
  if (locale === 'en') return account.desc_en
  if (locale === 'ka') return account.desc_ka
  return account.desc_ru
}

function fallbackDemoAccounts(): DemoAccount[] {
  return FALLBACK_CRM_TYPES.map((type) => ({
    crm_type: type.id,
    slug: type.id === 'general' ? 'demo' : `demo-${type.id}`,
    label_ru: type.label_ru,
    label_en: type.label_en,
    label_ka: type.label_ka,
    desc_ru: type.desc_ru,
    desc_en: type.desc_en,
    desc_ka: type.desc_ka,
    icon: type.icon,
    username: 'admin',
    password: type.id === 'general' ? 'admin123' : 'demo123',
  }))
}

export default function Demo() {
  const { t, locale } = useI18n()
  const { user, login } = useAuth()
  const [accounts, setAccounts] = useState<DemoAccount[]>(fallbackDemoAccounts())
  const [loading, setLoading] = useState(true)
  const [entering, setEntering] = useState<string | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.auth.demoAccounts()
      .then((items) => { if (items.length) setAccounts(items) })
      .catch(() => setAccounts(fallbackDemoAccounts()))
      .finally(() => setLoading(false))
  }, [])

  if (user) {
    return <Navigate to={firstAllowedRoute(user.permissions)} replace />
  }

  const handleEnter = async (account: DemoAccount) => {
    setError('')
    setEntering(account.crm_type)
    try {
      const loggedIn = await login(account.slug, account.username, account.password)
      window.location.hash = `#${firstAllowedRoute(loggedIn.permissions)}`
    } catch (err) {
      setError(err instanceof Error ? err.message : t.auth.loginError)
    } finally {
      setEntering(null)
    }
  }

  return (
    <div className="min-h-screen bg-app-bg">
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="mb-8">
          <Link
            to="/login"
            className="inline-flex items-center gap-2 text-sm text-app-text-muted hover:text-app-text mb-4"
          >
            <ArrowLeft size={16} />
            {t.auth.login}
          </Link>
          <div className="flex items-start gap-3">
            <div className="p-2 rounded-xl bg-kinetix-100 dark:bg-kinetix-900/30 text-kinetix-600">
              <Sparkles size={24} />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-app-text">{t.auth.demoGalleryTitle}</h1>
              <p className="text-app-text-muted mt-1">{t.auth.demoGallerySubtitle}</p>
            </div>
          </div>
        </div>

        {error && (
          <div className="mb-6 text-sm text-red-600 bg-red-50 dark:bg-red-900/20 dark:text-red-300 rounded-lg p-3">
            {error}
          </div>
        )}

        {loading ? (
          <p className="text-app-text-muted">{t.common.loading}</p>
        ) : (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {accounts.map((account) => {
              const Icon = crmTypeIcon(account.icon)
              const busy = entering === account.crm_type
              return (
                <button
                  key={account.crm_type}
                  type="button"
                  onClick={() => handleEnter(account)}
                  disabled={!!entering}
                  className="card p-5 text-left hover:ring-2 hover:ring-kinetix-500/40 transition-all disabled:opacity-60"
                >
                  <div className="flex items-start gap-3 mb-3">
                    <div className="p-2 rounded-lg bg-kinetix-50 dark:bg-kinetix-900/20 text-kinetix-600 shrink-0">
                      <Icon size={22} />
                    </div>
                    <div className="min-w-0">
                      <h2 className="font-semibold text-app-text">{label(account, locale)}</h2>
                      <p className="text-xs text-app-text-muted mt-0.5 line-clamp-2">{desc(account, locale)}</p>
                    </div>
                  </div>
                  <div className="flex items-center justify-between gap-2 mt-4 pt-3 border-t border-app-border">
                    <span className="text-xs text-app-text-muted font-mono">{account.slug}</span>
                    <span className="inline-flex items-center gap-1.5 text-sm font-medium text-kinetix-600">
                      <LogIn size={14} />
                      {busy ? t.common.loading : t.auth.demoEnter}
                    </span>
                  </div>
                </button>
              )
            })}
          </div>
        )}

        <p className="text-center text-sm text-app-text-muted mt-8">
          {t.auth.hasAccount}{' '}
          <Link to="/register" className="text-kinetix-600 hover:underline">{t.auth.register}</Link>
        </p>
      </div>
    </div>
  )
}
