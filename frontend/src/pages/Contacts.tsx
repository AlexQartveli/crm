import { useEffect, useState } from 'react'
import { Plus } from 'lucide-react'
import { api, Contact, Company } from '../api/client'
import Modal from '../components/Modal'
import CardActions, { RowActions } from '../components/CardActions'
import Page, { TableWrap, Loading, Empty } from '../components/Page'

const emptyForm = { name: '', phone: '', email: '', position: '', company_id: 0 }

export default function Contacts() {
  const [contacts, setContacts] = useState<Contact[]>([])
  const [companies, setCompanies] = useState<Company[]>([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [form, setForm] = useState(emptyForm)

  const load = async () => {
    setLoading(true)
    try {
      const [c, co] = await Promise.all([api.contacts.list(), api.companies.list()])
      setContacts(c)
      setCompanies(co)
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

  const openEdit = (c: Contact) => {
    setEditingId(c.id)
    setForm({
      name: c.name,
      phone: c.phone || '',
      email: c.email || '',
      position: c.position || '',
      company_id: c.company_id || 0,
    })
    setModalOpen(true)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const data = { ...form, company_id: form.company_id || undefined }
    if (editingId) {
      await api.contacts.update(editingId, data)
    } else {
      await api.contacts.create(data)
    }
    setModalOpen(false)
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
        <button className="btn-primary flex items-center gap-2" onClick={openCreate}>
          <Plus size={18} /> Добавить
        </button>
      }
    >
      {contacts.length === 0 ? (
        <Empty text="Нет контактов" />
      ) : (
        <>
          {/* Мобильные карточки */}
          <div className="md:hidden space-y-3">
            {contacts.map((c) => (
              <div key={c.id} className="card p-4">
                <h3 className="font-semibold text-base">{c.name}</h3>
                {c.position && <p className="text-sm text-gray-500 mt-0.5">{c.position}</p>}
                <p className="text-sm text-kinetix-600 mt-1">{companyName(c.company_id)}</p>
                <div className="mt-2 space-y-1 text-sm text-gray-600">
                  {c.phone && <p>{c.phone}</p>}
                  {c.email && <p>{c.email}</p>}
                </div>
                <CardActions onEdit={() => openEdit(c)} onDelete={() => handleDelete(c.id)} />
              </div>
            ))}
          </div>

          {/* Десктоп таблица */}
          <div className="hidden md:block">
            <TableWrap>
              <table className="w-full text-sm">
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
                        <RowActions onEdit={() => openEdit(c)} onDelete={() => handleDelete(c.id)} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </TableWrap>
          </div>
        </>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editingId ? 'Редактировать контакт' : 'Новый контакт'}>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label">Имя *</label>
            <input className="input" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          </div>
          <div>
            <label className="label">Телефон</label>
            <input className="input" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
          </div>
          <div>
            <label className="label">Email</label>
            <input className="input" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          </div>
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
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" className="btn-secondary" onClick={() => setModalOpen(false)}>Отмена</button>
            <button type="submit" className="btn-primary">{editingId ? 'Сохранить' : 'Создать'}</button>
          </div>
        </form>
      </Modal>
    </Page>
  )
}
