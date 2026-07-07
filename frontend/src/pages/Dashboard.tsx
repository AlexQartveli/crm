import { useEffect, useState } from 'react'
import { Users, Handshake, Building2, Package, TrendingUp, DollarSign } from 'lucide-react'
import { api, DashboardData } from '../api/client'
import Page, { Loading } from '../components/Page'
import { useI18n } from '../i18n/I18nContext'
import { useStatuses, formatMoney } from '../utils'

export default function Dashboard() {
  const { t } = useI18n()
  const { dealStages } = useStatuses()
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.dashboard().then(setData).catch(console.error).finally(() => setLoading(false))
  }, [])

  if (loading || !data) return <Loading />

  const stats = [
    { label: t.dashboard.stats.leads, value: data.leads, icon: Users, color: 'text-blue-600 bg-blue-50' },
    { label: t.dashboard.stats.deals, value: data.deals, icon: Handshake, color: 'text-purple-600 bg-purple-50' },
    { label: t.dashboard.stats.contacts, value: data.contacts, icon: Users, color: 'text-green-600 bg-green-50' },
    { label: t.dashboard.stats.companies, value: data.companies, icon: Building2, color: 'text-orange-600 bg-orange-50' },
    { label: t.dashboard.stats.products, value: data.products, icon: Package, color: 'text-indigo-600 bg-indigo-50' },
    { label: t.dashboard.stats.stock, value: data.total_stock, icon: Package, color: 'text-teal-600 bg-teal-50' },
  ]

  return (
    <Page title={t.dashboard.title}>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
        {stats.map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="card p-4">
            <div className={`inline-flex p-2 rounded-lg ${color} mb-3`}>
              <Icon size={20} />
            </div>
            <div className="text-2xl font-bold">{value}</div>
            <div className="text-sm text-gray-500">{label}</div>
          </div>
        ))}
      </div>

      <div className="grid md:grid-cols-2 gap-6 mb-8">
        <div className="card p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg text-green-600 bg-green-50">
              <DollarSign size={20} />
            </div>
            <h2 className="text-lg font-semibold">{t.dashboard.wonDeals}</h2>
          </div>
          <div className="text-3xl font-bold text-green-600">{formatMoney(data.won_amount)}</div>
        </div>
        <div className="card p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg text-kinetix-600 bg-kinetix-50">
              <TrendingUp size={20} />
            </div>
            <h2 className="text-lg font-semibold">{t.dashboard.pipeline}</h2>
          </div>
          <div className="text-3xl font-bold text-kinetix-600">{formatMoney(data.pipeline_amount)}</div>
        </div>
      </div>

      <div className="card p-6">
        <h2 className="text-lg font-semibold mb-4">{t.dashboard.dealsByStage}</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {Object.entries(dealStages).map(([key, { label, color }]) => (
            <div key={key} className="text-center p-4 rounded-lg bg-gray-50">
              <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${color} mb-2`}>
                {label}
              </span>
              <div className="text-2xl font-bold">{data.deals_by_stage[key] || 0}</div>
            </div>
          ))}
        </div>
      </div>
    </Page>
  )
}
