import { localApi } from './localStore'

const API_BASE = import.meta.env.VITE_API_URL || '/api'
const USE_LOCAL = import.meta.env.VITE_USE_LOCAL_API === 'true'
export const AUTH_TOKEN_KEY = 'kinetix_token'
export const COMPANY_SLUG_KEY = 'kinetix_company_slug'

let useLocal = USE_LOCAL

export function getAuthToken(): string | null {
  return localStorage.getItem(AUTH_TOKEN_KEY)
}

export function setAuthToken(token: string) {
  localStorage.setItem(AUTH_TOKEN_KEY, token)
}

export function clearAuthToken() {
  localStorage.removeItem(AUTH_TOKEN_KEY)
}

export function getCompanySlug(): string | null {
  return localStorage.getItem(COMPANY_SLUG_KEY)
}

export function setCompanySlug(slug: string) {
  localStorage.setItem(COMPANY_SLUG_KEY, slug)
}

export function clearCompanySlug() {
  localStorage.removeItem(COMPANY_SLUG_KEY)
}

class ApiError extends Error {
  status: number
  constructor(message: string, status: number) {
    super(message)
    this.status = status
  }
}

const REMOTE_TIMEOUT_MS = 20000
const REMOTE_RETRIES = 3

async function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function authHeaders(): Record<string, string> {
  const token = getAuthToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  let lastError: unknown
  const attempts = USE_LOCAL ? 1 : REMOTE_RETRIES
  for (let attempt = 0; attempt < attempts; attempt += 1) {
    const controller = new AbortController()
    const timeoutMs = USE_LOCAL ? 5000 : REMOTE_TIMEOUT_MS
    const timeout = setTimeout(() => controller.abort(), timeoutMs)
    try {
      const res = await fetch(`${API_BASE}${url}`, {
        headers: { 'Content-Type': 'application/json', ...authHeaders(), ...options?.headers },
        signal: controller.signal,
        ...options,
      })
      if (res.status === 401) {
        clearAuthToken()
        if (!window.location.hash.includes('/login')) {
          window.location.hash = '#/login'
        }
        throw new ApiError('Unauthorized', 401)
      }
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }))
        const message = err.detail || 'Ошибка запроса'
        throw new ApiError(typeof message === 'string' ? message : 'Ошибка запроса', res.status)
      }
      if (res.status === 204) return undefined as T
      return res.json()
    } catch (err) {
      lastError = err
      if (err instanceof ApiError && (err.status === 401 || err.status === 403)) throw err
      if (attempt < attempts - 1) await sleep(2000)
    } finally {
      clearTimeout(timeout)
    }
  }
  throw lastError
}

async function withFallback<T>(remote: () => Promise<T>, local: () => T): Promise<T> {
  if (getAuthToken()) return remote()
  if (useLocal) return local()
  try {
    return await remote()
  } catch (err) {
    if (err instanceof ApiError && (err.status === 401 || err.status === 403)) throw err
    useLocal = true
    return local()
  }
}

export const api = {
  auth: {
    login: (companySlug: string, username: string, password: string) =>
      request<TokenResponse>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ company_slug: companySlug, username, password }),
      }),
    register: (data: RegisterInput) =>
      request<TokenResponse>('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
    me: () => request<AuthUser>('/auth/me'),
    logout: () => request<{ ok: boolean }>('/auth/logout', { method: 'POST' }),
    updateProfile: (data: { full_name?: string; email?: string }) =>
      request<AuthUser>('/auth/profile', { method: 'PATCH', body: JSON.stringify(data) }),
    changePassword: (current_password: string, new_password: string) =>
      request<{ ok: boolean }>('/auth/change-password', {
        method: 'POST',
        body: JSON.stringify({ current_password, new_password }),
      }),
    users: {
      list: () => request<UserRecord[]>('/auth/users'),
      create: (data: UserCreateInput) => request<UserRecord>('/auth/users', { method: 'POST', body: JSON.stringify(data) }),
      update: (id: number, data: Partial<UserCreateInput & { is_active?: boolean }>) =>
        request<UserRecord>(`/auth/users/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
      delete: (id: number) => request<void>(`/auth/users/${id}`, { method: 'DELETE' }),
    },
  },

  tenant: {
    get: () => request<TenantRecord>('/tenant/me'),
    update: (data: Partial<TenantRecord>) =>
      request<TenantRecord>('/tenant/me', { method: 'PATCH', body: JSON.stringify(data) }),
  },

  dashboard: () => withFallback(() => request<DashboardData>('/dashboard'), () => localApi.dashboard()),

  leads: {
    list: () => withFallback(() => request<Lead[]>('/crm/leads'), () => localApi.leads.list()),
    create: (data: Partial<Lead>) => withFallback(() => request<Lead>('/crm/leads', { method: 'POST', body: JSON.stringify(data) }), () => localApi.leads.create(data)),
    update: (id: number, data: Partial<Lead>) => withFallback(() => request<Lead>(`/crm/leads/${id}`, { method: 'PATCH', body: JSON.stringify(data) }), () => localApi.leads.update(id, data)),
    delete: (id: number) => withFallback(() => request<void>(`/crm/leads/${id}`, { method: 'DELETE' }), () => { localApi.leads.delete(id) }),
  },

  companies: {
    list: () => withFallback(() => request<Company[]>('/crm/companies'), () => localApi.companies.list()),
    create: (data: Partial<Company>) => withFallback(() => request<Company>('/crm/companies', { method: 'POST', body: JSON.stringify(data) }), () => localApi.companies.create(data)),
    update: (id: number, data: Partial<Company>) => withFallback(() => request<Company>(`/crm/companies/${id}`, { method: 'PATCH', body: JSON.stringify(data) }), () => localApi.companies.update(id, data)),
    delete: (id: number) => withFallback(() => request<void>(`/crm/companies/${id}`, { method: 'DELETE' }), () => { localApi.companies.delete(id) }),
  },

  contacts: {
    list: () => withFallback(() => request<Contact[]>('/crm/contacts'), () => localApi.contacts.list()),
    create: (data: Partial<Contact>) => withFallback(() => request<Contact>('/crm/contacts', { method: 'POST', body: JSON.stringify(data) }), () => localApi.contacts.create(data)),
    update: (id: number, data: Partial<Contact>) => withFallback(() => request<Contact>(`/crm/contacts/${id}`, { method: 'PATCH', body: JSON.stringify(data) }), () => localApi.contacts.update(id, data)),
    delete: (id: number) => withFallback(() => request<void>(`/crm/contacts/${id}`, { method: 'DELETE' }), () => { localApi.contacts.delete(id) }),
  },

  deals: {
    list: () => withFallback(() => request<Deal[]>('/crm/deals'), () => localApi.deals.list()),
    create: (data: Partial<Deal>) => withFallback(() => request<Deal>('/crm/deals', { method: 'POST', body: JSON.stringify(data) }), () => localApi.deals.create(data)),
    update: (id: number, data: Partial<Deal>) => withFallback(() => request<Deal>(`/crm/deals/${id}`, { method: 'PATCH', body: JSON.stringify(data) }), () => localApi.deals.update(id, data)),
    delete: (id: number) => withFallback(() => request<void>(`/crm/deals/${id}`, { method: 'DELETE' }), () => { localApi.deals.delete(id) }),
  },

  products: {
    list: () => withFallback(() => request<Product[]>('/warehouse/products'), () => localApi.products.list()),
    create: (data: Partial<Product>) => withFallback(() => request<Product>('/warehouse/products', { method: 'POST', body: JSON.stringify(data) }), () => localApi.products.create(data)),
    update: (id: number, data: Partial<Product>) => withFallback(() => request<Product>(`/warehouse/products/${id}`, { method: 'PATCH', body: JSON.stringify(data) }), () => localApi.products.update(id, data)),
    delete: (id: number) => withFallback(() => request<void>(`/warehouse/products/${id}`, { method: 'DELETE' }), () => { localApi.products.delete(id) }),
  },

  warehouses: {
    list: () => withFallback(() => request<Warehouse[]>('/warehouse/warehouses'), () => localApi.warehouses.list()),
    create: (data: Partial<Warehouse>) => withFallback(() => request<Warehouse>('/warehouse/warehouses', { method: 'POST', body: JSON.stringify(data) }), () => localApi.warehouses.create(data)),
  },

  stocks: {
    list: (params?: { warehouse_id?: number; product_id?: number }) => {
      if (useLocal) return Promise.resolve(localApi.stocks.list(params))
      const qs = new URLSearchParams()
      if (params?.warehouse_id) qs.set('warehouse_id', String(params.warehouse_id))
      if (params?.product_id) qs.set('product_id', String(params.product_id))
      const q = qs.toString()
      return withFallback(
        () => request<Stock[]>(`/warehouse/stocks${q ? `?${q}` : ''}`),
        () => localApi.stocks.list(params),
      )
    },
  },

  movements: {
    list: () => withFallback(() => request<StockMovement[]>('/warehouse/movements'), () => localApi.movements.list()),
    create: (data: Partial<StockMovement>) => withFallback(() => request<StockMovement>('/warehouse/movements', { method: 'POST', body: JSON.stringify(data) }), () => localApi.movements.create(data)),
  },

  accounting: {
    invoices: {
      list: () => withFallback(() => request<TaxInvoice[]>('/accounting/invoices'), () => localApi.accounting.invoices.list()),
      create: (data: Partial<TaxInvoice>) => withFallback(() => request<TaxInvoice>('/accounting/invoices', { method: 'POST', body: JSON.stringify(data) }), () => localApi.accounting.invoices.create(data)),
      sync: (id: number) => withFallback(() => request<TaxInvoice>(`/accounting/invoices/${id}/sync`, { method: 'POST' }), () => localApi.accounting.invoices.sync(id)),
      activate: (id: number) => withFallback(() => request<TaxInvoice>(`/accounting/invoices/${id}/activate`, { method: 'POST' }), () => localApi.accounting.invoices.activate(id)),
    },
    settings: {
      get: () => withFallback(() => request<RsgeSettings | null>('/accounting/settings'), () => localApi.accounting.settings.get()),
      save: (data: Partial<RsgeSettings> & { password?: string }) => withFallback(() => request<RsgeSettings>('/accounting/settings', { method: 'POST', body: JSON.stringify(data) }), () => localApi.accounting.settings.save(data)),
    },
    rsge: {
      auth: (data: { username: string; password: string; pin?: string; pin_token?: string }) =>
        withFallback(() => request<RsgeAuthResult>('/accounting/rsge/auth', { method: 'POST', body: JSON.stringify(data) }), () => localApi.accounting.rsge.auth(data)),
      checkVat: (tin: string) =>
        withFallback(() => request<VatCheckResult>('/accounting/rsge/check-vat', { method: 'POST', body: JSON.stringify({ tin }) }), () => localApi.accounting.rsge.checkVat(tin)),
    },
  },

  messaging: {
    conversations: {
      list: (params?: { channel?: string; contact_id?: number; lead_id?: number }) => {
        const qs = new URLSearchParams()
        if (params?.channel) qs.set('channel', params.channel)
        if (params?.contact_id) qs.set('contact_id', String(params.contact_id))
        if (params?.lead_id) qs.set('lead_id', String(params.lead_id))
        const q = qs.toString()
        return withFallback(
          () => request<Conversation[]>(`/messaging/conversations${q ? `?${q}` : ''}`),
          () => localApi.messaging.conversations.list(params?.channel, params?.contact_id, params?.lead_id),
        )
      },
      get: (id: number) => withFallback(
        () => request<Conversation>(`/messaging/conversations/${id}`),
        () => localApi.messaging.conversations.get(id),
      ),
      messages: (id: number) => withFallback(
        () => request<Message[]>(`/messaging/conversations/${id}/messages`),
        () => localApi.messaging.conversations.messages(id),
      ),
      send: (id: number, body: string) => withFallback(
        () => request<Message>(`/messaging/conversations/${id}/messages`, { method: 'POST', body: JSON.stringify({ body }) }),
        () => localApi.messaging.conversations.send(id, body),
      ),
      markRead: (id: number) => withFallback(
        () => request<Conversation>(`/messaging/conversations/${id}/read`, { method: 'PATCH' }),
        () => localApi.messaging.conversations.markRead(id),
      ),
      link: (id: number, data: { contact_id?: number; lead_id?: number }) => withFallback(
        () => request<Conversation>(`/messaging/conversations/${id}/link`, { method: 'PATCH', body: JSON.stringify(data) }),
        () => localApi.messaging.conversations.link(id, data),
      ),
      convertContact: (id: number) => withFallback(
        () => request<Conversation>(`/messaging/conversations/${id}/convert-contact`, { method: 'POST' }),
        () => localApi.messaging.conversations.convertContact(id),
      ),
    },
    calls: {
      list: (channel?: string) => withFallback(
        () => request<CallLog[]>(`/messaging/calls${channel ? `?channel=${channel}` : ''}`),
        () => localApi.messaging.calls.list(channel),
      ),
    },
    settings: {
      get: () => withFallback(
        () => request<MessagingSettings>('/messaging/settings'),
        () => localApi.messaging.settings.get(),
      ),
      save: (data: Partial<MessagingSettings> & { whatsapp_token?: string; messenger_page_token?: string; telegram_bot_token?: string }) => withFallback(
        () => request<MessagingSettings>('/messaging/settings', { method: 'POST', body: JSON.stringify(data) }),
        () => localApi.messaging.settings.save(data),
      ),
    },
    sync: (channel: 'whatsapp' | 'messenger' | 'telegram') => withFallback(
      () => request<SyncResult>(`/messaging/sync/${channel}`, { method: 'POST' }),
      () => localApi.messaging.sync(channel),
    ),
    syncCrm: () => withFallback(
      () => request<CrmSyncResult>('/messaging/sync-crm', { method: 'POST' }),
      () => localApi.messaging.syncCrm(),
    ),
  },

  automations: {
    bots: {
      list: () => withFallback(
        () => request<ChatBot[]>('/automations/bots'),
        () => localApi.automations.bots.list(),
      ),
      get: (id: number) => withFallback(
        () => request<ChatBot>(`/automations/bots/${id}`),
        () => localApi.automations.bots.get(id),
      ),
      create: (data: ChatBotInput) => withFallback(
        () => request<ChatBot>('/automations/bots', { method: 'POST', body: JSON.stringify(data) }),
        () => localApi.automations.bots.create(data),
      ),
      update: (id: number, data: Partial<ChatBotInput>) => withFallback(
        () => request<ChatBot>(`/automations/bots/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
        () => localApi.automations.bots.update(id, data),
      ),
      delete: (id: number) => withFallback(
        () => request<void>(`/automations/bots/${id}`, { method: 'DELETE' }),
        () => localApi.automations.bots.delete(id),
      ),
      toggle: (id: number) => withFallback(
        () => request<ChatBot>(`/automations/bots/${id}/toggle`, { method: 'PATCH' }),
        () => localApi.automations.bots.toggle(id),
      ),
    },
    templates: {
      list: () => withFallback(
        () => request<MessageTemplate[]>('/automations/templates'),
        () => localApi.automations.templates.list(),
      ),
      create: (data: MessageTemplateInput) => withFallback(
        () => request<MessageTemplate>('/automations/templates', { method: 'POST', body: JSON.stringify(data) }),
        () => localApi.automations.templates.create(data),
      ),
      update: (id: number, data: Partial<MessageTemplateInput>) => withFallback(
        () => request<MessageTemplate>(`/automations/templates/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
        () => localApi.automations.templates.update(id, data),
      ),
      delete: (id: number) => withFallback(
        () => request<void>(`/automations/templates/${id}`, { method: 'DELETE' }),
        () => localApi.automations.templates.delete(id),
      ),
    },
    logs: {
      list: () => withFallback(
        () => request<BotLog[]>('/automations/logs'),
        () => localApi.automations.logs.list(),
      ),
    },
  },
}

export interface DashboardData {
  leads: number
  deals: number
  contacts: number
  companies: number
  products: number
  total_stock: number
  won_amount: number
  pipeline_amount: number
  deals_by_stage: Record<string, number>
  unread_messages?: number
  conversations?: number
}

export interface Lead {
  id: number
  title: string
  name?: string
  phone?: string
  email?: string
  source?: string
  status: string
  amount: number
  comment?: string
  created_at: string
  updated_at: string
}

export interface Company {
  id: number
  name: string
  inn?: string
  phone?: string
  email?: string
  address?: string
  comment?: string
  created_at: string
}

export interface Contact {
  id: number
  name: string
  phone?: string
  email?: string
  position?: string
  company_id?: number
  comment?: string
  created_at: string
}

export interface Deal {
  id: number
  title: string
  stage: string
  amount: number
  contact_id?: number
  company_id?: number
  comment?: string
  created_at: string
  updated_at: string
  products: DealProduct[]
  contact_name?: string
  company_name?: string
}

export interface DealProduct {
  id: number
  product_id: number
  quantity: number
  price: number
  product_name?: string
  deal_id?: number
}

export interface Product {
  id: number
  name: string
  sku?: string
  unit: string
  price: number
  description?: string
  created_at: string
  total_stock: number
}

export interface Warehouse {
  id: number
  name: string
  address?: string
  is_default: boolean
  created_at: string
}

export interface Stock {
  id: number
  product_id: number
  warehouse_id: number
  quantity: number
  reserved: number
  available: number
  product_name?: string
  warehouse_name?: string
}

export interface StockMovement {
  id: number
  product_id: number
  warehouse_id: number
  movement_type: string
  quantity: number
  to_warehouse_id?: number
  deal_id?: number
  comment?: string
  created_at: string
  product_name?: string
  warehouse_name?: string
}

export interface TaxInvoice {
  id: number
  number?: string
  deal_id?: number
  company_id?: number
  tin_seller: string
  tin_buyer: string
  buyer_name?: string
  amount: number
  vat_rate: number
  vat_amount: number
  total_amount: number
  status: string
  rsge_invoice_id?: number
  rsge_transaction_id?: string
  description?: string
  operation_date?: string
  created_at: string
  synced_at?: string
  deal_title?: string
  company_name?: string
}

export interface RsgeSettings {
  id: number
  company_tin: string
  username: string
  is_connected: boolean
  last_sync?: string
}

export interface RsgeAuthResult {
  success: boolean
  needs_pin?: boolean
  pin_token?: string
  message?: string
}

export interface VatCheckResult {
  tin: string
  is_vat_payer: boolean
  org_name?: string
}

export interface Conversation {
  id: number
  channel: string
  external_id: string
  contact_name?: string
  phone?: string
  contact_id?: number
  lead_id?: number
  unread_count: number
  last_message_at?: string
  last_message_preview?: string
  created_at: string
  contact_name_linked?: string
  lead_title?: string
  company_name?: string
  lead_status?: string
}

export interface Message {
  id: number
  conversation_id: number
  direction: string
  body: string
  message_type: string
  external_id?: string
  status: string
  created_at: string
}

export interface CallLog {
  id: number
  channel: string
  external_id: string
  conversation_id?: number
  direction: string
  status: string
  duration_seconds?: number
  contact_name?: string
  phone?: string
  contact_id?: number
  lead_id?: number
  started_at: string
}

export interface MessagingSettings {
  id: number
  whatsapp_phone_number_id?: string
  whatsapp_verify_token?: string
  messenger_page_id?: string
  messenger_verify_token?: string
  telegram_webhook_secret?: string
  whatsapp_connected: boolean
  messenger_connected: boolean
  telegram_connected: boolean
  whatsapp_configured?: boolean
  messenger_configured?: boolean
  telegram_configured?: boolean
  webhook_whatsapp_url?: string
  webhook_messenger_url?: string
  webhook_telegram_url?: string
}

export interface SyncResult {
  channel: string
  success: boolean
  message: string
}

export interface CrmSyncResult {
  conversations: number
  linked_contacts: number
  linked_leads: number
  created_leads: number
  message: string
}

export interface BotTrigger {
  id?: number
  bot_id?: number
  trigger_type: string
  keyword?: string
  sort_order?: number
}

export interface BotAction {
  id?: number
  bot_id?: number
  trigger_id?: number | null
  action_type: string
  config: string
  sort_order?: number
}

export interface ChatBot {
  id: number
  name: string
  description?: string
  channels: string
  is_active: boolean
  welcome_message?: string
  fallback_message?: string
  priority: number
  created_at: string
  updated_at: string
  triggers: BotTrigger[]
  actions: BotAction[]
}

export type ChatBotInput = Omit<ChatBot, 'id' | 'created_at' | 'updated_at'>

export interface MessageTemplate {
  id: number
  title: string
  body: string
  channel?: string
  shortcut?: string
  created_at: string
}

export type MessageTemplateInput = Omit<MessageTemplate, 'id' | 'created_at'>

export interface BotLog {
  id: number
  bot_id?: number
  conversation_id?: number
  trigger_type?: string
  action_type?: string
  detail?: string
  created_at: string
}

export interface TenantRecord {
  id: number
  name: string
  slug: string
  email?: string
  phone?: string
  address?: string
  is_active: boolean
  created_at?: string
}

export interface AuthUser {
  id: number
  username: string
  email?: string
  full_name: string
  role: string
  is_active: boolean
  tenant_id: number
  permissions: string[]
  tenant: TenantRecord
  created_at?: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: AuthUser
}

export interface UserRecord {
  id: number
  username: string
  email?: string
  full_name: string
  role: string
  is_active: boolean
  created_at?: string
}

export interface UserCreateInput {
  username: string
  password: string
  full_name: string
  email?: string
  role: string
}

export interface RegisterInput {
  company_name: string
  company_slug: string
  admin_username: string
  admin_password: string
  admin_full_name: string
  admin_email?: string
  company_email?: string
  company_phone?: string
}
