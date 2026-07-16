import { useEffect, useState } from 'react'
import { Plus, Trash2 } from 'lucide-react'
import { api, Company } from '../api/client'
import CustomFieldsForm from '../components/CustomFieldsForm'
import Modal from '../components/Modal'
import { useCrmConfig } from '../crm/CrmConfigContext'
import { formatCustomValue } from '../crm/helpers'
import { useI18n } from '../i18n/I18nContext'
import { formatDate } from '../utils'

const emptyForm = { name: '', inn: '', phone: '', email: '', address: '', custom_data: {} as Record<string, unknown> }

export default function Companies() {
  const { t, locale } = useI18n()
  const { entityLabel, listFieldsFor } = useCrmConfig()
  const customListFields = listFieldsFor('companies')
  const pageTitle = entityLabel('companies', t.companies.title)
  const [companies, setCompanies] = useState<Company[]>([])
  const [modalOpen, setModalOpen] = useState(false)
  const [form, setForm] = useState(emptyForm)

  const load = () => api.companies.list().then(setCompanies).catch(console.error)
  useEffect(() => { load() }, [])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    await api.companies.create(form)
    setModalOpen(false)
    setForm(emptyForm)
    load()
  }

  const handleDelete = async (id: number) => {
    if (!confirm(t.common.confirmDeleteCompany)) return
    await api.companies.delete(id)
    load()
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="page-title">{pageTitle}</h1>
        <button className="btn-primary flex items-center gap-2" onClick={() => setModalOpen(true)}>
          <Plus size={18} /> {t.companies.add}
        </button>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {companies.map((c) => (
          <div key={c.id} className="card p-5 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-3">
              <h3 className="font-semibold text-lg">{c.name}</h3>
              <button onClick={() => handleDelete(c.id)} className="text-red-400 hover:text-red-600">
                <Trash2 size={16} />
              </button>
            </div>
            {c.inn && <div className="text-sm text-app-text-muted mb-1">{t.common.inn}: {c.inn}</div>}
            {c.phone && <div className="text-sm text-app-text-secondary mb-1">{c.phone}</div>}
            {c.email && <div className="text-sm text-app-text-secondary mb-1">{c.email}</div>}
            {c.address && <div className="text-sm text-app-text-muted">{c.address}</div>}
            {customListFields.map((f) => (
              <div key={f.key} className="text-sm text-app-text-muted mt-1">
                {locale === 'en' ? f.label_en : locale === 'ka' ? f.label_ka : f.label_ru}: {formatCustomValue(f, c.custom_data?.[f.key], locale)}
              </div>
            ))}
            <div className="text-xs text-app-text-muted mt-3">{formatDate(c.created_at)}</div>
          </div>
        ))}
      </div>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={t.companies.new}>
        <form onSubmit={handleCreate} className="space-y-4">
          <div>
            <label className="label">{t.common.name} *</label>
            <input className="input" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          </div>
          <div>
            <label className="label">{t.common.inn}</label>
            <input className="input" value={form.inn} onChange={(e) => setForm({ ...form, inn: e.target.value })} />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">{t.common.phone}</label>
              <input className="input" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
            </div>
            <div>
              <label className="label">{t.common.email}</label>
              <input className="input" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
            </div>
          </div>
          <div>
            <label className="label">{t.common.address}</label>
            <input className="input" value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} />
          </div>
          <CustomFieldsForm entity="companies" values={form.custom_data} onChange={(custom_data) => setForm({ ...form, custom_data })} />
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" className="btn-secondary" onClick={() => setModalOpen(false)}>{t.common.cancel}</button>
            <button type="submit" className="btn-primary">{t.common.create}</button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
