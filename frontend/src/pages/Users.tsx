import { useEffect, useState } from 'react'
import { Plus, Trash2, UserCog } from 'lucide-react'
import { api, UserRecord } from '../api/client'
import Modal from '../components/Modal'
import Page, { Loading } from '../components/Page'
import { useAuth } from '../auth/AuthContext'
import { ROLE_LABELS } from '../auth/permissions'
import { useI18n } from '../i18n/I18nContext'

const ROLES = ['admin', 'director', 'sales', 'operator', 'warehouse', 'accountant']

export default function Users() {
  const { t, locale } = useI18n()
  const { can } = useAuth()
  const [users, setUsers] = useState<UserRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [form, setForm] = useState({ username: '', password: '', full_name: '', email: '', role: 'sales' })

  const roleLabel = (role: string) => {
    const labels = ROLE_LABELS[role]
    if (!labels) return role
    return labels[locale] || labels.ru
  }

  const load = () => {
    setLoading(true)
    api.auth.users.list()
      .then(setUsers)
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  if (!can('users.manage')) {
    return <Page title={t.users.title}><p className="text-app-text-muted">{t.auth.accessDenied}</p></Page>
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    await api.auth.users.create(form)
    setModalOpen(false)
    setForm({ username: '', password: '', full_name: '', email: '', role: 'sales' })
    load()
  }

  const handleToggle = async (user: UserRecord) => {
    await api.auth.users.update(user.id, { is_active: !user.is_active })
    load()
  }

  const handleDelete = async (id: number) => {
    if (!confirm(t.users.confirmDelete)) return
    await api.auth.users.delete(id)
    load()
  }

  if (loading) return <Loading />

  return (
    <Page title={t.users.title}>
      <p className="text-app-text-muted mb-6 -mt-2">{t.users.subtitle}</p>

      <div className="flex justify-end mb-4">
        <button className="btn-primary flex items-center gap-2" onClick={() => setModalOpen(true)}>
          <Plus size={18} /> {t.users.add}
        </button>
      </div>

      <div className="card overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr>
              <th className="text-left p-4 font-medium">{t.auth.username}</th>
              <th className="text-left p-4 font-medium">{t.common.name}</th>
              <th className="text-left p-4 font-medium">{t.users.role}</th>
              <th className="text-left p-4 font-medium">{t.common.status}</th>
              <th className="p-4"></th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id}>
                <td className="p-4 font-medium">{user.username}</td>
                <td className="p-4">{user.full_name}</td>
                <td className="p-4">
                  <span className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-kinetix-100 text-kinetix-800 dark:bg-kinetix-900/40 dark:text-kinetix-200">
                    <UserCog size={12} />
                    {roleLabel(user.role)}
                  </span>
                </td>
                <td className="p-4">
                  <button
                    type="button"
                    className={`text-xs px-2 py-1 rounded-full ${user.is_active ? 'bg-green-100 text-green-800' : 'bg-slate-100 text-slate-600'}`}
                    onClick={() => handleToggle(user)}
                  >
                    {user.is_active ? t.users.active : t.users.inactive}
                  </button>
                </td>
                <td className="p-4 text-right">
                  <button className="text-red-400" onClick={() => handleDelete(user.id)}>
                    <Trash2 size={16} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={t.users.add}>
        <form onSubmit={handleCreate} className="space-y-4">
          <div><label className="label">{t.auth.username} *</label><input className="input" required value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} /></div>
          <div><label className="label">{t.common.name} *</label><input className="input" required value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} /></div>
          <div><label className="label">{t.common.email}</label><input className="input" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></div>
          <div><label className="label">{t.auth.password} *</label><input className="input" type="password" required value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></div>
          <div>
            <label className="label">{t.users.role}</label>
            <select className="input" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
              {ROLES.map((r) => <option key={r} value={r}>{roleLabel(r)}</option>)}
            </select>
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" className="btn-secondary" onClick={() => setModalOpen(false)}>{t.common.cancel}</button>
            <button type="submit" className="btn-primary">{t.common.create}</button>
          </div>
        </form>
      </Modal>
    </Page>
  )
}
