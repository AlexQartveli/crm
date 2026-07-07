import type {
  Company,
  Contact,
  DashboardData,
  Deal,
  DealProduct,
  Lead,
  Product,
  RsgeAuthResult,
  RsgeSettings,
  Stock,
  StockMovement,
  TaxInvoice,
  VatCheckResult,
  Warehouse,
} from './client'

const STORAGE_KEY = 'kinetix_data_v2'

interface Store {
  leads: Lead[]
  companies: Company[]
  contacts: Contact[]
  deals: Deal[]
  dealProducts: DealProduct[]
  products: Product[]
  warehouses: Warehouse[]
  stocks: Omit<Stock, 'available' | 'product_name' | 'warehouse_name'>[]
  movements: StockMovement[]
  taxInvoices: TaxInvoice[]
  rsgeSettings: RsgeSettings | null
  nextId: number
}

function now() {
  return new Date().toISOString()
}

function calcVat(amount: number, rate = 18) {
  const vat = Math.round(amount * rate) / 100
  return { vat, total: amount + vat }
}

function seed(): Store {
  const t = now()
  return {
    nextId: 100,
    leads: [
      { id: 1, title: 'Заявка с сайта', name: 'Иван Петров', phone: '+7 999 123-45-67', email: 'ivan@example.com', source: 'Сайт', status: 'new', amount: 150000, created_at: t, updated_at: t },
      { id: 2, title: 'Звонок менеджеру', name: 'Мария Сидорова', phone: '+7 999 234-56-78', source: 'Телефон', status: 'in_progress', amount: 85000, created_at: t, updated_at: t },
    ],
    companies: [
      { id: 1, name: 'ООО «ТехноПром»', inn: '7701234567', phone: '+7 495 111-22-33', email: 'info@technoprom.ru', address: 'Москва, ул. Ленина, 1', created_at: t },
      { id: 2, name: 'ИП Козлов А.В.', inn: '7709876543', phone: '+7 916 555-44-33', email: 'kozlov@mail.ru', created_at: t },
    ],
    contacts: [
      { id: 1, name: 'Алексей Козлов', phone: '+7 916 555-44-33', email: 'kozlov@mail.ru', position: 'Директор', company_id: 2, created_at: t },
      { id: 2, name: 'Елена Волкова', phone: '+7 495 222-33-44', email: 'volkova@technoprom.ru', position: 'Менеджер по закупкам', company_id: 1, created_at: t },
    ],
    warehouses: [
      { id: 1, name: 'Основной склад', address: 'Москва, Складская 5', is_default: true, created_at: t },
      { id: 2, name: 'Склад №2', address: 'Москва, Промышленная 12', is_default: false, created_at: t },
    ],
    products: [
      { id: 1, name: 'Ноутбук Dell XPS 15', sku: 'NB-DELL-XPS15', unit: 'шт', price: 125000, created_at: t, total_stock: 20 },
      { id: 2, name: 'Монитор LG 27"', sku: 'MON-LG-27', unit: 'шт', price: 32000, created_at: t, total_stock: 40 },
      { id: 3, name: 'Клавиатура Logitech MX', sku: 'KB-LOG-MX', unit: 'шт', price: 8500, created_at: t, total_stock: 50 },
      { id: 4, name: 'Мышь Logitech MX Master', sku: 'MS-LOG-MXM', unit: 'шт', price: 7200, created_at: t, total_stock: 45 },
      { id: 5, name: 'Кабель HDMI 2м', sku: 'CB-HDMI-2M', unit: 'шт', price: 450, created_at: t, total_stock: 200 },
    ],
    stocks: [
      { id: 1, product_id: 1, warehouse_id: 1, quantity: 15, reserved: 0 },
      { id: 2, product_id: 2, warehouse_id: 1, quantity: 30, reserved: 0 },
      { id: 3, product_id: 3, warehouse_id: 1, quantity: 50, reserved: 0 },
      { id: 4, product_id: 4, warehouse_id: 1, quantity: 45, reserved: 0 },
      { id: 5, product_id: 5, warehouse_id: 1, quantity: 200, reserved: 0 },
      { id: 6, product_id: 1, warehouse_id: 2, quantity: 5, reserved: 0 },
      { id: 7, product_id: 2, warehouse_id: 2, quantity: 10, reserved: 0 },
    ],
    deals: [
      { id: 1, title: 'Поставка IT-оборудования', stage: 'negotiation', amount: 520000, contact_id: 2, company_id: 1, created_at: t, updated_at: t, products: [], contact_name: 'Елена Волкова', company_name: 'ООО «ТехноПром»' },
      { id: 2, title: 'Офисная периферия', stage: 'proposal', amount: 89000, contact_id: 1, company_id: 2, created_at: t, updated_at: t, products: [], contact_name: 'Алексей Козлов', company_name: 'ИП Козлов А.В.' },
      { id: 3, title: 'Мониторы для отдела', stage: 'new', amount: 192000, contact_id: 2, company_id: 1, created_at: t, updated_at: t, products: [], contact_name: 'Елена Волкова', company_name: 'ООО «ТехноПром»' },
      { id: 4, title: 'Кабельная продукция', stage: 'won', amount: 45000, contact_id: 1, company_id: 2, created_at: t, updated_at: t, products: [], contact_name: 'Алексей Козлов', company_name: 'ИП Козлов А.В.' },
    ],
    dealProducts: [
      { id: 1, deal_id: 1, product_id: 1, quantity: 3, price: 125000, product_name: 'Ноутбук Dell XPS 15' },
      { id: 2, deal_id: 1, product_id: 2, quantity: 5, price: 32000, product_name: 'Монитор LG 27"' },
      { id: 3, deal_id: 2, product_id: 3, quantity: 5, price: 8500, product_name: 'Клавиатура Logitech MX' },
      { id: 4, deal_id: 2, product_id: 4, quantity: 5, price: 7200, product_name: 'Мышь Logitech MX Master' },
    ],
    movements: [],
    taxInvoices: [
      {
        id: 1, number: 'INV-2026-0001', deal_id: 4, company_id: 2,
        tin_seller: '123456789', tin_buyer: '405321742', buyer_name: 'ИП Козлов А.В.',
        amount: 38135.59, vat_rate: 18, vat_amount: 6864.41, total_amount: 45000,
        status: 'active', rsge_invoice_id: 8842, description: 'Кабельная продукция',
        created_at: t, synced_at: t, deal_title: 'Кабельная продукция', company_name: 'ИП Козлов А.В.',
      },
      {
        id: 2, number: 'INV-2026-0002', deal_id: 1, company_id: 1,
        tin_seller: '123456789', tin_buyer: '206322102', buyer_name: 'ООО «ТехноПром»',
        amount: 440677.97, vat_rate: 18, vat_amount: 79322.03, total_amount: 520000,
        status: 'draft', description: 'Поставка IT-оборудования',
        created_at: t, deal_title: 'Поставка IT-оборудования', company_name: 'ООО «ТехноПром»',
      },
    ],
    rsgeSettings: { id: 1, company_tin: '123456789', username: 'demo', is_connected: true, last_sync: t },
  }
}

function load(): Store {
  const raw = localStorage.getItem(STORAGE_KEY)
  if (!raw) {
    const s = seed()
    save(s)
    return s
  }
  try {
    const parsed = JSON.parse(raw) as Partial<Store>
    if (!Array.isArray(parsed.contacts) || !Array.isArray(parsed.products) || !Array.isArray(parsed.deals)) {
      const s = seed()
      save(s)
      return s
    }
    return {
      ...parsed,
      leads: parsed.leads ?? [],
      companies: parsed.companies ?? [],
      contacts: parsed.contacts ?? [],
      deals: parsed.deals ?? [],
      dealProducts: parsed.dealProducts ?? [],
      products: parsed.products ?? [],
      warehouses: parsed.warehouses ?? [],
      stocks: parsed.stocks ?? [],
      movements: parsed.movements ?? [],
      taxInvoices: parsed.taxInvoices ?? [],
      rsgeSettings: parsed.rsgeSettings ?? null,
      nextId: parsed.nextId ?? 100,
    } as Store
  } catch {
    const s = seed()
    save(s)
    return s
  }
}

function save(store: Store) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(store))
}

function nextId(store: Store) {
  store.nextId += 1
  return store.nextId
}

function enrichDeal(store: Store, deal: Deal): Deal {
  const products = store.dealProducts
    .filter((dp) => dp.deal_id === deal.id)
    .map((dp) => ({
      ...dp,
      product_name: store.products.find((p) => p.id === dp.product_id)?.name,
    }))
  const contact = store.contacts.find((c) => c.id === deal.contact_id)
  const company = store.companies.find((c) => c.id === deal.company_id)
  return { ...deal, products, contact_name: contact?.name, company_name: company?.name }
}

function updateProductStockTotals(store: Store) {
  for (const p of store.products) {
    p.total_stock = store.stocks.filter((s) => s.product_id === p.id).reduce((sum, s) => sum + s.quantity, 0)
  }
}

export const localApi = {
  dashboard(): DashboardData {
    const s = load()
    const dealsByStage: Record<string, number> = {}
    for (const d of s.deals) {
      dealsByStage[d.stage] = (dealsByStage[d.stage] || 0) + 1
    }
    return {
      leads: s.leads.length,
      deals: s.deals.length,
      contacts: s.contacts.length,
      companies: s.companies.length,
      products: s.products.length,
      total_stock: s.stocks.reduce((sum, st) => sum + st.quantity, 0),
      won_amount: s.deals.filter((d) => d.stage === 'won').reduce((sum, d) => sum + d.amount, 0),
      pipeline_amount: s.deals.filter((d) => !['won', 'lost'].includes(d.stage)).reduce((sum, d) => sum + d.amount, 0),
      deals_by_stage: dealsByStage,
    }
  },

  leads: {
    list: () => load().leads.sort((a, b) => b.created_at.localeCompare(a.created_at)),
    create: (data: Partial<Lead>) => {
      const s = load()
      const lead: Lead = {
        id: nextId(s),
        title: data.title || '',
        name: data.name,
        phone: data.phone,
        email: data.email,
        source: data.source,
        status: data.status || 'new',
        amount: data.amount || 0,
        comment: data.comment,
        created_at: now(),
        updated_at: now(),
      }
      s.leads.unshift(lead)
      save(s)
      return lead
    },
    update: (id: number, data: Partial<Lead>) => {
      const s = load()
      const i = s.leads.findIndex((l) => l.id === id)
      if (i < 0) throw new Error('Лид не найден')
      s.leads[i] = { ...s.leads[i], ...data, updated_at: now() }
      save(s)
      return s.leads[i]
    },
    delete: (id: number) => {
      const s = load()
      s.leads = s.leads.filter((l) => l.id !== id)
      save(s)
    },
  },

  companies: {
    list: () => load().companies.sort((a, b) => b.created_at.localeCompare(a.created_at)),
    create: (data: Partial<Company>) => {
      const s = load()
      const company: Company = {
        id: nextId(s),
        name: data.name || '',
        inn: data.inn,
        phone: data.phone,
        email: data.email,
        address: data.address,
        comment: data.comment,
        created_at: now(),
      }
      s.companies.unshift(company)
      save(s)
      return company
    },
    update: (id: number, data: Partial<Company>) => {
      const s = load()
      const i = s.companies.findIndex((c) => c.id === id)
      if (i < 0) throw new Error('Компания не найдена')
      s.companies[i] = { ...s.companies[i], ...data }
      save(s)
      return s.companies[i]
    },
    delete: (id: number) => {
      const s = load()
      s.companies = s.companies.filter((c) => c.id !== id)
      save(s)
    },
  },

  contacts: {
    list: () => load().contacts.sort((a, b) => b.created_at.localeCompare(a.created_at)),
    create: (data: Partial<Contact>) => {
      const s = load()
      const contact: Contact = {
        id: nextId(s),
        name: data.name || '',
        phone: data.phone,
        email: data.email,
        position: data.position,
        company_id: data.company_id,
        comment: data.comment,
        created_at: now(),
      }
      s.contacts.unshift(contact)
      save(s)
      return contact
    },
    update: (id: number, data: Partial<Contact>) => {
      const s = load()
      const i = s.contacts.findIndex((c) => c.id === id)
      if (i < 0) throw new Error('Контакт не найден')
      s.contacts[i] = { ...s.contacts[i], ...data }
      save(s)
      return s.contacts[i]
    },
    delete: (id: number) => {
      const s = load()
      s.contacts = s.contacts.filter((c) => c.id !== id)
      save(s)
    },
  },

  deals: {
    list: () => load().deals.map((d) => enrichDeal(load(), d)).sort((a, b) => b.updated_at.localeCompare(a.updated_at)),
    create: (data: Partial<Deal>) => {
      const s = load()
      const deal: Deal = {
        id: nextId(s),
        title: data.title || '',
        stage: data.stage || 'new',
        amount: data.amount || 0,
        contact_id: data.contact_id,
        company_id: data.company_id,
        comment: data.comment,
        created_at: now(),
        updated_at: now(),
        products: [],
      }
      s.deals.unshift(deal)
      save(s)
      return enrichDeal(s, deal)
    },
    update: (id: number, data: Partial<Deal>) => {
      const s = load()
      const i = s.deals.findIndex((d) => d.id === id)
      if (i < 0) throw new Error('Сделка не найдена')
      s.deals[i] = { ...s.deals[i], ...data, updated_at: now() }
      save(s)
      return enrichDeal(s, s.deals[i])
    },
    delete: (id: number) => {
      const s = load()
      s.deals = s.deals.filter((d) => d.id !== id)
      s.dealProducts = s.dealProducts.filter((dp) => dp.deal_id !== id)
      save(s)
    },
  },

  products: {
    list: () => {
      const s = load()
      updateProductStockTotals(s)
      save(s)
      return [...s.products].sort((a, b) => a.name.localeCompare(b.name))
    },
    create: (data: Partial<Product>) => {
      const s = load()
      const product: Product = {
        id: nextId(s),
        name: data.name || '',
        sku: data.sku,
        unit: data.unit || 'шт',
        price: data.price || 0,
        description: data.description,
        created_at: now(),
        total_stock: 0,
      }
      s.products.push(product)
      save(s)
      return product
    },
    update: (id: number, data: Partial<Product>) => {
      const s = load()
      const i = s.products.findIndex((p) => p.id === id)
      if (i < 0) throw new Error('Товар не найден')
      s.products[i] = { ...s.products[i], ...data }
      updateProductStockTotals(s)
      save(s)
      return s.products[i]
    },
    delete: (id: number) => {
      const s = load()
      s.products = s.products.filter((p) => p.id !== id)
      s.stocks = s.stocks.filter((st) => st.product_id !== id)
      save(s)
    },
  },

  warehouses: {
    list: () => load().warehouses.sort((a, b) => a.name.localeCompare(b.name)),
    create: (data: Partial<Warehouse>) => {
      const s = load()
      if (data.is_default) s.warehouses.forEach((w) => { w.is_default = false })
      const warehouse: Warehouse = {
        id: nextId(s),
        name: data.name || '',
        address: data.address,
        is_default: data.is_default || false,
        created_at: now(),
      }
      s.warehouses.push(warehouse)
      save(s)
      return warehouse
    },
  },

  stocks: {
    list: (params?: { warehouse_id?: number; product_id?: number }) => {
      const s = load()
      let stocks = s.stocks
      if (params?.warehouse_id) stocks = stocks.filter((st) => st.warehouse_id === params.warehouse_id)
      if (params?.product_id) stocks = stocks.filter((st) => st.product_id === params.product_id)
      return stocks.map((st) => {
        const product = s.products.find((p) => p.id === st.product_id)
        const warehouse = s.warehouses.find((w) => w.id === st.warehouse_id)
        return {
          ...st,
          available: st.quantity - st.reserved,
          product_name: product?.name,
          warehouse_name: warehouse?.name,
        }
      })
    },
  },

  movements: {
    list: () => {
      const s = load()
      return s.movements
        .map((m) => ({
          ...m,
          product_name: s.products.find((p) => p.id === m.product_id)?.name,
          warehouse_name: s.warehouses.find((w) => w.id === m.warehouse_id)?.name,
        }))
        .sort((a, b) => b.created_at.localeCompare(a.created_at))
    },
    create: (data: Partial<StockMovement>) => {
      const s = load()
      const product = s.products.find((p) => p.id === data.product_id)
      const warehouse = s.warehouses.find((w) => w.id === data.warehouse_id)
      if (!product || !warehouse) throw new Error('Товар или склад не найден')

      const movement: StockMovement = {
        id: nextId(s),
        product_id: data.product_id!,
        warehouse_id: data.warehouse_id!,
        movement_type: data.movement_type || 'receipt',
        quantity: data.quantity || 0,
        to_warehouse_id: data.to_warehouse_id,
        deal_id: data.deal_id,
        comment: data.comment,
        created_at: now(),
        product_name: product.name,
        warehouse_name: warehouse.name,
      }

      const getStock = (productId: number, warehouseId: number) => {
        let st = s.stocks.find((x) => x.product_id === productId && x.warehouse_id === warehouseId)
        if (!st) {
          st = { id: nextId(s), product_id: productId, warehouse_id: warehouseId, quantity: 0, reserved: 0 }
          s.stocks.push(st)
        }
        return st
      }

      if (movement.movement_type === 'receipt') {
        getStock(movement.product_id, movement.warehouse_id).quantity += movement.quantity
      } else if (movement.movement_type === 'expense') {
        const st = getStock(movement.product_id, movement.warehouse_id)
        if (st.quantity - st.reserved < movement.quantity) throw new Error('Недостаточно товара на складе')
        st.quantity -= movement.quantity
      } else if (movement.movement_type === 'transfer' && movement.to_warehouse_id) {
        const from = getStock(movement.product_id, movement.warehouse_id)
        if (from.quantity - from.reserved < movement.quantity) throw new Error('Недостаточно товара для перемещения')
        from.quantity -= movement.quantity
        getStock(movement.product_id, movement.to_warehouse_id).quantity += movement.quantity
      } else if (movement.movement_type === 'adjustment') {
        getStock(movement.product_id, movement.warehouse_id).quantity = movement.quantity
      }

      s.movements.unshift(movement)
      updateProductStockTotals(s)
      save(s)
      return movement
    },
  },

  accounting: {
    invoices: {
      list: () => {
        const s = load()
        return s.taxInvoices.sort((a, b) => b.created_at.localeCompare(a.created_at))
      },
      create: (data: Partial<TaxInvoice>) => {
        const s = load()
        const { vat, total } = calcVat(data.amount || 0, data.vat_rate || 18)
        const inv: TaxInvoice = {
          id: nextId(s),
          number: `INV-${new Date().getFullYear()}-${String(s.taxInvoices.length + 1).padStart(4, '0')}`,
          deal_id: data.deal_id,
          company_id: data.company_id,
          tin_seller: data.tin_seller || '123456789',
          tin_buyer: data.tin_buyer || '',
          buyer_name: data.buyer_name,
          amount: data.amount || 0,
          vat_rate: data.vat_rate || 18,
          vat_amount: vat,
          total_amount: total,
          status: 'draft',
          description: data.description,
          created_at: now(),
        }
        s.taxInvoices.unshift(inv)
        save(s)
        return inv
      },
      sync: (id: number) => {
        const s = load()
        const inv = s.taxInvoices.find((i) => i.id === id)
        if (!inv) throw new Error('Счёт не найден')
        inv.rsge_transaction_id = `TXN-${Math.floor(Math.random() * 90000) + 10000}`
        inv.rsge_invoice_id = Math.floor(Math.random() * 9000) + 1000
        inv.status = 'sent'
        inv.synced_at = now()
        save(s)
        return inv
      },
      activate: (id: number) => {
        const s = load()
        const inv = s.taxInvoices.find((i) => i.id === id)
        if (!inv) throw new Error('Счёт не найден')
        inv.status = 'active'
        save(s)
        return inv
      },
    },
    settings: {
      get: () => load().rsgeSettings,
      save: (data: Partial<RsgeSettings> & { password?: string }) => {
        const s = load()
        s.rsgeSettings = {
          id: 1,
          company_tin: data.company_tin || '',
          username: data.username || '',
          is_connected: s.rsgeSettings?.is_connected || false,
          last_sync: s.rsgeSettings?.last_sync,
        }
        save(s)
        return s.rsgeSettings!
      },
    },
    rsge: {
      auth: (data: { username: string; password: string; pin?: string; pin_token?: string }): RsgeAuthResult => {
        const s = load()
        if (data.pin_token && !data.pin) {
          return { success: false, needs_pin: true, pin_token: 'mock-pin-token' }
        }
        if (s.rsgeSettings) {
          s.rsgeSettings.is_connected = true
          s.rsgeSettings.last_sync = now()
          save(s)
        }
        return { success: true, message: 'Подключено к RS.ge (демо)' }
      },
      checkVat: (tin: string): VatCheckResult => ({
        tin,
        is_vat_payer: tin.length >= 9,
        org_name: `სატესტო კომპანია ${tin.slice(0, 4)}`,
      }),
    },
  },
}
