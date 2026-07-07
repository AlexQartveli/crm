import { useEffect, useState } from 'react'
import { Plus, Trash2 } from 'lucide-react'
import { api, Contact, Company } from '../api/client'
import Modal from '../components/Modal'
import Page, { TableWrap, Loading, Empty } from '../components/Page'

export default function Contacts() {
  const [contacts, setContacts] = useState<Contact[]>([])
  const [companies, setCompanies] = useState<Company[]>([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [form, setForm] = useState({ name: '', phone: '', email: '', position: '', company_id: 0 })

  const load = async () => {
    setLoading(true)
    try {
      const [c, co] = await Promise.all([api.contacts.list(), api.companies.list()])
      setContacts(c)
      setCompanies(co)
    } finally {
      setLoading(false)
    }
  }
  useEffect(() => { load() }, [])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    await api.contacts.create({ ...form, company_id: form.company_id || undefined })
    setModalOpen(false)
    setForm({ name: '', phone: '', email: '', position: '', company_id: 0 })
    load()
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Удалить контакт?')) return
    await api.contacts.delete(id)
    load()
  }

  const companyName = (id?: number) => companies.find((c) => c.id === id)?.name || '—'

  if (loading) return <Loading />

  return (
    <Page
      title="Контакты"
      action={
        <button className="btn-primary flex items-center gap-2" onClick={() => setModalOpen(true)}>
          <Plus size={18} /> Добавить
        </button>
      }
    >
      {contacts.length === 0 ? (
        <Empty text="Нет контактов" />
      ) : (
        <TableWrap>
          <table className="w-full text-sm min-w-[600px]">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left p-3 font-medium text-gray-600">Имя</th>
                <th className="text-left p-3 font-medium text-gray-600">Должность</th>
                <th className="text-left p-3 font-medium text-gray-600">Компания</th>
                <th className="text-left p-3 font-medium text-gray-600">Телефон</th>
                <th className="text-left p-3 font-medium text-gray-600">Email</th>
                <th className="p-3"></th>
              </tr>
            </thead>
            <tbody>
              {contacts.map((c) => (
                <tr key={c.id} className="border-b hover:bg-gray-50">
                  <td className="p-3 font-medium">{c.name}</td>
                  <td className="p-3">{c.position || '—'}</td>
                  <td className="p-3">{companyName(c.company_id)}</td>
                  <td className="p-3">{c.phone || '—'}</td>
                  <td className="p-3">{c.email || '—'}</td>
                  <td className="p-3">
                    <button onClick={() => handleDelete(c.id)} className="text-red-400 hover:text-red-600">
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </TableWrap>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Новый контакт">
        <form onSubmit={handleCreate} className="space-y-4">
          <div>
            <label className="label">Имя *</label>
            <input className="input" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Телефон</label>
              <input className="input" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
            </div>
            <div>
              <label className="label">Email</label>
              <input className="input" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Должность</label>
              <input className="input" value={form.position} onChange={(e) => setForm({ ...form, position: e.target.value })} />
            </div>
            <div>
              <label className="label">Компания</label>
              <select className="input" value={form.company_id} onChange={(e) => setForm({ ...form, company_id: +e.target.value })}>
                <option value={0}>—</option>
                {companies.map((c) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>
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
