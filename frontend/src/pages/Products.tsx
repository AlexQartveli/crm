import { useEffect, useState } from 'react'
import { Plus } from 'lucide-react'
import { api, Product } from '../api/client'
import Modal from '../components/Modal'
import CardActions, { RowActions } from '../components/CardActions'
import Page, { TableWrap, Loading, Empty } from '../components/Page'
import { formatMoney } from '../utils'

const emptyForm = { name: '', sku: '', unit: 'шт', price: 0, description: '' }

export default function Products() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [form, setForm] = useState(emptyForm)

  const load = async () => {
    setLoading(true)
    try {
      setProducts(await api.products.list())
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

  const openEdit = (p: Product) => {
    setEditingId(p.id)
    setForm({
      name: p.name,
      sku: p.sku || '',
      unit: p.unit,
      price: p.price,
      description: p.description || '',
    })
    setModalOpen(true)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (editingId) {
      await api.products.update(editingId, form)
    } else {
      await api.products.create(form)
    }
    setModalOpen(false)
    load()
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Удалить товар?')) return
    await api.products.delete(id)
    load()
  }

  if (loading) return <Loading />

  return (
    <Page
      title="Товары"
      action={
        <button className="btn-primary flex items-center gap-2" onClick={openCreate}>
          <Plus size={18} /> Добавить
        </button>
      }
    >
      {products.length === 0 ? (
        <Empty text="Нет товаров" />
      ) : (
        <>
          <div className="md:hidden space-y-3">
            {products.map((p) => (
              <div key={p.id} className="card p-4">
                <h3 className="font-semibold">{p.name}</h3>
                {p.sku && <p className="text-sm text-gray-500 mt-0.5">Арт: {p.sku}</p>}
                <div className="flex justify-between items-center mt-2">
                  <span className="text-lg font-bold text-kinetix-700">{formatMoney(p.price)}</span>
                  <span className={`text-sm font-medium ${p.total_stock > 0 ? 'text-green-600' : 'text-red-500'}`}>
                    На складе: {p.total_stock} {p.unit}
                  </span>
                </div>
                <CardActions onEdit={() => openEdit(p)} onDelete={() => handleDelete(p.id)} />
              </div>
            ))}
          </div>

          <div className="hidden md:block">
            <TableWrap>
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="text-left p-3 font-medium text-gray-600">Название</th>
                    <th className="text-left p-3 font-medium text-gray-600">Артикул</th>
                    <th className="text-right p-3 font-medium text-gray-600">Цена</th>
                    <th className="text-right p-3 font-medium text-gray-600">На складе</th>
                    <th className="p-3"></th>
                  </tr>
                </thead>
                <tbody>
                  {products.map((p) => (
                    <tr key={p.id} className="border-b hover:bg-gray-50">
                      <td className="p-3 font-medium">{p.name}</td>
                      <td className="p-3 text-gray-500">{p.sku || '—'}</td>
                      <td className="p-3 text-right">{formatMoney(p.price)}</td>
                      <td className="p-3 text-right">
                        <span className={p.total_stock > 0 ? 'text-green-600 font-medium' : 'text-red-500'}>
                          {p.total_stock}
                        </span>
                      </td>
                      <td className="p-3">
                        <RowActions onEdit={() => openEdit(p)} onDelete={() => handleDelete(p.id)} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </TableWrap>
          </div>
        </>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editingId ? 'Редактировать товар' : 'Новый товар'}>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label">Название *</label>
            <input className="input" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          </div>
          <div>
            <label className="label">Артикул</label>
            <input className="input" value={form.sku} onChange={(e) => setForm({ ...form, sku: e.target.value })} />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Единица</label>
              <input className="input" value={form.unit} onChange={(e) => setForm({ ...form, unit: e.target.value })} />
            </div>
            <div>
              <label className="label">Цена</label>
              <input className="input" type="number" value={form.price} onChange={(e) => setForm({ ...form, price: +e.target.value })} />
            </div>
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
