import { useEffect, useState } from 'react'
import { Plus } from 'lucide-react'
import { api, Deal } from '../api/client'
import Modal from '../components/Modal'
import CardActions from '../components/CardActions'
import Page, { Loading } from '../components/Page'
import { DEAL_STAGES, formatMoney } from '../utils'

const STAGE_ORDER = ['new', 'preparation', 'proposal', 'negotiation', 'won', 'lost']
const emptyForm = { title: '', amount: 0, stage: 'new' }

export default function Deals() {
  const [deals, setDeals] = useState<Deal[]>([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [form, setForm] = useState(emptyForm)

  const load = async () => {
    setLoading(true)
    try {
      setDeals(await api.deals.list())
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }
  useEffect(() => { load() }, [])

  const openCreate = () => {
    setEditingId(null)
    setForm(emptyForm)
    setModalOpen(true)
  }

  const openEdit = (deal: Deal) => {
    setEditingId(deal.id)
    setForm({ title: deal.title, amount: deal.amount, stage: deal.stage })
    setModalOpen(true)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (editingId) {
      await api.deals.update(editingId, form)
    } else {
      await api.deals.create(form)
    }
    setModalOpen(false)
    load()
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Удалить сделку?')) return
    await api.deals.delete(id)
    load()
  }

  const handleStageChange = async (dealId: number, stage: string) => {
    await api.deals.update(dealId, { stage })
    load()
  }

  if (loading) return <Loading />

  return (
    <Page
      title="Сделки"
      action={
        <button className="btn-primary flex items-center gap-2" onClick={openCreate}>
          <Plus size={18} /> Новая
        </button>
      }
    >
      {/* Мобильный список */}
      <div className="md:hidden space-y-3">
        {deals.map((deal) => (
          <div key={deal.id} className="card p-4">
            <div className="flex items-start justify-between gap-2 mb-2">
              <h3 className="font-semibold">{deal.title}</h3>
              <span className={`shrink-0 px-2 py-0.5 rounded-full text-xs font-medium ${DEAL_STAGES[deal.stage]?.color}`}>
                {DEAL_STAGES[deal.stage]?.label}
              </span>
            </div>
            <div className="text-xl font-bold text-kinetix-700 mb-1">{formatMoney(deal.amount)}</div>
            {deal.company_name && <p className="text-sm text-gray-500">{deal.company_name}</p>}
            {deal.contact_name && <p className="text-sm text-gray-400">{deal.contact_name}</p>}
            <select
              value={deal.stage}
              onChange={(e) => handleStageChange(deal.id, e.target.value)}
              className="mt-3 w-full text-sm border rounded-lg px-3 py-2 bg-gray-50"
            >
              {STAGE_ORDER.map((s) => (
                <option key={s} value={s}>{DEAL_STAGES[s].label}</option>
              ))}
            </select>
            <CardActions onEdit={() => openEdit(deal)} onDelete={() => handleDelete(deal.id)} />
          </div>
        ))}
      </div>

      {/* Десктоп канбан */}
      <div className="hidden md:flex gap-3 overflow-x-auto pb-4">
        {STAGE_ORDER.map((stage) => {
          const info = DEAL_STAGES[stage]
          const stageDeals = deals.filter((d) => d.stage === stage)
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
                    <CardActions onEdit={() => openEdit(deal)} onDelete={() => handleDelete(deal.id)} />
                  </div>
                ))}
              </div>
            </div>
          )
        })}
      </div>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editingId ? 'Редактировать сделку' : 'Новая сделка'}>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label">Название *</label>
            <input className="input" required value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
          </div>
          <div>
            <label className="label">Сумма</label>
            <input className="input" type="number" value={form.amount} onChange={(e) => setForm({ ...form, amount: +e.target.value })} />
          </div>
          <div>
            <label className="label">Стадия</label>
            <select className="input" value={form.stage} onChange={(e) => setForm({ ...form, stage: e.target.value })}>
              {STAGE_ORDER.map((s) => (
                <option key={s} value={s}>{DEAL_STAGES[s].label}</option>
              ))}
            </select>
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" className="btn-secondary" onClick={() => setModalOpen(false)}>Отмена</button>
            <button type="submit" className="btn-primary">{editingId ? 'Сохранить' : 'Создать'}</button>
          </div>
        </form>
      </Modal>
    </Page>
  )
}
