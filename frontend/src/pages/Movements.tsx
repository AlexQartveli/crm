import { useEffect, useState } from 'react'
import { Plus } from 'lucide-react'
import { api, Product, StockMovement, Warehouse } from '../api/client'
import Modal from '../components/Modal'
import { useI18n } from '../i18n/I18nContext'
import { useStatuses, formatDate } from '../utils'

export default function Movements() {
  const { t } = useI18n()
  const { movementTypes } = useStatuses()
  const [movements, setMovements] = useState<StockMovement[]>([])
  const [products, setProducts] = useState<Product[]>([])
  const [warehouses, setWarehouses] = useState<Warehouse[]>([])
  const [modalOpen, setModalOpen] = useState(false)
  const [form, setForm] = useState({
    product_id: 0,
    warehouse_id: 0,
    movement_type: 'receipt',
    quantity: 1,
    to_warehouse_id: 0,
    comment: '',
  })

  const load = () => {
    api.movements.list().then(setMovements).catch(console.error)
    api.products.list().then(setProducts).catch(console.error)
    api.warehouses.list().then(setWarehouses).catch(console.error)
  }
  useEffect(() => { load() }, [])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    const data = {
      ...form,
      to_warehouse_id: form.movement_type === 'transfer' ? form.to_warehouse_id : undefined,
    }
    await api.movements.create(data)
    setModalOpen(false)
    setForm({ product_id: 0, warehouse_id: 0, movement_type: 'receipt', quantity: 1, to_warehouse_id: 0, comment: '' })
    load()
  }

  const typeColor = (type: string) => {
    switch (type) {
      case 'receipt': return 'bg-green-100 text-green-800'
      case 'expense': return 'bg-red-100 text-red-800'
      case 'transfer': return 'bg-blue-100 text-blue-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">{t.movements.title}</h1>
        <button className="btn-primary flex items-center gap-2" onClick={() => setModalOpen(true)}>
          <Plus size={18} /> {t.common.newMovement}
        </button>
      </div>

      <div className="card overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left p-4 font-medium text-gray-600">{t.common.date}</th>
              <th className="text-left p-4 font-medium text-gray-600">{t.common.type}</th>
              <th className="text-left p-4 font-medium text-gray-600">{t.common.product}</th>
              <th className="text-left p-4 font-medium text-gray-600">{t.common.warehouse}</th>
              <th className="text-right p-4 font-medium text-gray-600">{t.common.qty}</th>
              <th className="text-left p-4 font-medium text-gray-600">{t.common.comment}</th>
            </tr>
          </thead>
          <tbody>
            {movements.map((m) => (
              <tr key={m.id} className="border-b hover:bg-gray-50">
                <td className="p-4 text-gray-500">{formatDate(m.created_at)}</td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${typeColor(m.movement_type)}`}>
                    {movementTypes[m.movement_type as keyof typeof movementTypes] ?? m.movement_type}
                  </span>
                </td>
                <td className="p-4 font-medium">{m.product_name}</td>
                <td className="p-4">{m.warehouse_name}</td>
                <td className="p-4 text-right font-medium">{m.quantity}</td>
                <td className="p-4 text-gray-500">{m.comment || t.common.dash}</td>
              </tr>
            ))}
            {movements.length === 0 && (
              <tr>
                <td colSpan={6} className="p-8 text-center text-gray-400">{t.common.noMovements}</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={t.common.newMovement}>
        <form onSubmit={handleCreate} className="space-y-4">
          <div>
            <label className="label">{t.common.movementType}</label>
            <select className="input" value={form.movement_type} onChange={(e) => setForm({ ...form, movement_type: e.target.value })}>
              {Object.entries(movementTypes).map(([k, v]) => (
                <option key={k} value={k}>{v}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">{t.common.product} *</label>
            <select className="input" required value={form.product_id} onChange={(e) => setForm({ ...form, product_id: +e.target.value })}>
              <option value={0}>{t.common.selectProduct}</option>
              {products.map((p) => (
                <option key={p.id} value={p.id}>{p.name} ({p.sku})</option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">{t.common.warehouse} *</label>
            <select className="input" required value={form.warehouse_id} onChange={(e) => setForm({ ...form, warehouse_id: +e.target.value })}>
              <option value={0}>{t.common.selectWarehouse}</option>
              {warehouses.map((w) => (
                <option key={w.id} value={w.id}>{w.name}</option>
              ))}
            </select>
          </div>
          {form.movement_type === 'transfer' && (
            <div>
              <label className="label">{t.common.destWarehouse} *</label>
              <select className="input" required value={form.to_warehouse_id} onChange={(e) => setForm({ ...form, to_warehouse_id: +e.target.value })}>
                <option value={0}>{t.common.selectWarehouse}</option>
                {warehouses.filter((w) => w.id !== form.warehouse_id).map((w) => (
                  <option key={w.id} value={w.id}>{w.name}</option>
                ))}
              </select>
            </div>
          )}
          <div>
            <label className="label">{t.common.quantity} *</label>
            <input className="input" type="number" min={0.01} step={0.01} required value={form.quantity} onChange={(e) => setForm({ ...form, quantity: +e.target.value })} />
          </div>
          <div>
            <label className="label">{t.common.comment}</label>
            <input className="input" value={form.comment} onChange={(e) => setForm({ ...form, comment: e.target.value })} />
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
