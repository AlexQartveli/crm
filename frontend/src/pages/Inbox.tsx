import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { MessageCircle, Phone, Send, Plug, UserPlus, Link2, Building2, Briefcase, FileText } from 'lucide-react'
import { api, Contact, Conversation, Lead, Message, MessageTemplate } from '../api/client'
import Modal from '../components/Modal'
import { useI18n } from '../i18n/I18nContext'
import { formatDate } from '../utils'

function channelLabel(channel: string, t: ReturnType<typeof useI18n>['t']) {
  if (channel === 'whatsapp') return t.inbox.whatsapp
  if (channel === 'telegram') return t.integrations.telegram
  return t.inbox.messenger
}

function channelBadge(channel: string) {
  if (channel === 'whatsapp') return 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300'
  if (channel === 'telegram') return 'bg-sky-100 text-sky-800 dark:bg-sky-900/40 dark:text-sky-300'
  return 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300'
}

export default function Inbox() {
  const { t } = useI18n()
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [calls, setCalls] = useState<Awaited<ReturnType<typeof api.messaging.calls.list>>>([])
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [reply, setReply] = useState('')
  const [tab, setTab] = useState<'messages' | 'calls'>('messages')
  const [linkModalOpen, setLinkModalOpen] = useState(false)
  const [contacts, setContacts] = useState<Contact[]>([])
  const [leads, setLeads] = useState<Lead[]>([])
  const [linkContactId, setLinkContactId] = useState(0)
  const [linkLeadId, setLinkLeadId] = useState(0)
  const [crmMessage, setCrmMessage] = useState('')
  const [templates, setTemplates] = useState<MessageTemplate[]>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const selected = conversations.find((c) => c.id === selectedId) || null

  const loadConversations = () =>
    api.messaging.conversations.list().then(setConversations).catch(console.error)

  const loadCalls = () =>
    api.messaging.calls.list().then(setCalls).catch(console.error)

  const refreshSelected = () => {
    if (!selectedId) return
    api.messaging.conversations.get(selectedId).then((conv) => {
      setConversations((prev) => prev.map((c) => (c.id === conv.id ? conv : c)))
    }).catch(console.error)
  }

  useEffect(() => {
    loadConversations()
    loadCalls()
    api.automations.templates.list().then(setTemplates).catch(console.error)
    const interval = setInterval(() => {
      loadConversations()
      loadCalls()
      if (selectedId) {
        api.messaging.conversations.messages(selectedId).then(setMessages).catch(console.error)
      }
    }, 10000)
    return () => clearInterval(interval)
  }, [selectedId])

  useEffect(() => {
    if (!selectedId) return
    api.messaging.conversations.messages(selectedId).then(setMessages).catch(console.error)
    api.messaging.conversations.markRead(selectedId).then(() => loadConversations()).catch(console.error)
  }, [selectedId])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const openLinkModal = async () => {
    const [c, l] = await Promise.all([api.contacts.list(), api.leads.list()])
    setContacts(c)
    setLeads(l)
    setLinkContactId(selected?.contact_id || 0)
    setLinkLeadId(selected?.lead_id || 0)
    setLinkModalOpen(true)
  }

  const handleLink = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedId) return
    await api.messaging.conversations.link(selectedId, {
      contact_id: linkContactId || undefined,
      lead_id: linkLeadId || undefined,
    })
    setLinkModalOpen(false)
    setCrmMessage(t.inbox.linkSaved)
    loadConversations()
    refreshSelected()
  }

  const handleConvert = async () => {
    if (!selectedId) return
    await api.messaging.conversations.convertContact(selectedId)
    setCrmMessage(t.inbox.contactCreated)
    loadConversations()
    refreshSelected()
  }

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedId || !reply.trim()) return
    await api.messaging.conversations.send(selectedId, reply.trim())
    setReply('')
    api.messaging.conversations.messages(selectedId).then(setMessages)
    loadConversations()
  }

  return (
    <div className="p-4 md:p-8 h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h1 className="page-title">{t.inbox.title}</h1>
        <Link to="/integrations" className="btn-secondary flex items-center gap-2">
          <Plug size={18} /> {t.nav.integrations}
        </Link>
      </div>

      <div className="flex gap-1 mb-4">
        <button
          className={`px-4 py-2 rounded-lg text-sm font-medium ${tab === 'messages' ? 'bg-kinetix-600 text-white' : 'bg-app-surface text-app-text-secondary'}`}
          onClick={() => setTab('messages')}
        >
          <MessageCircle size={16} className="inline mr-1" />
          {t.inbox.messages} ({conversations.length})
        </button>
        <button
          className={`px-4 py-2 rounded-lg text-sm font-medium ${tab === 'calls' ? 'bg-kinetix-600 text-white' : 'bg-app-surface text-app-text-secondary'}`}
          onClick={() => setTab('calls')}
        >
          <Phone size={16} className="inline mr-1" />
          {t.inbox.calls} ({calls.length})
        </button>
      </div>

      {tab === 'calls' ? (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr>
                <th className="text-left p-4 font-medium">{t.common.date}</th>
                <th className="text-left p-4 font-medium">{t.inbox.channel}</th>
                <th className="text-left p-4 font-medium">{t.common.contact}</th>
                <th className="text-left p-4 font-medium">{t.common.phone}</th>
                <th className="text-left p-4 font-medium">{t.common.status}</th>
              </tr>
            </thead>
            <tbody>
              {calls.map((call) => (
                <tr key={call.id}>
                  <td className="p-4">{formatDate(call.started_at)}</td>
                  <td className="p-4">
                    <span className={`text-xs px-2 py-1 rounded-full ${channelBadge(call.channel)}`}>
                      {channelLabel(call.channel, t)}
                    </span>
                  </td>
                  <td className="p-4">{call.contact_name || t.common.dash}</td>
                  <td className="p-4">{call.phone || t.common.dash}</td>
                  <td className="p-4">
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      call.status === 'missed' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
                    }`}>
                      {t.inbox.callStatus[call.status as keyof typeof t.inbox.callStatus] || call.status}
                    </span>
                  </td>
                </tr>
              ))}
              {calls.length === 0 && (
                <tr><td colSpan={5} className="p-8 text-center text-app-text-muted">{t.common.empty}</td></tr>
              )}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="flex flex-1 gap-4 min-h-[500px]">
          <div className="w-full md:w-72 lg:w-80 card overflow-y-auto shrink-0">
            {conversations.map((conv) => (
              <button
                key={conv.id}
                onClick={() => setSelectedId(conv.id)}
                className={`w-full text-left p-4 border-b border-app-border hover:bg-app-surface-hover transition-colors ${
                  selectedId === conv.id ? 'bg-kinetix-50 dark:bg-kinetix-900/30' : ''
                }`}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="font-medium truncate">{conv.contact_name || conv.external_id}</span>
                  {conv.unread_count > 0 && (
                    <span className="bg-kinetix-600 text-white text-xs px-2 py-0.5 rounded-full shrink-0">
                      {conv.unread_count}
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-2 mt-1 flex-wrap">
                  <span className={`text-xs px-2 py-0.5 rounded-full ${channelBadge(conv.channel)}`}>
                    {channelLabel(conv.channel, t)}
                  </span>
                  {(conv.contact_id || conv.lead_id) && (
                    <span className="text-xs text-green-600 dark:text-green-400">CRM</span>
                  )}
                </div>
                <p className="text-sm text-app-text-muted mt-1 truncate">{conv.last_message_preview}</p>
              </button>
            ))}
            {conversations.length === 0 && (
              <p className="p-8 text-center text-app-text-muted">{t.inbox.noConversations}</p>
            )}
          </div>

          <div className="hidden md:flex flex-1 card flex-col min-w-0">
            {selected ? (
              <>
                <div className="p-4 border-b border-app-border">
                  <h2 className="font-semibold">{selected.contact_name || selected.external_id}</h2>
                  <div className="flex items-center gap-2 mt-1 text-sm text-app-text-muted">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${channelBadge(selected.channel)}`}>
                      {channelLabel(selected.channel, t)}
                    </span>
                    {selected.phone && <span>{selected.phone}</span>}
                  </div>
                </div>
                <div className="flex-1 overflow-y-auto p-4 space-y-3">
                  {messages.map((msg) => (
                    <div
                      key={msg.id}
                      className={`flex ${msg.direction === 'outbound' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`max-w-[70%] px-4 py-2 rounded-2xl text-sm ${
                        msg.direction === 'outbound'
                          ? 'bg-kinetix-600 text-white rounded-br-sm'
                          : 'bg-app-surface border border-app-border rounded-bl-sm'
                      }`}>
                        {msg.body}
                        <div className={`text-xs mt-1 ${msg.direction === 'outbound' ? 'text-kinetix-200' : 'text-app-text-muted'}`}>
                          {formatDate(msg.created_at)}
                        </div>
                      </div>
                    </div>
                  ))}
                  <div ref={messagesEndRef} />
                </div>
                <form onSubmit={handleSend} className="p-4 border-t border-app-border space-y-2">
                  {templates.length > 0 && (
                    <div className="flex items-center gap-2 flex-wrap">
                      <FileText size={14} className="text-app-text-muted shrink-0" />
                      <span className="text-xs text-app-text-muted">{t.inbox.quickTemplates}:</span>
                      {templates.map((tpl) => (
                        <button
                          key={tpl.id}
                          type="button"
                          className="text-xs px-2 py-1 rounded-full bg-app-surface border border-app-border hover:border-kinetix-500 hover:text-kinetix-600 transition-colors"
                          title={tpl.body}
                          onClick={() => setReply(tpl.body)}
                        >
                          {tpl.shortcut || tpl.title}
                        </button>
                      ))}
                    </div>
                  )}
                  <div className="flex gap-2">
                  <input
                    className="input flex-1"
                    value={reply}
                    onChange={(e) => setReply(e.target.value)}
                    placeholder={t.inbox.replyPlaceholder}
                  />
                  <button type="submit" className="btn-primary flex items-center gap-2" disabled={!reply.trim()}>
                    <Send size={18} />
                  </button>
                  </div>
                </form>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center text-app-text-muted">
                {t.inbox.selectConversation}
              </div>
            )}
          </div>

          {selected && (
            <div className="hidden lg:flex w-64 card flex-col shrink-0">
              <div className="p-4 border-b border-app-border">
                <h3 className="font-semibold text-sm">{t.inbox.crmLinks}</h3>
              </div>
              <div className="p-4 space-y-4 flex-1 text-sm">
                {crmMessage && (
                  <div className="info-banner-neutral text-xs">{crmMessage}</div>
                )}

                <div>
                  <div className="flex items-center gap-2 text-app-text-muted mb-1">
                    <Briefcase size={14} />
                    <span>{t.inbox.linkedContact}</span>
                  </div>
                  {selected.contact_id ? (
                    <Link to="/contacts" className="text-kinetix-600 dark:text-kinetix-400 hover:underline">
                      {selected.contact_name_linked || `#${selected.contact_id}`}
                    </Link>
                  ) : (
                    <span className="text-app-text-muted">{t.inbox.noCrmLink}</span>
                  )}
                </div>

                <div>
                  <div className="flex items-center gap-2 text-app-text-muted mb-1">
                    <MessageCircle size={14} />
                    <span>{t.inbox.linkedLead}</span>
                  </div>
                  {selected.lead_id ? (
                    <Link to="/leads" className="text-kinetix-600 dark:text-kinetix-400 hover:underline">
                      {selected.lead_title || `#${selected.lead_id}`}
                    </Link>
                  ) : (
                    <span className="text-app-text-muted">{t.inbox.noCrmLink}</span>
                  )}
                </div>

                {selected.company_name && (
                  <div>
                    <div className="flex items-center gap-2 text-app-text-muted mb-1">
                      <Building2 size={14} />
                      <span>{t.inbox.linkedCompany}</span>
                    </div>
                    <Link to="/companies" className="text-kinetix-600 dark:text-kinetix-400 hover:underline">
                      {selected.company_name}
                    </Link>
                  </div>
                )}

                <div className="space-y-2 pt-2">
                  {!selected.contact_id && (
                    <button type="button" className="btn-secondary w-full flex items-center justify-center gap-2 text-sm"
                      onClick={handleConvert}>
                      <UserPlus size={16} />
                      {t.inbox.convertToContact}
                    </button>
                  )}
                  <button type="button" className="btn-secondary w-full flex items-center justify-center gap-2 text-sm"
                    onClick={openLinkModal}>
                    <Link2 size={16} />
                    {t.inbox.linkToCrm}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      <Modal open={linkModalOpen} onClose={() => setLinkModalOpen(false)} title={t.inbox.linkModalTitle}>
        <form onSubmit={handleLink} className="space-y-4">
          <div>
            <label className="label">{t.inbox.selectContact}</label>
            <select className="input" value={linkContactId} onChange={(e) => setLinkContactId(+e.target.value)}>
              <option value={0}>{t.common.dash}</option>
              {contacts.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
          <div>
            <label className="label">{t.inbox.selectLead}</label>
            <select className="input" value={linkLeadId} onChange={(e) => setLinkLeadId(+e.target.value)}>
              <option value={0}>{t.common.dash}</option>
              {leads.map((l) => <option key={l.id} value={l.id}>{l.title}</option>)}
            </select>
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" className="btn-secondary" onClick={() => setLinkModalOpen(false)}>{t.common.cancel}</button>
            <button type="submit" className="btn-primary">{t.common.save}</button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
