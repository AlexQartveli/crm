import { useEffect, useState } from 'react'
import { Plus, Send, CheckCircle, FileText } from 'lucide-react'
import { api, TaxInvoice, Deal, Company } from '../api/client'
import Modal from '../components/Modal'
import Page, { TableWrap, Loading } from '../components/Page'
import { useI18n } from '../i18n/I18nContext'
import { useStatuses, formatMoney } from '../utils'

export default function Accounting() {
  const { t } = useI18n()
  const { invoiceStatuses } = useStatuses()
  const [invoices, setInvoices] = useState<TaxInvoice[]>([])
  const [deals, setDeals] = useState<Deal[]>([])
  const [companies, setCompanies] = useState<Company[]>([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [form, setForm] = useState({
    deal_id: 0,
    company_id: 0,
    tin_seller: '123456789',
    tin_buyer: '',
    buyer_name: '',
    amount: 0,
    description: '',
  })

  const load = async () => {
    setLoading(true)
    try {
      const [inv, d, c] = await Promise.all([
        api.accounting.invoices.list(),
        api.deals.list(),
        api.companies.list(),
      ])
      setInvoices(inv)
      setDeals(d)
      setCompanies(c)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    const company = companies.find((c) => c.id === form.company_id)
    await api.accounting.invoices.create({
      ...form,
      deal_id: form.deal_id || undefined,
      company_id: form.company_id || undefined,
      tin_buyer: form.tin_buyer || company?.inn || '',
      buyer_name: form.buyer_name || company?.name,
    })
    setModalOpen(false)
    load()
  }

  const handleSync = async (id: number) => {
    await api.accounting.invoices.sync(id)
    load()
  }

  const handleActivate = async (id: number) => {
    await api.accounting.invoices.activate(id)
    load()
  }

  const onDealSelect = (dealId: number) => {
    const deal = deals.find((d) => d.id === dealId)
    const company = companies.find((c) => c.id === deal?.company_id)
    setForm({
      ...form,
      deal_id: dealId,
      company_id: deal?.company_id || 0,
      amount: deal?.amount || 0,
      tin_buyer: company?.inn || '',
      buyer_name: company?.name || '',
      description: deal?.title || '',
    })
  }

  if (loading) return <Loading />

  return (
    <Page
      title={t.accounting.title}
      action={
        <button className="btn-primary flex items-center gap-2" onClick={() => setModalOpen(true)}>
          <Plus size={18} /> {t.accounting.newInvoice}
        </button>
      }
    >
      <div className="card p-4 mb-6 bg-kinetix-50 border-kinetix-200">
        <div className="flex items-center gap-3">
          <FileText className="text-kinetix-600" size={24} />
          <div>
            <h3 className="font-semibold text-kinetix-800">{t.accounting.rsgeTitle}</h3>
            <p className="text-sm text-kinetix-600">{t.accounting.rsgeDesc}</p>
          </div>
        </div>
      </div>

      <TableWrap>
        <table className="w-full text-sm min-w-[700px]">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left p-3 font-medium text-gray-600">{t.common.number}</th>
              <th className="text-left p-3 font-medium text-gray-600">{t.common.buyer}</th>
              <th className="text-left p-3 font-medium text-gray-600">{t.common.tin}</th>
              <th className="text-right p-3 font-medium text-gray-600">{t.common.amount}</th>
              <th className="text-right p-3 font-medium text-gray-600">{t.common.vat}</th>
              <th className="text-right p-3 font-medium text-gray-600">{t.common.total}</th>
              <th className="text-left p-3 font-medium text-gray-600">{t.common.status}</th>
              <th className="text-left p-3 font-medium text-gray-600">{t.common.rsgeId}</th>
              <th className="p-3"></th>
            </tr>
          </thead>
          <tbody>
            {invoices.map((inv) => (
              <tr key={inv.id} className="border-b hover:bg-gray-50">
                <td className="p-3 font-medium">{inv.number}</td>
                <td className="p-3">{inv.buyer_name || inv.company_name || t.common.dash}</td>
                <td className="p-3 text-gray-500">{inv.tin_buyer}</td>
                <td className="p-3 text-right">{formatMoney(inv.amount)}</td>
                <td className="p-3 text-right text-orange-600">{formatMoney(inv.vat_amount)}</td>
                <td className="p-3 text-right font-medium">{formatMoney(inv.total_amount)}</td>
                <td className="p-3">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${invoiceStatuses[inv.status]?.color || ''}`}>
                    {invoiceStatuses[inv.status]?.label || inv.status}
                  </span>
                </td>
                <td className="p-3 text-xs text-gray-500">
                  {inv.rsge_invoice_id ? `#${inv.rsge_invoice_id}` : t.common.dash}
                </td>
                <td className="p-3">
                  <div className="flex gap-1">
                    {inv.status === 'draft' && (
                      <button onClick={() => handleSync(inv.id)} className="p-1.5 text-blue-600 hover:bg-blue-50 rounded" title={t.common.sendToRsge}>
                        <Send size={16} />
                      </button>
                    )}
                    {inv.status === 'sent' && (
                      <button onClick={() => handleActivate(inv.id)} className="p-1.5 text-green-600 hover:bg-green-50 rounded" title={t.common.activate}>
                        <CheckCircle size={16} />
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </TableWrap>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={t.accounting.newTaxInvoice}>
        <form onSubmit={handleCreate} className="space-y-4">
          <div>
            <label className="label">{t.common.deal}</label>
            <select className="input" value={form.deal_id} onChange={(e) => onDealSelect(+e.target.value)}>
              <option value={0}>{t.common.select}</option>
              {deals.map((d) => (
                <option key={d.id} value={d.id}>{d.title} ({formatMoney(d.amount)})</option>
              ))}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">{t.common.sellerTin} *</label>
              <input className="input" required value={form.tin_seller} onChange={(e) => setForm({ ...form, tin_seller: e.target.value })} />
            </div>
            <div>
              <label className="label">{t.common.buyerTin} *</label>
              <input className="input" required value={form.tin_buyer} onChange={(e) => setForm({ ...form, tin_buyer: e.target.value })} />
            </div>
          </div>
          <div>
            <label className="label">{t.common.buyerName}</label>
            <input className="input" value={form.buyer_name} onChange={(e) => setForm({ ...form, buyer_name: e.target.value })} />
          </div>
          <div>
            <label className="label">{t.common.amountNoVat}</label>
            <input className="input" type="number" value={form.amount} onChange={(e) => setForm({ ...form, amount: +e.target.value })} />
          </div>
          <div>
            <label className="label">{t.common.description}</label>
            <input className="input" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
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
