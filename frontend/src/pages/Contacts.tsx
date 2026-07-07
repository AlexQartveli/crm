import { useEffect, useState } from 'react'
import { Plus, Trash2 } from 'lucide-react'
import { api, Contact, Company } from '../api/client'
import Modal from '../components/Modal'
import { formatDate } from '../utils'

export default function Contacts() {
  const [contacts, setContacts] = useState<Contact[]>([])
  const [companies, setCompanies] = useState<Company[]>([])
  const [modalOpen, setModalOpen] = useState(false)
  const [form, setForm] = useState({ name: '', phone: '', email: '', position: '', company_id: 0 })

  const load = () => {
    api.contacts.list().then(setContacts).catch(console.error)
    api.companies.list().then(setCompanies).catch(console.error)
  }
  useEffect(() => { load() }, [])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    const data = { ...form, company_id: form.company_id || undefined }
    await api.contacts.create(data)
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

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Контакты</h1>
        <button className="btn-primary flex items-center gap-2" onClick={() => setModalOpen(true)}>
          <Plus size={18} /> Добавить контакт
        </button>
      </div>

      <div className="card overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left p-4 font-medium text-gray-600">Имя</th>
              <th className="text-left p-4 font-medium text-gray-600">Должность</th>
              <th className="text-left p-4 font-medium text-gray-600">Компания</th>
              <th className="text-left p-4 font-medium text-gray-600">Телефон</th>
              <th className="text-left p-4 font-medium text-gray-600">Email</th>
              <th className="text-left p-4 font-medium text-gray-600">Дата</th>
              <th className="p-4"></th>
            </tr>
          </thead>
          <tbody>
            {contacts.map((c) => (
              <tr key={c.id} className="border-b hover:bg-gray-50">
                <td className="p-4 font-medium">{c.name}</td>
                <td className="p-4">{c.position || '—'}</td>
                <td className="p-4">{companyName(c.company_id)}</td>
                <td className="p-4">{c.phone || '—'}</td>
                <td className="p-4">{c.email || '—'}</td>
                <td className="p-4 text-gray-500">{formatDate(c.created_at)}</td>
                <td className="p-4">
                  <button onClick={() => handleDelete(c.id)} className="text-red-400 hover:text-red-600">
                    <Trash2 size={16} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

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
    </div>
  )
}
