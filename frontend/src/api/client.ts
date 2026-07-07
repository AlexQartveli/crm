import { localApi } from './localStore'

const API_BASE = import.meta.env.VITE_API_URL || '/api'
const USE_LOCAL = import.meta.env.VITE_USE_LOCAL_API === 'true'

let useLocal = USE_LOCAL

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), 5000)
  try {
    const res = await fetch(`${API_BASE}${url}`, {
      headers: { 'Content-Type': 'application/json', ...options?.headers },
      signal: controller.signal,
      ...options,
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }))
      throw new Error(err.detail || 'Ошибка запроса')
    }
    if (res.status === 204) return undefined as T
    return res.json()
  } finally {
    clearTimeout(timeout)
  }
}

async function withFallback<T>(remote: () => Promise<T>, local: () => T): Promise<T> {
  if (useLocal) return local()
  try {
    return await remote()
  } catch {
    useLocal = true
    return local()
  }
}

export const api = {
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
