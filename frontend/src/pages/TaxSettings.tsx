import { useEffect, useState } from 'react'
import { Link2, Shield, Search } from 'lucide-react'
import { api, RsgeSettings } from '../api/client'
import Page, { Loading } from '../components/Page'

export default function TaxSettings() {
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
    setMessage('Настройки сохранены')
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
        setMessage('Введите PIN из SMS')
      } else if (result.success) {
        setMessage('Подключено к RS.ge ✓')
        setNeedsPin(false)
        load()
      } else {
        setMessage(result.message || 'Ошибка авторизации')
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
    <Page title="RS.ge — Налоговая Грузии">
      <div className="grid md:grid-cols-2 gap-6">
        <div className="card p-6">
          <div className="flex items-center gap-3 mb-6">
            <Link2 className="text-kinetix-600" size={24} />
            <div>
              <h2 className="text-lg font-semibold">Подключение к RS.ge</h2>
              <p className="text-sm text-gray-500">eapi.rs.ge — электронные налоговые счета</p>
            </div>
          </div>

          {settings?.is_connected && (
            <div className="mb-4 p-3 bg-green-50 text-green-700 rounded-lg text-sm flex items-center gap-2">
              <Shield size={16} /> Подключено к RS.ge
            </div>
          )}

          <form onSubmit={handleSave} className="space-y-4">
            <div>
              <label className="label">TIN компании (საიდენტიფიკაციო ნომერი)</label>
              <input className="input" required value={form.company_tin} onChange={(e) => setForm({ ...form, company_tin: e.target.value })} placeholder="123456789" />
            </div>
            <div>
              <label className="label">Логин RS.ge</label>
              <input className="input" required value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
            </div>
            <div>
              <label className="label">Пароль</label>
              <input className="input" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
            </div>
            {needsPin && (
              <div>
                <label className="label">PIN из SMS</label>
                <input className="input" value={form.pin} onChange={(e) => setForm({ ...form, pin: e.target.value })} />
              </div>
            )}
            <div className="flex gap-3">
              <button type="submit" className="btn-secondary">Сохранить</button>
              <button type="button" className="btn-primary" onClick={handleAuth} disabled={authLoading}>
                {authLoading ? 'Подключение...' : 'Подключить'}
              </button>
            </div>
          </form>
          {message && <p className="mt-4 text-sm text-gray-600">{message}</p>}
        </div>

        <div className="card p-6">
          <div className="flex items-center gap-3 mb-6">
            <Search className="text-kinetix-600" size={24} />
            <h2 className="text-lg font-semibold">Проверка плательщика НДС</h2>
          </div>
          <div className="flex gap-3 mb-4">
            <input className="input" value={vatTin} onChange={(e) => setVatTin(e.target.value)} placeholder="TIN контрагента" />
            <button className="btn-primary shrink-0" onClick={handleVatCheck}>Проверить</button>
          </div>
          {vatResult && (
            <div className={`p-4 rounded-lg ${vatResult.is_vat_payer ? 'bg-green-50' : 'bg-gray-50'}`}>
              <p className="font-medium">{vatResult.org_name || 'Организация'}</p>
              <p className="text-sm mt-1">
                {vatResult.is_vat_payer ? '✓ Плательщик НДС' : '✗ Не является плательщиком НДС'}
              </p>
            </div>
          )}

          <div className="mt-8 p-4 bg-gray-50 rounded-lg text-sm text-gray-600 space-y-2">
            <p className="font-medium text-gray-800">Возможности интеграции:</p>
            <ul className="list-disc list-inside space-y-1">
              <li>Создание налоговых счетов (საგადასახადო დოკუმენტი)</li>
              <li>Отправка и активация в RS.ge</li>
              <li>Проверка статуса плательщика НДС</li>
              <li>Привязка счетов к сделкам CRM</li>
              <li>НДС 18% (ставка Грузии)</li>
            </ul>
          </div>
        </div>
      </div>
    </Page>
  )
}
