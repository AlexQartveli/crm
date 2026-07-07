import { useEffect, useState } from 'react'
import { Link2, Shield, Search } from 'lucide-react'
import { api, RsgeSettings } from '../api/client'
import Page, { Loading } from '../components/Page'
import { useI18n } from '../i18n/I18nContext'

export default function TaxSettings() {
  const { t } = useI18n()
  const [settings, setSettings] = useState<RsgeSettings | null>(null)
  const [loading, setLoading] = useState(true)
  const [authLoading, setAuthLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [pinToken, setPinToken] = useState('')
  const [needsPin, setNeedsPin] = useState(false)
  const [form, setForm] = useState({ company_tin: '', username: '', password: '', pin: '' })
  const [vatTin, setVatTin] = useState('')
  const [vatResult, setVatResult] = useState<{ is_vat_payer: boolean; org_name?: string } | null>(null)

  const load = async () => {
    setLoading(true)
    try {
      const s = await api.accounting.settings.get()
      if (s) {
        setSettings(s)
        setForm((f) => ({ ...f, company_tin: s.company_tin, username: s.username }))
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    await api.accounting.settings.save({
      company_tin: form.company_tin,
      username: form.username,
      password: form.password,
    })
    setMessage(t.common.settingsSaved)
    load()
  }

  const handleAuth = async () => {
    setAuthLoading(true)
    setMessage('')
    try {
      const result = await api.accounting.rsge.auth({
        username: form.username,
        password: form.password,
        pin: needsPin ? form.pin : undefined,
        pin_token: needsPin ? pinToken : undefined,
      })
      if (result.needs_pin) {
        setNeedsPin(true)
        setPinToken(result.pin_token || '')
        setMessage(t.common.enterPin)
      } else if (result.success) {
        setMessage(`${t.common.connected} ✓`)
        setNeedsPin(false)
        load()
      } else {
        setMessage(result.message || t.common.authError)
      }
    } finally {
      setAuthLoading(false)
    }
  }

  const handleVatCheck = async () => {
    if (!vatTin) return
    const result = await api.accounting.rsge.checkVat(vatTin)
    setVatResult(result)
  }

  if (loading) return <Loading />

  return (
    <Page title={t.tax.title}>
      <div className="grid md:grid-cols-2 gap-6">
        <div className="card p-6">
          <div className="flex items-center gap-3 mb-6">
            <Link2 className="text-kinetix-600" size={24} />
            <div>
              <h2 className="text-lg font-semibold">{t.tax.connectTitle}</h2>
              <p className="text-sm text-gray-500">{t.tax.connectDesc}</p>
            </div>
          </div>

          {settings?.is_connected && (
            <div className="mb-4 p-3 bg-green-50 text-green-700 rounded-lg text-sm flex items-center gap-2">
              <Shield size={16} /> {t.tax.connected}
            </div>
          )}

          <form onSubmit={handleSave} className="space-y-4">
            <div>
              <label className="label">{t.tax.companyTin}</label>
              <input className="input" required value={form.company_tin} onChange={(e) => setForm({ ...form, company_tin: e.target.value })} placeholder="123456789" />
            </div>
            <div>
              <label className="label">{t.tax.rsgeLogin}</label>
              <input className="input" required value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
            </div>
            <div>
              <label className="label">{t.common.password}</label>
              <input className="input" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
            </div>
            {needsPin && (
              <div>
                <label className="label">{t.common.pinSms}</label>
                <input className="input" value={form.pin} onChange={(e) => setForm({ ...form, pin: e.target.value })} />
              </div>
            )}
            <div className="flex gap-3">
              <button type="submit" className="btn-secondary">{t.common.save}</button>
              <button type="button" className="btn-primary" onClick={handleAuth} disabled={authLoading}>
                {authLoading ? t.common.connecting : t.common.connect}
              </button>
            </div>
          </form>
          {message && <p className="mt-4 text-sm text-gray-600">{message}</p>}
        </div>

        <div className="card p-6">
          <div className="flex items-center gap-3 mb-6">
            <Search className="text-kinetix-600" size={24} />
            <h2 className="text-lg font-semibold">{t.tax.vatCheck}</h2>
          </div>
          <div className="flex gap-3 mb-4">
            <input className="input" value={vatTin} onChange={(e) => setVatTin(e.target.value)} placeholder={t.tax.counterpartyTin} />
            <button className="btn-primary shrink-0" onClick={handleVatCheck}>{t.common.check}</button>
          </div>
          {vatResult && (
            <div className={`p-4 rounded-lg ${vatResult.is_vat_payer ? 'bg-green-50' : 'bg-gray-50'}`}>
              <p className="font-medium">{vatResult.org_name || t.common.organization}</p>
              <p className="text-sm mt-1">
                {vatResult.is_vat_payer ? `✓ ${t.common.vatPayer}` : `✗ ${t.common.notVatPayer}`}
              </p>
            </div>
          )}

          <div className="mt-8 p-4 bg-gray-50 rounded-lg text-sm text-gray-600 space-y-2">
            <p className="font-medium text-gray-800">{t.tax.features}</p>
            <ul className="list-disc list-inside space-y-1">
              <li>{t.tax.f1}</li>
              <li>{t.tax.f2}</li>
              <li>{t.tax.f3}</li>
              <li>{t.tax.f4}</li>
              <li>{t.tax.f5}</li>
            </ul>
          </div>
        </div>
      </div>
    </Page>
  )
}
