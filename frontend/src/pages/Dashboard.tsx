import { useEffect, useState } from 'react'
import { Users, Handshake, Building2, Package, TrendingUp, DollarSign, MessageCircle } from 'lucide-react'
import { api, DashboardData } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import { PERM } from '../auth/permissions'
import Page from '../components/Page'
import { useI18n } from '../i18n/I18nContext'
import { useStatuses, formatMoney } from '../utils'

export default function Dashboard() {
  const { t } = useI18n()
  const { can } = useAuth()
  const { dealStages } = useStatuses()
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.dashboard().then(setData).catch(console.error).finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <Page title={t.dashboard.title}>
        <p className="text-app-text-muted">{t.common.loading}</p>
        <p className="text-sm text-app-text-muted mt-2">{t.common.connectingServer}</p>
      </Page>
    )
  }
  if (!data) return <Page title={t.dashboard.title}><p className="text-app-text-muted">{t.common.empty}</p></Page>

  const stats = [
    { label: t.dashboard.stats.leads, value: data.leads, icon: Users, color: 'stat-icon-blue', show: can(PERM.leadsView) },
    { label: t.dashboard.stats.deals, value: data.deals, icon: Handshake, color: 'stat-icon-purple', show: can(PERM.dealsView) },
    { label: t.dashboard.stats.contacts, value: data.contacts, icon: Users, color: 'stat-icon-green', show: can(PERM.contactsView) },
    { label: t.dashboard.stats.companies, value: data.companies, icon: Building2, color: 'stat-icon-orange', show: can(PERM.companiesView) },
    { label: t.dashboard.stats.products, value: data.products, icon: Package, color: 'stat-icon-indigo', show: can(PERM.productsView) },
    { label: t.dashboard.stats.stock, value: data.total_stock, icon: Package, color: 'stat-icon-teal', show: can(PERM.stocksView) },
    { label: t.dashboard.stats.messages, value: data.unread_messages || 0, icon: MessageCircle, color: 'stat-icon-blue', show: can(PERM.inbox) },
  ].filter((s) => s.show)

  const showDeals = can(PERM.dealsView)

  return (
    <Page title={t.dashboard.title}>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
        {stats.map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="card p-4">
            <div className={`stat-icon ${color} mb-3`}>
              <Icon size={20} />
            </div>
            <div className="text-2xl font-bold text-app-text">{value}</div>
            <div className="text-sm text-app-text-muted">{label}</div>
          </div>
        ))}
      </div>

      {showDeals && (
        <>
          <div className="grid md:grid-cols-2 gap-6 mb-8">
            <div className="card p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="stat-icon stat-icon-green">
                  <DollarSign size={20} />
                </div>
                <h2 className="text-lg font-semibold text-app-text">{t.dashboard.wonDeals}</h2>
              </div>
              <div className="text-3xl font-bold text-green-600 dark:text-green-400">{formatMoney(data.won_amount)}</div>
            </div>
            <div className="card p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="stat-icon stat-icon-kinetix">
                  <TrendingUp size={20} />
                </div>
                <h2 className="text-lg font-semibold text-app-text">{t.dashboard.pipeline}</h2>
              </div>
              <div className="text-3xl font-bold text-kinetix-600 dark:text-kinetix-400">{formatMoney(data.pipeline_amount)}</div>
            </div>
          </div>

          <div className="card p-6">
            <h2 className="text-lg font-semibold mb-4 text-app-text">{t.dashboard.dealsByStage}</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
              {Object.entries(dealStages).map(([key, { label, color }]) => (
                <div key={key} className="stage-tile">
                  <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${color} mb-2`}>
                    {label}
                  </span>
                  <div className="text-2xl font-bold text-app-text">{data.deals_by_stage[key] || 0}</div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </Page>
  )
}
