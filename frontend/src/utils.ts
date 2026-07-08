import { useI18n } from './i18n/I18nContext'
import type { Translations } from './i18n/translations'

type StatusInfo = { label: string; color: string }

function mapStatuses(
  labels: Record<string, string>,
  colors: Record<string, string>,
): Record<string, StatusInfo> {
  return Object.fromEntries(
    Object.entries(labels).map(([k, label]) => [k, { label, color: colors[k] || '' }]),
  )
}

const STAGE_COLORS: Record<string, string> = {
  new: 'bg-blue-100 text-blue-800 dark:bg-blue-950/60 dark:text-blue-300',
  preparation: 'bg-purple-100 text-purple-800 dark:bg-purple-950/60 dark:text-purple-300',
  proposal: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-950/60 dark:text-yellow-300',
  negotiation: 'bg-orange-100 text-orange-800 dark:bg-orange-950/60 dark:text-orange-300',
  won: 'bg-green-100 text-green-800 dark:bg-green-950/60 dark:text-green-300',
  lost: 'bg-red-100 text-red-800 dark:bg-red-950/60 dark:text-red-300',
}

const LEAD_COLORS: Record<string, string> = {
  new: 'bg-blue-100 text-blue-800 dark:bg-blue-950/60 dark:text-blue-300',
  in_progress: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-950/60 dark:text-yellow-300',
  converted: 'bg-green-100 text-green-800 dark:bg-green-950/60 dark:text-green-300',
  junk: 'bg-gray-100 text-gray-800 dark:bg-slate-700 dark:text-slate-300',
}

const INVOICE_COLORS: Record<string, string> = {
  draft: 'bg-gray-100 text-gray-800 dark:bg-slate-700 dark:text-slate-300',
  pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-950/60 dark:text-yellow-300',
  sent: 'bg-blue-100 text-blue-800 dark:bg-blue-950/60 dark:text-blue-300',
  active: 'bg-green-100 text-green-800 dark:bg-green-950/60 dark:text-green-300',
  cancelled: 'bg-red-100 text-red-800 dark:bg-red-950/60 dark:text-red-300',
  refused: 'bg-red-100 text-red-800 dark:bg-red-950/60 dark:text-red-300',
}

export function useStatuses(): {
  dealStages: Record<string, StatusInfo>
  leadStatuses: Record<string, StatusInfo>
  invoiceStatuses: Record<string, StatusInfo>
  movementTypes: Translations['movementTypes']
} {
  const { t } = useI18n()

  return {
    dealStages: mapStatuses(t.dealStages, STAGE_COLORS),
    leadStatuses: mapStatuses(t.leadStatuses, LEAD_COLORS),
    invoiceStatuses: mapStatuses(t.invoiceStatuses, INVOICE_COLORS),
    movementTypes: t.movementTypes,
  }
}

export function formatMoney(amount: number, locale?: string): string {
  const loc = locale || localStorage.getItem('kinetix_locale') || 'ka'
  const fmtLocale = loc === 'ka' ? 'ka-GE' : loc === 'en' ? 'en-US' : 'ru-RU'
  try {
    return new Intl.NumberFormat(fmtLocale, {
      style: 'currency',
      currency: 'GEL',
      maximumFractionDigits: 0,
    }).format(amount)
  } catch {
    return `${Math.round(amount)} ₾`
  }
}

export function formatDate(date: string, locale?: string): string {
  const loc = locale || localStorage.getItem('kinetix_locale') || 'ka'
  const fmtLocale = loc === 'ka' ? 'ka-GE' : loc === 'en' ? 'en-GB' : 'ru-RU'
  return new Intl.DateTimeFormat(fmtLocale, {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(new Date(date))
}
