import { useEffect, useState } from 'react'
import { Plus } from 'lucide-react'
import { api, Deal } from '../api/client'
import Modal from '../components/Modal'
import Page, { Loading } from '../components/Page'
import { DEAL_STAGES, formatMoney } from '../utils'

const STAGE_ORDER = ['new', 'preparation', 'proposal', 'negotiation', 'won', 'lost']

export default function Deals() {
  const [deals, setDeals] = useState<Deal[]>([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [form, setForm] = useState({ title: '', amount: 0, stage: 'new' })

  const load = async () => {
    setLoading(true)
    try {
      setDeals(await api.deals.list())
    } finally {
      setLoading(false)
    }
  }
  useEffect(() => { load() }, [])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    await api.deals.create(form)
    setModalOpen(false)
    setForm({ title: '', amount: 0, stage: 'new' })
    load()
  }

  const handleStageChange = async (dealId: number, stage: string) => {
    await api.deals.update(dealId, { stage })
    load()
  }

  const dealsByStage = STAGE_ORDER.reduce<Record<string, Deal[]>>((acc, stage) => {
    acc[stage] = deals.filter((d) => d.stage === stage)
    return acc
  }, {})

  if (loading) return <Loading />

  return (
    <Page
      title="Сделки"
      action={
        <button className="btn-primary flex items-center gap-2" onClick={() => setModalOpen(true)}>
          <Plus size={18} /> Новая сделка
        </button>
      }
    >
      <div className="flex gap-3 overflow-x-auto pb-4 -mx-4 px-4 md:mx-0 md:px-0">
        {STAGE_ORDER.map((stage) => {
          const info = DEAL_STAGES[stage]
          const stageDeals = dealsByStage[stage] || []
          const total = stageDeals.reduce((s, d) => s + d.amount, 0)

          return (
            <div key={stage} className="min-w-[260px] flex-shrink-0">
              <div className="flex items-center justify-between mb-3">
                <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${info.color}`}>
                  {info.label}
                </span>
                <span className="text-xs text-gray-500">
                  {stageDeals.length} · {formatMoney(total)}
                </span>
              </div>
              <div className="space-y-3 min-h-[120px]">
                {stageDeals.map((deal) => (
                  <div key={deal.id} className="card p-4 hover:shadow-md transition-shadow">
                    <h3 className="font-medium text-sm mb-2">{deal.title}</h3>
                    <div className="text-lg font-bold text-kinetix-700 mb-2">
                      {formatMoney(deal.amount)}
                    </div>
                    {deal.company_name && (
                      <div className="text-xs text-gray-500 mb-1">{deal.company_name}</div>
                    )}
                    <select
                      value={deal.stage}
                      onChange={(e) => handleStageChange(deal.id, e.target.value)}
                      className="mt-2 w-full text-xs border rounded-lg px-2 py-1.5 bg-gray-50"
                    >
                      {STAGE_ORDER.map((s) => (
                        <option key={s} value={s}>{DEAL_STAGES[s].label}</option>
                      ))}
                    </select>
                  </div>
                ))}
              </div>
            </div>
          )
        })}
      </div>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Новая сделка">
        <form onSubmit={handleCreate} className="space-y-4">
          <div>
            <label className="label">Название *</label>
            <input className="input" required value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
          </div>
          <div>
            <label className="label">Сумма</label>
            <input className="input" type="number" value={form.amount} onChange={(e) => setForm({ ...form, amount: +e.target.value })} />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" className="btn-secondary" onClick={() => setModalOpen(false)}>Отмена</button>
            <button type="submit" className="btn-primary">Создать</button>
          </div>
        </form>
      </Modal>
    </Page>
  )
}
