export const PERM = {
  dashboard: 'dashboard.view',
  leadsView: 'crm.leads.view',
  leadsManage: 'crm.leads.manage',
  dealsView: 'crm.deals.view',
  dealsManage: 'crm.deals.manage',
  contactsView: 'crm.contacts.view',
  contactsManage: 'crm.contacts.manage',
  companiesView: 'crm.companies.view',
  companiesManage: 'crm.companies.manage',
  productsView: 'warehouse.products.view',
  productsManage: 'warehouse.products.manage',
  stocksView: 'warehouse.stocks.view',
  movementsView: 'warehouse.movements.view',
  movementsManage: 'warehouse.movements.manage',
  accountingView: 'accounting.view',
  accountingManage: 'accounting.manage',
  accountingSettings: 'accounting.settings',
  inbox: 'messaging.inbox',
  integrations: 'messaging.integrations',
  automationsView: 'automations.view',
  automationsManage: 'automations.manage',
  usersManage: 'users.manage',
} as const

export type Permission = (typeof PERM)[keyof typeof PERM]

export const ROUTE_PERMISSIONS: Record<string, Permission> = {
  '/': PERM.dashboard,
  '/leads': PERM.leadsView,
  '/deals': PERM.dealsView,
  '/contacts': PERM.contactsView,
  '/companies': PERM.companiesView,
  '/products': PERM.productsView,
  '/warehouse': PERM.stocksView,
  '/movements': PERM.movementsView,
  '/inbox': PERM.inbox,
  '/bots': PERM.automationsView,
  '/integrations': PERM.integrations,
  '/accounting': PERM.accountingView,
  '/accounting/settings': PERM.accountingSettings,
  '/users': PERM.usersManage,
  '/cabinet': PERM.dashboard,
}

export const ROLE_LABELS: Record<string, { ru: string; en: string; ka: string }> = {
  admin: { ru: 'Администратор', en: 'Administrator', ka: 'ადმინისტრატორი' },
  director: { ru: 'Руководитель', en: 'Director', ka: 'ხელმძღვანელი' },
  sales: { ru: 'Менеджер по продажам', en: 'Sales manager', ka: 'გაყიდვების მენეჯერი' },
  operator: { ru: 'Оператор поддержки', en: 'Support operator', ka: 'ოპერატორი' },
  warehouse: { ru: 'Кладовщик', en: 'Warehouse manager', ka: 'საწყობის მენეჯერი' },
  accountant: { ru: 'Бухгалтер', en: 'Accountant', ka: 'ბუღალტერი' },
}

export function canAccess(permissions: string[], permission: string): boolean {
  return permissions.includes(permission)
}

export function firstAllowedRoute(permissions: string[]): string {
  for (const [route, perm] of Object.entries(ROUTE_PERMISSIONS)) {
    if (canAccess(permissions, perm)) return route
  }
  return '/login'
}
