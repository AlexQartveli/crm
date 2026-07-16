import { useEffect, useState } from 'react'
import { Plus } from 'lucide-react'
import { api, Product } from '../api/client'
import CustomFieldsForm from '../components/CustomFieldsForm'
import Modal from '../components/Modal'
import CardActions, { RowActions } from '../components/CardActions'
import Page, { TableWrap, Loading, Empty } from '../components/Page'
import { useCrmConfig } from '../crm/CrmConfigContext'
import { formatCustomValue } from '../crm/helpers'
import { useI18n } from '../i18n/I18nContext'
import { formatMoney } from '../utils'

const emptyForm = { name: '', sku: '', unit: 'шт', price: 0, description: '', custom_data: {} as Record<string, unknown> }

export default function Products() {
  const { t, locale } = useI18n()
  const { entityLabel, listFieldsFor } = useCrmConfig()
  const customListFields = listFieldsFor('products')
  const pageTitle = entityLabel('products', t.products.title)
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [form, setForm] = useState(emptyForm)

  const load = async () => {
    setLoading(true)
    try { setProducts(await api.products.list()) } finally { setLoading(false) }
  }
  useEffect(() => { load() }, [])

  const openCreate = () => { setEditingId(null); setForm(emptyForm); setModalOpen(true) }
  const openEdit = (p: Product) => {
    setEditingId(p.id)
    setForm({ name: p.name, sku: p.sku || '', unit: p.unit, price: p.price, description: p.description || '', custom_data: p.custom_data || {} })
    setModalOpen(true)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (editingId) await api.products.update(editingId, form)
    else await api.products.create(form)
    setModalOpen(false)
    load()
  }

  const handleDelete = async (id: number) => {
    if (!confirm(t.common.confirmDeleteProduct)) return
    await api.products.delete(id)
    load()
  }

  if (loading) return <Loading />

  return (
    <Page
      title={pageTitle}
      action={<button className="btn-primary flex items-center gap-2" onClick={openCreate}><Plus size={18} /> {t.common.add}</button>}
    >
      {products.length === 0 ? (
        <Empty text={t.common.noProducts} />
      ) : (
        <>
          <div className="md:hidden space-y-3">
            {products.map((p) => (
              <div key={p.id} className="card p-4">
                <h3 className="font-semibold">{p.name}</h3>
                {p.sku && <p className="text-sm text-app-text-muted mt-0.5">{t.products.art}: {p.sku}</p>}
                <div className="flex justify-between items-center mt-2">
                  <span className="text-lg font-bold text-kinetix-700 dark:text-kinetix-400">{formatMoney(p.price)}</span>
                  <span className={`text-sm font-medium ${p.total_stock > 0 ? 'text-green-600 dark:text-green-400' : 'text-red-500 dark:text-red-400'}`}>
                    {t.common.inStock}: {p.total_stock} {p.unit}
                  </span>
                </div>
                <CardActions onEdit={() => openEdit(p)} onDelete={() => handleDelete(p.id)} />
              </div>
            ))}
          </div>
          <div className="hidden md:block">
            <TableWrap>
              <table className="w-full text-sm">
                <thead>
                  <tr>
                    <th className="text-left p-3 font-medium">{t.common.name}</th>
                    <th className="text-left p-3 font-medium">{t.common.sku}</th>
                    <th className="text-right p-3 font-medium">{t.common.price}</th>
                    <th className="text-right p-3 font-medium">{t.common.inStock}</th>
                    {customListFields.map((f) => (
                      <th key={f.key} className="text-left p-3 font-medium">
                        {locale === 'en' ? f.label_en : locale === 'ka' ? f.label_ka : f.label_ru}
                      </th>
                    ))}
                    <th className="p-3"></th>
                  </tr>
                </thead>
                <tbody>
                  {products.map((p) => (
                    <tr key={p.id}>
                      <td className="p-3 font-medium">{p.name}</td>
                      <td className="p-3 text-app-text-muted">{p.sku || t.common.dash}</td>
                      <td className="p-3 text-right">{formatMoney(p.price)}</td>
                      <td className="p-3 text-right"><span className={p.total_stock > 0 ? 'text-green-600 dark:text-green-400 font-medium' : 'text-red-500 dark:text-red-400'}>{p.total_stock}</span></td>
                      {customListFields.map((f) => (
                        <td key={f.key} className="p-3">{formatCustomValue(f, p.custom_data?.[f.key], locale)}</td>
                      ))}
                      <td className="p-3"><RowActions onEdit={() => openEdit(p)} onDelete={() => handleDelete(p.id)} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </TableWrap>
          </div>
        </>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editingId ? t.products.edit : t.products.new}>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div><label className="label">{t.common.name} *</label><input className="input" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></div>
          <div><label className="label">{t.common.sku}</label><input className="input" value={form.sku} onChange={(e) => setForm({ ...form, sku: e.target.value })} /></div>
          <div className="grid grid-cols-2 gap-4">
            <div><label className="label">{t.common.unit}</label><input className="input" value={form.unit} onChange={(e) => setForm({ ...form, unit: e.target.value })} /></div>
            <div><label className="label">{t.common.price}</label><input className="input" type="number" value={form.price} onChange={(e) => setForm({ ...form, price: +e.target.value })} /></div>
          </div>
          <CustomFieldsForm entity="products" values={form.custom_data} onChange={(custom_data) => setForm({ ...form, custom_data })} />
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" className="btn-secondary" onClick={() => setModalOpen(false)}>{t.common.cancel}</button>
            <button type="submit" className="btn-primary">{editingId ? t.common.save : t.common.create}</button>
          </div>
        </form>
      </Modal>
    </Page>
  )
}
