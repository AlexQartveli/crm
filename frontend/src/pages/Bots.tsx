import { useEffect, useState } from 'react'
import { Bot, Plus, Trash2, Power, FileText, History } from 'lucide-react'
import { api, BotAction, BotTrigger, ChatBot, ChatBotInput, MessageTemplate } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import { PERM } from '../auth/permissions'
import Modal from '../components/Modal'
import Page, { Loading } from '../components/Page'
import { useI18n } from '../i18n/I18nContext'
import { formatDate } from '../utils'

const CHANNELS = ['all', 'whatsapp', 'messenger', 'telegram']
const TRIGGER_TYPES = ['first_message', 'keyword', 'any_message', 'regex']
const ACTION_TYPES = ['send_message', 'create_lead', 'update_lead_status', 'create_deal', 'add_lead_comment']

const emptyBot = (): ChatBotInput => ({
  name: '',
  description: '',
  channels: 'all',
  is_active: true,
  welcome_message: '',
  fallback_message: '',
  priority: 0,
  triggers: [{ trigger_type: 'first_message', keyword: '', sort_order: 0 }],
  actions: [{ action_type: 'send_message', config: '{"text":""}', sort_order: 0 }],
})

function parseConfig(config: string): Record<string, string> {
  try {
    return JSON.parse(config || '{}')
  } catch {
    return {}
  }
}

export default function Bots() {
  const { t } = useI18n()
  const { can } = useAuth()
  const canManage = can(PERM.automationsManage)
  const [tab, setTab] = useState<'bots' | 'templates' | 'logs'>('bots')
  const [loading, setLoading] = useState(true)
  const [bots, setBots] = useState<ChatBot[]>([])
  const [templates, setTemplates] = useState<MessageTemplate[]>([])
  const [logs, setLogs] = useState<Awaited<ReturnType<typeof api.automations.logs.list>>>([])
  const [modalOpen, setModalOpen] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [form, setForm] = useState<ChatBotInput>(emptyBot())
  const [tplForm, setTplForm] = useState({ title: '', body: '', shortcut: '' })
  const [tplModal, setTplModal] = useState(false)

  const load = async () => {
    setLoading(true)
    try {
      const [b, tpl, lg] = await Promise.all([
        api.automations.bots.list(),
        api.automations.templates.list(),
        api.automations.logs.list(),
      ])
      setBots(b)
      setTemplates(tpl)
      setLogs(lg)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const openCreate = () => {
    setEditingId(null)
    setForm(emptyBot())
    setModalOpen(true)
  }

  const openEdit = (bot: ChatBot) => {
    setEditingId(bot.id)
    setForm({
      name: bot.name,
      description: bot.description,
      channels: bot.channels,
      is_active: bot.is_active,
      welcome_message: bot.welcome_message,
      fallback_message: bot.fallback_message,
      priority: bot.priority,
      triggers: bot.triggers.map(({ trigger_type, keyword, sort_order }) => ({ trigger_type, keyword, sort_order })),
      actions: bot.actions.map(({ trigger_id, action_type, config, sort_order }) => ({ trigger_id, action_type, config, sort_order })),
    })
    setModalOpen(true)
  }

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    if (editingId) await api.automations.bots.update(editingId, form)
    else await api.automations.bots.create(form)
    setModalOpen(false)
    load()
  }

  const handleToggle = async (id: number) => {
    await api.automations.bots.toggle(id)
    load()
  }

  const handleDelete = async (id: number) => {
    if (!confirm(t.bots.confirmDelete)) return
    await api.automations.bots.delete(id)
    load()
  }

  const handleTplSave = async (e: React.FormEvent) => {
    e.preventDefault()
    await api.automations.templates.create(tplForm)
    setTplModal(false)
    setTplForm({ title: '', body: '', shortcut: '' })
    load()
  }

  const updateTrigger = (i: number, patch: Partial<BotTrigger>) => {
    const triggers = [...form.triggers]
    triggers[i] = { ...triggers[i], ...patch }
    setForm({ ...form, triggers })
  }

  const updateAction = (i: number, patch: Partial<BotAction>) => {
    const actions = [...form.actions]
    actions[i] = { ...actions[i], ...patch }
    setForm({ ...form, actions })
  }

  const setActionText = (i: number, text: string) => {
    updateAction(i, { config: JSON.stringify({ text }) })
  }

  if (loading) return <Loading />

  return (
    <Page title={t.bots.title}>
      <p className="text-app-text-muted mb-6 -mt-2">{t.bots.subtitle}</p>

      <div className="flex gap-1 mb-6 flex-wrap">
        {(['bots', 'templates', 'logs'] as const).map((key) => (
          <button
            key={key}
            className={`px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 ${
              tab === key ? 'bg-kinetix-600 text-white' : 'bg-app-surface text-app-text-secondary'
            }`}
            onClick={() => setTab(key)}
          >
            {key === 'bots' && <Bot size={16} />}
            {key === 'templates' && <FileText size={16} />}
            {key === 'logs' && <History size={16} />}
            {t.bots.tabs[key]}
          </button>
        ))}
      </div>

      {tab === 'bots' && (
        <>
          {canManage && (
          <div className="flex justify-end mb-4">
            <button className="btn-primary flex items-center gap-2" onClick={openCreate}>
              <Plus size={18} /> {t.bots.add}
            </button>
          </div>
          )}
          <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
            {bots.map((bot) => (
              <div key={bot.id} className="card p-5">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h3 className="font-semibold flex items-center gap-2">
                      <Bot size={18} className="text-kinetix-600" />
                      {bot.name}
                    </h3>
                    <p className="text-sm text-app-text-muted mt-1">{bot.description || t.common.dash}</p>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded-full ${bot.is_active ? 'bg-green-100 text-green-800' : 'bg-slate-100 text-slate-600'}`}>
                    {bot.is_active ? t.bots.active : t.bots.inactive}
                  </span>
                </div>
                <div className="mt-3 text-xs text-app-text-muted space-y-1">
                  <p>{t.bots.channels}: {bot.channels}</p>
                  <p>{t.bots.triggers}: {bot.triggers.length} · {t.bots.actions}: {bot.actions.length}</p>
                </div>
                <div className="flex gap-2 mt-4">
                  {canManage && (
                  <>
                  <button className="btn-secondary text-sm flex-1" onClick={() => openEdit(bot)}>{t.common.edit}</button>
                  <button className="btn-secondary text-sm" onClick={() => handleToggle(bot.id)} title={t.bots.toggle}>
                    <Power size={16} />
                  </button>
                  <button className="btn-secondary text-sm text-red-500" onClick={() => handleDelete(bot.id)}>
                    <Trash2 size={16} />
                  </button>
                  </>
                  )}
                </div>
              </div>
            ))}
            {bots.length === 0 && <p className="text-app-text-muted col-span-full">{t.common.empty}</p>}
          </div>
        </>
      )}

      {tab === 'templates' && (
        <>
          {canManage && (
          <div className="flex justify-end mb-4">
            <button className="btn-primary flex items-center gap-2" onClick={() => setTplModal(true)}>
              <Plus size={18} /> {t.bots.addTemplate}
            </button>
          </div>
          )}
          <div className="card overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr>
                  <th className="text-left p-4 font-medium">{t.common.title}</th>
                  <th className="text-left p-4 font-medium">{t.bots.shortcut}</th>
                  <th className="text-left p-4 font-medium">{t.common.comment}</th>
                  <th className="p-4"></th>
                </tr>
              </thead>
              <tbody>
                {templates.map((tpl) => (
                  <tr key={tpl.id}>
                    <td className="p-4 font-medium">{tpl.title}</td>
                    <td className="p-4">{tpl.shortcut || t.common.dash}</td>
                    <td className="p-4 text-app-text-muted max-w-md truncate">{tpl.body}</td>
                    <td className="p-4">
                      {canManage && (
                      <button className="text-red-400" onClick={async () => { await api.automations.templates.delete(tpl.id); load() }}>
                        <Trash2 size={16} />
                      </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {tab === 'logs' && (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr>
                <th className="text-left p-4 font-medium">{t.common.date}</th>
                <th className="text-left p-4 font-medium">{t.bots.trigger}</th>
                <th className="text-left p-4 font-medium">{t.bots.action}</th>
                <th className="text-left p-4 font-medium">{t.common.comment}</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.id}>
                  <td className="p-4">{formatDate(log.created_at)}</td>
                  <td className="p-4">{log.trigger_type || t.common.dash}</td>
                  <td className="p-4">{log.action_type || t.common.dash}</td>
                  <td className="p-4 text-app-text-muted max-w-lg truncate">{log.detail || t.common.dash}</td>
                </tr>
              ))}
              {logs.length === 0 && (
                <tr><td colSpan={4} className="p-8 text-center text-app-text-muted">{t.common.empty}</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editingId ? t.bots.edit : t.bots.new}>
        <form onSubmit={handleSave} className="space-y-4 max-h-[70vh] overflow-y-auto pr-1">
          <div><label className="label">{t.common.name} *</label><input className="input" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></div>
          <div><label className="label">{t.common.comment}</label><textarea className="input" rows={2} value={form.description || ''} onChange={(e) => setForm({ ...form, description: e.target.value })} /></div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">{t.bots.channels}</label>
              <select className="input" value={form.channels} onChange={(e) => setForm({ ...form, channels: e.target.value })}>
                {CHANNELS.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label className="label">{t.bots.priority}</label>
              <input className="input" type="number" value={form.priority} onChange={(e) => setForm({ ...form, priority: +e.target.value })} />
            </div>
          </div>
          <div><label className="label">{t.bots.welcomeMessage}</label><textarea className="input" rows={2} value={form.welcome_message || ''} onChange={(e) => setForm({ ...form, welcome_message: e.target.value })} /></div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="label mb-0">{t.bots.triggers}</label>
              <button type="button" className="text-sm text-kinetix-600" onClick={() => setForm({ ...form, triggers: [...form.triggers, { trigger_type: 'keyword', keyword: '', sort_order: form.triggers.length }] })}>+</button>
            </div>
            {form.triggers.map((tr, i) => (
              <div key={i} className="grid grid-cols-2 gap-2 mb-2">
                <select className="input" value={tr.trigger_type} onChange={(e) => updateTrigger(i, { trigger_type: e.target.value })}>
                  {TRIGGER_TYPES.map((tt) => <option key={tt} value={tt}>{t.bots.triggerTypes[tt as keyof typeof t.bots.triggerTypes] || tt}</option>)}
                </select>
                <input className="input" placeholder={t.bots.keyword} value={tr.keyword || ''} onChange={(e) => updateTrigger(i, { keyword: e.target.value })} />
              </div>
            ))}
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="label mb-0">{t.bots.actions}</label>
              <button type="button" className="text-sm text-kinetix-600" onClick={() => setForm({ ...form, actions: [...form.actions, { action_type: 'send_message', config: '{"text":""}', sort_order: form.actions.length }] })}>+</button>
            </div>
            {form.actions.map((act, i) => (
              <div key={i} className="border border-app-border rounded-lg p-3 mb-2 space-y-2">
                <select className="input" value={act.action_type} onChange={(e) => updateAction(i, { action_type: e.target.value })}>
                  {ACTION_TYPES.map((at) => <option key={at} value={at}>{t.bots.actionTypes[at as keyof typeof t.bots.actionTypes] || at}</option>)}
                </select>
                {(act.action_type === 'send_message' || act.action_type === 'add_lead_comment') && (
                  <textarea className="input" rows={2} value={parseConfig(act.config).text || ''} onChange={(e) => setActionText(i, e.target.value)} />
                )}
                {act.action_type === 'update_lead_status' && (
                  <select className="input" value={parseConfig(act.config).status || 'in_progress'} onChange={(e) => updateAction(i, { config: JSON.stringify({ status: e.target.value }) })}>
                    <option value="new">new</option>
                    <option value="in_progress">in_progress</option>
                    <option value="converted">converted</option>
                  </select>
                )}
                {act.action_type === 'create_deal' && (
                  <input className="input" placeholder={t.common.title} value={parseConfig(act.config).title || ''} onChange={(e) => updateAction(i, { config: JSON.stringify({ ...parseConfig(act.config), title: e.target.value, stage: 'new' }) })} />
                )}
              </div>
            ))}
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button type="button" className="btn-secondary" onClick={() => setModalOpen(false)}>{t.common.cancel}</button>
            <button type="submit" className="btn-primary">{t.common.save}</button>
          </div>
        </form>
      </Modal>

      <Modal open={tplModal} onClose={() => setTplModal(false)} title={t.bots.addTemplate}>
        <form onSubmit={handleTplSave} className="space-y-4">
          <div><label className="label">{t.common.title} *</label><input className="input" required value={tplForm.title} onChange={(e) => setTplForm({ ...tplForm, title: e.target.value })} /></div>
          <div><label className="label">{t.bots.shortcut}</label><input className="input" value={tplForm.shortcut} onChange={(e) => setTplForm({ ...tplForm, shortcut: e.target.value })} placeholder="/price" /></div>
          <div><label className="label">{t.bots.templateBody} *</label><textarea className="input" required rows={4} value={tplForm.body} onChange={(e) => setTplForm({ ...tplForm, body: e.target.value })} /></div>
          <div className="flex justify-end gap-3">
            <button type="button" className="btn-secondary" onClick={() => setTplModal(false)}>{t.common.cancel}</button>
            <button type="submit" className="btn-primary">{t.common.create}</button>
          </div>
        </form>
      </Modal>
    </Page>
  )
}
