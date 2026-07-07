const API_BASE = '/api'

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Ошибка запроса')
  }
  if (res.status === 204) return undefined as T
  return res.json()
}

export const api = {
  dashboard: () => request<DashboardData>('/dashboard'),

  leads: {
    list: () => request<Lead[]>('/crm/leads'),
    create: (data: Partial<Lead>) => request<Lead>('/crm/leads', { method: 'POST', body: JSON.stringify(data) }),
    update: (id: number, data: Partial<Lead>) => request<Lead>(`/crm/leads/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
    delete: (id: number) => request<void>(`/crm/leads/${id}`, { method: 'DELETE' }),
  },

  companies: {
    list: () => request<Company[]>('/crm/companies'),
    create: (data: Partial<Company>) => request<Company>('/crm/companies', { method: 'POST', body: JSON.stringify(data) }),
    update: (id: number, data: Partial<Company>) => request<Company>(`/crm/companies/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
    delete: (id: number) => request<void>(`/crm/companies/${id}`, { method: 'DELETE' }),
  },

  contacts: {
    list: () => request<Contact[]>('/crm/contacts'),
    create: (data: Partial<Contact>) => request<Contact>('/crm/contacts', { method: 'POST', body: JSON.stringify(data) }),
    update: (id: number, data: Partial<Contact>) => request<Contact>(`/crm/contacts/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
    delete: (id: number) => request<void>(`/crm/contacts/${id}`, { method: 'DELETE' }),
  },

  deals: {
    list: () => request<Deal[]>('/crm/deals'),
    create: (data: Partial<Deal>) => request<Deal>('/crm/deals', { method: 'POST', body: JSON.stringify(data) }),
    update: (id: number, data: Partial<Deal>) => request<Deal>(`/crm/deals/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
    delete: (id: number) => request<void>(`/crm/deals/${id}`, { method: 'DELETE' }),
  },

  products: {
    list: () => request<Product[]>('/warehouse/products'),
    create: (data: Partial<Product>) => request<Product>('/warehouse/products', { method: 'POST', body: JSON.stringify(data) }),
    update: (id: number, data: Partial<Product>) => request<Product>(`/warehouse/products/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
    delete: (id: number) => request<void>(`/warehouse/products/${id}`, { method: 'DELETE' }),
  },

  warehouses: {
    list: () => request<Warehouse[]>('/warehouse/warehouses'),
    create: (data: Partial<Warehouse>) => request<Warehouse>('/warehouse/warehouses', { method: 'POST', body: JSON.stringify(data) }),
  },

  stocks: {
    list: (params?: { warehouse_id?: number; product_id?: number }) => {
      const qs = new URLSearchParams()
      if (params?.warehouse_id) qs.set('warehouse_id', String(params.warehouse_id))
      if (params?.product_id) qs.set('product_id', String(params.product_id))
      const q = qs.toString()
      return request<Stock[]>(`/warehouse/stocks${q ? `?${q}` : ''}`)
    },
  },

  movements: {
    list: () => request<StockMovement[]>('/warehouse/movements'),
    create: (data: Partial<StockMovement>) => request<StockMovement>('/warehouse/movements', { method: 'POST', body: JSON.stringify(data) }),
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
