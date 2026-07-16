import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Link2, MessageCircle, Send, Shield, RefreshCw, Bot } from 'lucide-react'
import { api, MessagingSettings } from '../api/client'
import Page, { Loading } from '../components/Page'
import { useI18n } from '../i18n/I18nContext'

type ChannelKey = 'whatsapp' | 'messenger' | 'telegram'

function StatusBadge({ connected }: { connected: boolean }) {
  const { t } = useI18n()
  return (
    <span className={`text-xs font-medium px-2 py-1 rounded-full ${
      connected ? 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300' : 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300'
    }`}>
      {connected ? t.integrations.connected : t.integrations.notConnected}
    </span>
  )
}

export default function Integrations() {
  const { t } = useI18n()
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState('')
  const [syncing, setSyncing] = useState<ChannelKey | null>(null)
  const [syncingCrm, setSyncingCrm] = useState(false)
  const [settings, setSettings] = useState<MessagingSettings | null>(null)
  const [form, setForm] = useState({
    whatsapp_token: '',
    whatsapp_phone_number_id: '',
    whatsapp_verify_token: 'kinetix-verify',
    messenger_page_token: '',
    messenger_verify_token: 'kinetix-verify',
    messenger_page_id: '',
    telegram_bot_token: '',
    telegram_webhook_secret: 'kinetix-tg-secret',
  })

  const load = async () => {
    setLoading(true)
    try {
      const s = await api.messaging.settings.get()
      setSettings(s)
      setForm((f) => ({
        ...f,
        whatsapp_phone_number_id: s.whatsapp_phone_number_id || '',
        whatsapp_verify_token: s.whatsapp_verify_token || 'kinetix-verify',
        messenger_page_id: s.messenger_page_id || '',
        messenger_verify_token: s.messenger_verify_token || 'kinetix-verify',
        telegram_webhook_secret: s.telegram_webhook_secret || 'kinetix-tg-secret',
      }))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    const payload: Record<string, string> = {}
    if (form.whatsapp_phone_number_id) payload.whatsapp_phone_number_id = form.whatsapp_phone_number_id
    if (form.whatsapp_verify_token) payload.whatsapp_verify_token = form.whatsapp_verify_token
    if (form.messenger_page_id) payload.messenger_page_id = form.messenger_page_id
    if (form.messenger_verify_token) payload.messenger_verify_token = form.messenger_verify_token
    if (form.telegram_webhook_secret) payload.telegram_webhook_secret = form.telegram_webhook_secret
    if (form.whatsapp_token) payload.whatsapp_token = form.whatsapp_token
    if (form.messenger_page_token) payload.messenger_page_token = form.messenger_page_token
    if (form.telegram_bot_token) payload.telegram_bot_token = form.telegram_bot_token
    await api.messaging.settings.save(payload)
    setMessage(t.common.settingsSaved)
    setForm((f) => ({ ...f, whatsapp_token: '', messenger_page_token: '', telegram_bot_token: '' }))
    load()
  }

  const handleSync = async (channel: ChannelKey) => {
    setSyncing(channel)
    setMessage('')
    try {
      const result = await api.messaging.sync(channel)
      setMessage(result.message)
      if (result.success) load()
    } finally {
      setSyncing(null)
    }
  }

  const handleSyncCrm = async () => {
    setSyncingCrm(true)
    setMessage('')
    try {
      const result = await api.messaging.syncCrm()
      setMessage(
        t.integrations.syncCrmResult
          .replace('{conversations}', String(result.conversations))
          .replace('{contacts}', String(result.linked_contacts))
          .replace('{leads}', String(result.linked_leads)),
      )
    } finally {
      setSyncingCrm(false)
    }
  }

  if (loading) return <Loading />

  return (
    <Page title={t.integrations.title}>
      <p className="text-app-text-muted mb-6 -mt-2">{t.integrations.subtitle}</p>

      {message && (
        <div className="mb-4 info-banner-neutral text-sm">{message}</div>
      )}

      <form onSubmit={handleSave} className="space-y-6">
        <div className="grid lg:grid-cols-3 gap-6">
          {/* WhatsApp */}
          <div className="card p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <MessageCircle className="text-green-600" size={24} />
                <h2 className="text-lg font-semibold">{t.integrations.whatsapp}</h2>
              </div>
              <StatusBadge connected={!!settings?.whatsapp_connected} />
            </div>
            <p className="text-sm text-app-text-muted mb-4">{t.integrations.whatsappDesc}</p>
            <div className="space-y-3">
              <div>
                <label className="label">{t.integrations.accessToken}</label>
                <input className="input" type="password" value={form.whatsapp_token}
                  onChange={(e) => setForm({ ...form, whatsapp_token: e.target.value })}
                  placeholder={settings?.whatsapp_configured ? '••••••••' : ''} />
              </div>
              <div>
                <label className="label">{t.integrations.phoneNumberId}</label>
                <input className="input" value={form.whatsapp_phone_number_id}
                  onChange={(e) => setForm({ ...form, whatsapp_phone_number_id: e.target.value })} />
              </div>
              <div>
                <label className="label">{t.integrations.verifyToken}</label>
                <input className="input" value={form.whatsapp_verify_token}
                  onChange={(e) => setForm({ ...form, whatsapp_verify_token: e.target.value })} />
              </div>
              <div className="info-box text-xs break-all">
                <p className="font-medium mb-1">{t.integrations.webhookUrl}</p>
                <p>{settings?.webhook_whatsapp_url}</p>
              </div>
              <button type="button" className="btn-primary w-full" disabled={syncing === 'whatsapp'}
                onClick={() => handleSync('whatsapp')}>
                {syncing === 'whatsapp' ? t.integrations.syncing : t.integrations.sync}
              </button>
            </div>
          </div>

          {/* Messenger */}
          <div className="card p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <Send className="text-blue-600" size={24} />
                <h2 className="text-lg font-semibold">{t.integrations.messenger}</h2>
              </div>
              <StatusBadge connected={!!settings?.messenger_connected} />
            </div>
            <p className="text-sm text-app-text-muted mb-4">{t.integrations.messengerDesc}</p>
            <div className="space-y-3">
              <div>
                <label className="label">{t.integrations.pageToken}</label>
                <input className="input" type="password" value={form.messenger_page_token}
                  onChange={(e) => setForm({ ...form, messenger_page_token: e.target.value })}
                  placeholder={settings?.messenger_configured ? '••••••••' : ''} />
              </div>
              <div>
                <label className="label">{t.integrations.pageId}</label>
                <input className="input" value={form.messenger_page_id}
                  onChange={(e) => setForm({ ...form, messenger_page_id: e.target.value })} />
              </div>
              <div>
                <label className="label">{t.integrations.verifyToken}</label>
                <input className="input" value={form.messenger_verify_token}
                  onChange={(e) => setForm({ ...form, messenger_verify_token: e.target.value })} />
              </div>
              <div className="info-box text-xs break-all">
                <p className="font-medium mb-1">{t.integrations.webhookUrl}</p>
                <p>{settings?.webhook_messenger_url}</p>
              </div>
              <button type="button" className="btn-primary w-full" disabled={syncing === 'messenger'}
                onClick={() => handleSync('messenger')}>
                {syncing === 'messenger' ? t.integrations.syncing : t.integrations.sync}
              </button>
            </div>
          </div>

          {/* Telegram */}
          <div className="card p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <Link2 className="text-sky-500" size={24} />
                <h2 className="text-lg font-semibold">{t.integrations.telegram}</h2>
              </div>
              <StatusBadge connected={!!settings?.telegram_connected} />
            </div>
            <p className="text-sm text-app-text-muted mb-4">{t.integrations.telegramDesc}</p>
            <div className="space-y-3">
              <div>
                <label className="label">{t.integrations.botToken}</label>
                <input className="input" type="password" value={form.telegram_bot_token}
                  onChange={(e) => setForm({ ...form, telegram_bot_token: e.target.value })}
                  placeholder={settings?.telegram_configured ? '••••••••' : ''} />
              </div>
              <div>
                <label className="label">{t.integrations.webhookSecret}</label>
                <input className="input" value={form.telegram_webhook_secret}
                  onChange={(e) => setForm({ ...form, telegram_webhook_secret: e.target.value })} />
              </div>
              <div className="info-box text-xs break-all">
                <p className="font-medium mb-1">{t.integrations.webhookUrl}</p>
                <p>{settings?.webhook_telegram_url}</p>
              </div>
              <button type="button" className="btn-primary w-full" disabled={syncing === 'telegram'}
                onClick={() => handleSync('telegram')}>
                {syncing === 'telegram' ? t.integrations.syncing : t.integrations.sync}
              </button>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center gap-3 mb-2">
            <RefreshCw className="text-kinetix-600" size={22} />
            <h2 className="text-lg font-semibold">{t.integrations.syncCrm}</h2>
          </div>
          <p className="text-sm text-app-text-muted mb-4">{t.integrations.syncCrmDesc}</p>
          <button type="button" className="btn-primary" disabled={syncingCrm} onClick={handleSyncCrm}>
            {syncingCrm ? t.integrations.syncingCrm : t.integrations.syncCrm}
          </button>
        </div>

        <div className="card p-6">
          <div className="flex items-center gap-3 mb-2">
            <Bot className="text-kinetix-600" size={22} />
            <h2 className="text-lg font-semibold">{t.nav.bots}</h2>
          </div>
          <p className="text-sm text-app-text-muted mb-4">{t.integrations.f5}</p>
          <Link to="/bots" className="btn-primary inline-flex items-center gap-2">
            {t.integrations.openBots}
          </Link>
        </div>

        <div className="card p-6">
          <div className="flex items-center gap-3 mb-4">
            <Shield className="text-kinetix-600" size={22} />
            <h2 className="text-lg font-semibold">{t.integrations.howItWorks}</h2>
          </div>
          <ul className="list-disc list-inside space-y-1 text-sm text-app-text-secondary">
            <li>{t.integrations.f1}</li>
            <li>{t.integrations.f2}</li>
            <li>{t.integrations.f3}</li>
            <li>{t.integrations.f4}</li>
          </ul>
        </div>

        <div className="flex gap-3">
          <button type="submit" className="btn-secondary">{t.common.save}</button>
        </div>
      </form>
    </Page>
  )
}
