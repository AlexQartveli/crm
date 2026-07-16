import type { CrmConfig, CrmFieldDef } from '../api/client'
import type { Locale } from '../i18n/translations'

export type { CrmConfig, CrmFieldDef }

export const STATUS_COLORS: Record<string, string> = {
  blue: 'bg-blue-100 text-blue-800 dark:bg-blue-950/60 dark:text-blue-300',
  purple: 'bg-purple-100 text-purple-800 dark:bg-purple-950/60 dark:text-purple-300',
  yellow: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-950/60 dark:text-yellow-300',
  orange: 'bg-orange-100 text-orange-800 dark:bg-orange-950/60 dark:text-orange-300',
  green: 'bg-green-100 text-green-800 dark:bg-green-950/60 dark:text-green-300',
  red: 'bg-red-100 text-red-800 dark:bg-red-950/60 dark:text-red-300',
  gray: 'bg-gray-100 text-gray-800 dark:bg-slate-700 dark:text-slate-300',
}

export const ROUTE_MODULE: Record<string, string> = {
  '/': 'dashboard',
  '/leads': 'leads',
  '/deals': 'deals',
  '/contacts': 'contacts',
  '/companies': 'companies',
  '/products': 'products',
  '/warehouse': 'warehouse',
  '/movements': 'movements',
  '/inbox': 'inbox',
  '/bots': 'bots',
  '/integrations': 'integrations',
  '/accounting': 'accounting',
  '/accounting/settings': 'accounting',
  '/cabinet': 'cabinet',
  '/users': 'users',
}

type Label3 = { ru: string; en: string; ka: string }

export function pickLabel(label: Label3 | undefined, locale: Locale, fallback: string): string {
  if (!label) return fallback
  if (locale === 'en') return label.en
  if (locale === 'ka') return label.ka
  return label.ru
}

export function fieldLabel(field: CrmFieldDef, locale: Locale): string {
  if (locale === 'en') return field.label_en
  if (locale === 'ka') return field.label_ka
  return field.label_ru
}

export function optionLabel(
  opt: { label_ru: string; label_en: string; label_ka: string },
  locale: Locale,
): string {
  if (locale === 'en') return opt.label_en
  if (locale === 'ka') return opt.label_ka
  return opt.label_ru
}

export function statusLabel(
  status: { label_ru: string; label_en: string; label_ka: string },
  locale: Locale,
): string {
  if (locale === 'en') return status.label_en
  if (locale === 'ka') return status.label_ka
  return status.label_ru
}

export function mapStatuses(
  items: CrmConfig['deal_stages'],
  locale: Locale,
): Record<string, { label: string; color: string }> {
  return Object.fromEntries(
    items.map((s) => [s.key, { label: statusLabel(s, locale), color: STATUS_COLORS[s.color] || STATUS_COLORS.blue }]),
  )
}

export function entityTitle(config: CrmConfig | null, entity: string, locale: Locale, fallback: string): string {
  return pickLabel(config?.labels[entity], locale, fallback)
}

export function hasModule(config: CrmConfig | null, module: string): boolean {
  if (!config) return true
  return config.modules.includes(module)
}

export function isFieldHidden(config: CrmConfig | null, entity: string, field: string): boolean {
  return config?.hide_base_fields[entity]?.includes(field) ?? false
}

export function listFields(config: CrmConfig | null, entity: string): CrmFieldDef[] {
  return (config?.fields[entity] || []).filter((f) => f.show_in_list)
}

export function formatCustomValue(
  field: CrmFieldDef,
  value: unknown,
  locale: Locale,
): string {
  if (value === null || value === undefined || value === '') return '—'
  if (field.type === 'select' && field.options) {
    const opt = field.options.find((o) => o.id === value)
    return opt ? optionLabel(opt, locale) : String(value)
  }
  return String(value)
}
