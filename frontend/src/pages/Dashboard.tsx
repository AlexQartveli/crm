import { useEffect, useState } from 'react'
import { Users, Handshake, Building2, Package, TrendingUp, DollarSign } from 'lucide-react'
import { api, DashboardData } from '../api/client'
import Page, { Loading } from '../components/Page'

import { DEAL_STAGES, formatMoney } from '../utils'

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.dashboard().then(setData).catch(console.error).finally(() => setLoading(false))
  }, [])

  if (loading || !data) return <Loading />

  const stats = [
    { label: 'Лиды', value: data.leads, icon: Users, color: 'text-blue-600 bg-blue-50' },
    { label: 'Сделки', value: data.deals, icon: Handshake, color: 'text-purple-600 bg-purple-50' },
    { label: 'Контакты', value: data.contacts, icon: Users, color: 'text-green-600 bg-green-50' },
    { label: 'Компании', value: data.companies, icon: Building2, color: 'text-orange-600 bg-orange-50' },
    { label: 'Товары', value: data.products, icon: Package, color: 'text-indigo-600 bg-indigo-50' },
    { label: 'На складе', value: data.total_stock, icon: Package, color: 'text-teal-600 bg-teal-50' },
  ]

  return (
    <Page title="Дашборд">

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
            <h2 className="text-lg font-semibold">Выигранные сделки</h2>
          </div>
          <div className="text-3xl font-bold text-green-600">{formatMoney(data.won_amount)}</div>
        </div>
        <div className="card p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg text-kinetix-600 bg-kinetix-50">
              <TrendingUp size={20} />
            </div>
            <h2 className="text-lg font-semibold">Воронка продаж</h2>
          </div>
          <div className="text-3xl font-bold text-kinetix-600">{formatMoney(data.pipeline_amount)}</div>
        </div>
      </div>

      <div className="card p-6">
        <h2 className="text-lg font-semibold mb-4">Сделки по стадиям</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {Object.entries(DEAL_STAGES).map(([key, { label, color }]) => (
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
