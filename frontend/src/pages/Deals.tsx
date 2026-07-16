import { useEffect, useState } from 'react'
import { Plus } from 'lucide-react'
import { api, Deal } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import { PERM } from '../auth/permissions'
import CustomFieldsForm from '../components/CustomFieldsForm'
import Modal from '../components/Modal'
import CardActions from '../components/CardActions'
import Page, { Loading } from '../components/Page'
import { useCrmConfig } from '../crm/CrmConfigContext'
import { formatCustomValue } from '../crm/helpers'
import { useI18n } from '../i18n/I18nContext'
import { useStatuses, formatMoney } from '../utils'

const emptyForm = {
  title: '', amount: 0, stage: 'new',
  custom_data: {} as Record<string, unknown>,
}

export default function Deals() {
  const { t, locale } = useI18n()
  const { can } = useAuth()
  const { entityLabel, fieldHidden, listFieldsFor } = useCrmConfig()
  const canManage = can(PERM.dealsManage)
  const { dealStages, dealStageOrder } = useStatuses()
  const customListFields = listFieldsFor('deals')
  const defaultStage = dealStageOrder[0] || 'new'
  const [deals, setDeals] = useState<Deal[]>([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [form, setForm] = useState({ ...emptyForm, stage: defaultStage })

  const pageTitle = entityLabel('deals', t.deals.title)

  const load = async () => {
    setLoading(true)
    try { setDeals(await api.deals.list()) } finally { setLoading(false) }
  }
  useEffect(() => { load() }, [])
  useEffect(() => { setForm((f) => ({ ...f, stage: f.stage || defaultStage })) }, [defaultStage])

  const openCreate = () => { setEditingId(null); setForm({ ...emptyForm, stage: defaultStage }); setModalOpen(true) }
  const openEdit = (deal: Deal) => {
    setEditingId(deal.id)
    setForm({
      title: deal.title,
      amount: deal.amount,
      stage: deal.stage,
      custom_data: deal.custom_data || {},
    })
    setModalOpen(true)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (editingId) await api.deals.update(editingId, form)
    else await api.deals.create(form)
    setModalOpen(false)
    load()
  }

  const handleDelete = async (id: number) => {
    if (!confirm(t.common.confirmDeleteDeal)) return
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
      title={pageTitle}
      action={canManage ? <button className="btn-primary flex items-center gap-2" onClick={openCreate}><Plus size={18} /> {t.deals.add}</button> : undefined}
    >
      <div className="md:hidden space-y-3">
        {deals.map((deal) => (
          <div key={deal.id} className="card p-4">
            <div className="flex items-start justify-between gap-2 mb-2">
              <h3 className="font-semibold">{deal.title}</h3>
              <span className={`shrink-0 px-2 py-0.5 rounded-full text-xs font-medium ${dealStages[deal.stage]?.color}`}>
                {dealStages[deal.stage]?.label}
              </span>
            </div>
            {!fieldHidden('deals', 'amount') && (
              <div className="text-xl font-bold text-kinetix-700 dark:text-kinetix-400 mb-1">{formatMoney(deal.amount)}</div>
            )}
            {deal.company_name && <p className="text-sm text-app-text-muted">{deal.company_name}</p>}
            {customListFields.map((f) => (
              <p key={f.key} className="text-sm text-app-text-muted">
                {locale === 'en' ? f.label_en : locale === 'ka' ? f.label_ka : f.label_ru}: {formatCustomValue(f, deal.custom_data?.[f.key], locale)}
              </p>
            ))}
            <select value={deal.stage} onChange={(e) => handleStageChange(deal.id, e.target.value)} className="mt-3 select-muted">
              {dealStageOrder.map((s) => <option key={s} value={s}>{dealStages[s]?.label}</option>)}
            </select>
            <CardActions canManage={canManage} onEdit={() => openEdit(deal)} onDelete={() => handleDelete(deal.id)} />
          </div>
        ))}
      </div>

      <div className="hidden md:flex gap-3 overflow-x-auto pb-4">
        {dealStageOrder.map((stage) => {
          const info = dealStages[stage]
          const stageDeals = deals.filter((d) => d.stage === stage)
          const total = stageDeals.reduce((s, d) => s + d.amount, 0)
          return (
            <div key={stage} className="min-w-[260px] flex-shrink-0">
              <div className="flex items-center justify-between mb-3">
                <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${info?.color}`}>{info?.label}</span>
                {!fieldHidden('deals', 'amount') && (
                  <span className="text-xs text-app-text-muted">{stageDeals.length} · {formatMoney(total)}</span>
                )}
              </div>
              <div className="space-y-3 min-h-[120px]">
                {stageDeals.map((deal) => (
                  <div key={deal.id} className="card p-4 hover:shadow-md transition-shadow">
                    <h3 className="font-medium text-sm mb-2">{deal.title}</h3>
                    {!fieldHidden('deals', 'amount') && (
                      <div className="text-lg font-bold text-kinetix-700 dark:text-kinetix-400 mb-2">{formatMoney(deal.amount)}</div>
                    )}
                    {deal.company_name && <div className="text-xs text-app-text-muted mb-1">{deal.company_name}</div>}
                    {customListFields.slice(0, 2).map((f) => (
                      <div key={f.key} className="text-xs text-app-text-muted">
                        {formatCustomValue(f, deal.custom_data?.[f.key], locale)}
                      </div>
                    ))}
                    <select value={deal.stage} onChange={(e) => handleStageChange(deal.id, e.target.value)} className="mt-2 select-muted text-xs py-1.5">
                      {dealStageOrder.map((s) => <option key={s} value={s}>{dealStages[s]?.label}</option>)}
                    </select>
                    <CardActions canManage={canManage} onEdit={() => openEdit(deal)} onDelete={() => handleDelete(deal.id)} />
                  </div>
                ))}
              </div>
            </div>
          )
        })}
      </div>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editingId ? t.deals.edit : t.deals.new}>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div><label className="label">{t.common.title} *</label><input className="input" required value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} /></div>
          {!fieldHidden('deals', 'amount') && (
            <div><label className="label">{t.common.amount}</label><input className="input" type="number" value={form.amount} onChange={(e) => setForm({ ...form, amount: +e.target.value })} /></div>
          )}
          <div>
            <label className="label">{t.common.stage}</label>
            <select className="input" value={form.stage} onChange={(e) => setForm({ ...form, stage: e.target.value })}>
              {dealStageOrder.map((s) => <option key={s} value={s}>{dealStages[s]?.label}</option>)}
            </select>
          </div>
          <CustomFieldsForm
            entity="deals"
            values={form.custom_data}
            onChange={(custom_data) => setForm({ ...form, custom_data })}
          />
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" className="btn-secondary" onClick={() => setModalOpen(false)}>{t.common.cancel}</button>
            <button type="submit" className="btn-primary">{editingId ? t.common.save : t.common.create}</button>
          </div>
        </form>
      </Modal>
    </Page>
  )
}
