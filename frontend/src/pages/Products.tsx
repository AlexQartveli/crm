import { useEffect, useState } from 'react'
import { Plus, Trash2 } from 'lucide-react'
import { api, Product } from '../api/client'
import Modal from '../components/Modal'
import { formatMoney } from '../utils'

export default function Products() {
  const [products, setProducts] = useState<Product[]>([])
  const [modalOpen, setModalOpen] = useState(false)
  const [form, setForm] = useState({ name: '', sku: '', unit: 'шт', price: 0, description: '' })

  const load = () => api.products.list().then(setProducts).catch(console.error)
  useEffect(() => { load() }, [])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    await api.products.create(form)
    setModalOpen(false)
    setForm({ name: '', sku: '', unit: 'шт', price: 0, description: '' })
    load()
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Удалить товар?')) return
    await api.products.delete(id)
    load()
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Товары</h1>
        <button className="btn-primary flex items-center gap-2" onClick={() => setModalOpen(true)}>
          <Plus size={18} /> Добавить товар
        </button>
      </div>

      <div className="card overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left p-4 font-medium text-gray-600">Название</th>
              <th className="text-left p-4 font-medium text-gray-600">Артикул</th>
              <th className="text-left p-4 font-medium text-gray-600">Ед.</th>
              <th className="text-right p-4 font-medium text-gray-600">Цена</th>
              <th className="text-right p-4 font-medium text-gray-600">На складе</th>
              <th className="p-4"></th>
            </tr>
          </thead>
          <tbody>
            {products.map((p) => (
              <tr key={p.id} className="border-b hover:bg-gray-50">
                <td className="p-4 font-medium">{p.name}</td>
                <td className="p-4 text-gray-500">{p.sku || '—'}</td>
                <td className="p-4">{p.unit}</td>
                <td className="p-4 text-right">{formatMoney(p.price)}</td>
                <td className="p-4 text-right">
                  <span className={p.total_stock > 0 ? 'text-green-600 font-medium' : 'text-red-500'}>
                    {p.total_stock}
                  </span>
                </td>
                <td className="p-4">
                  <button onClick={() => handleDelete(p.id)} className="text-red-400 hover:text-red-600">
                    <Trash2 size={16} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Новый товар">
        <form onSubmit={handleCreate} className="space-y-4">
          <div>
            <label className="label">Название *</label>
            <input className="input" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="label">Артикул</label>
              <input className="input" value={form.sku} onChange={(e) => setForm({ ...form, sku: e.target.value })} />
            </div>
            <div>
              <label className="label">Единица</label>
              <input className="input" value={form.unit} onChange={(e) => setForm({ ...form, unit: e.target.value })} />
            </div>
            <div>
              <label className="label">Цена</label>
              <input className="input" type="number" value={form.price} onChange={(e) => setForm({ ...form, price: +e.target.value })} />
            </div>
          </div>
          <div>
            <label className="label">Описание</label>
            <textarea className="input" rows={3} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
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
