import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Trash2, MessageCircle } from 'lucide-react'
import { api, Lead } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import { PERM } from '../auth/permissions'
import Modal from '../components/Modal'
import { useI18n } from '../i18n/I18nContext'
import { useStatuses, formatDate, formatMoney } from '../utils'

export default function Leads() {
  const { t } = useI18n()
  const { can } = useAuth()
  const canManage = can(PERM.leadsManage)
  const { leadStatuses } = useStatuses()
  const [leads, setLeads] = useState<Lead[]>([])
  const [modalOpen, setModalOpen] = useState(false)
  const [form, setForm] = useState({ title: '', name: '', phone: '', email: '', source: '', amount: 0 })
  const [convCounts, setConvCounts] = useState<Record<number, number>>({})

  const load = () => {
    Promise.all([api.leads.list(), api.messaging.conversations.list()])
      .then(([leads, convos]) => {
        setLeads(leads)
        const counts: Record<number, number> = {}
        for (const conv of convos) {
          if (conv.lead_id) counts[conv.lead_id] = (counts[conv.lead_id] || 0) + 1
        }
        setConvCounts(counts)
      })
      .catch(console.error)
  }
  useEffect(() => { load() }, [])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    await api.leads.create(form)
    setModalOpen(false)
    setForm({ title: '', name: '', phone: '', email: '', source: '', amount: 0 })
    load()
  }

  const handleDelete = async (id: number) => {
    if (!confirm(t.common.confirmDeleteLead)) return
    await api.leads.delete(id)
    load()
  }

  const handleStatusChange = async (id: number, status: string) => {
    await api.leads.update(id, { status })
    load()
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="page-title">{t.leads.title}</h1>
        {canManage && (
        <button className="btn-primary flex items-center gap-2" onClick={() => setModalOpen(true)}>
          <Plus size={18} /> {t.leads.add}
        </button>
        )}
      </div>

      <div className="card overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr>
              <th className="text-left p-4 font-medium">{t.common.title}</th>
              <th className="text-left p-4 font-medium">{t.common.contact}</th>
              <th className="text-left p-4 font-medium">{t.common.phone}</th>
              <th className="text-left p-4 font-medium">{t.common.source}</th>
              <th className="text-left p-4 font-medium">{t.common.status}</th>
              <th className="text-right p-4 font-medium">{t.common.amount}</th>
              <th className="text-left p-4 font-medium">{t.common.date}</th>
              <th className="text-left p-4 font-medium">{t.leads.messengerDialogs}</th>
              <th className="p-4"></th>
            </tr>
          </thead>
          <tbody>
            {leads.map((lead) => (
              <tr key={lead.id}>
                <td className="p-4 font-medium">{lead.title}</td>
                <td className="p-4">{lead.name || t.common.dash}</td>
                <td className="p-4">{lead.phone || t.common.dash}</td>
                <td className="p-4">{lead.source || t.common.dash}</td>
                <td className="p-4">
                  {canManage ? (
                  <select
                    value={lead.status}
                    onChange={(e) => handleStatusChange(lead.id, e.target.value)}
                    className={`text-xs font-medium px-2 py-1 rounded-full border-0 cursor-pointer ${leadStatuses[lead.status]?.color || ''}`}
                  >
                    {Object.entries(leadStatuses).map(([k, v]) => (
                      <option key={k} value={k}>{v.label}</option>
                    ))}
                  </select>
                  ) : (
                    <span className={`text-xs font-medium px-2 py-1 rounded-full ${leadStatuses[lead.status]?.color || ''}`}>
                      {leadStatuses[lead.status]?.label || lead.status}
                    </span>
                  )}
                </td>
                <td className="p-4 text-right">{formatMoney(lead.amount)}</td>
                <td className="p-4 text-app-text-muted">{formatDate(lead.created_at)}</td>
                <td className="p-4">
                  {convCounts[lead.id] ? (
                    <Link to="/inbox" className="inline-flex items-center gap-1 text-kinetix-600 dark:text-kinetix-400">
                      <MessageCircle size={14} />
                      {convCounts[lead.id]}
                    </Link>
                  ) : t.common.dash}
                </td>
                <td className="p-4">
                  {canManage && (
                  <button onClick={() => handleDelete(lead.id)} className="text-red-400 hover:text-red-500 dark:text-red-400 dark:hover:text-red-300">
                    <Trash2 size={16} />
                  </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={t.leads.new}>
        <form onSubmit={handleCreate} className="space-y-4">
          <div>
            <label className="label">{t.common.title} *</label>
            <input className="input" required value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">{t.common.personName}</label>
              <input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
            </div>
            <div>
              <label className="label">{t.common.phone}</label>
              <input className="input" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">{t.common.email}</label>
              <input className="input" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
            </div>
            <div>
              <label className="label">{t.common.source}</label>
              <input className="input" value={form.source} onChange={(e) => setForm({ ...form, source: e.target.value })} />
            </div>
          </div>
          <div>
            <label className="label">{t.common.amount}</label>
            <input className="input" type="number" value={form.amount} onChange={(e) => setForm({ ...form, amount: +e.target.value })} />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" className="btn-secondary" onClick={() => setModalOpen(false)}>{t.common.cancel}</button>
            <button type="submit" className="btn-primary">{t.common.create}</button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
