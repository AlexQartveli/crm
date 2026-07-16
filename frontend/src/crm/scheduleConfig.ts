export type ScheduleView = 'grid' | 'calendar' | 'timeline'

export const SCHEDULE_BY_CRM: Record<string, { view: ScheduleView; resourceType: string }> = {
  hospitality: { view: 'grid', resourceType: 'room' },
  medical: { view: 'calendar', resourceType: 'doctor' },
  education: { view: 'calendar', resourceType: 'classroom' },
  logistics: { view: 'timeline', resourceType: 'vehicle' },
  construction: { view: 'timeline', resourceType: 'site' },
  factory: { view: 'calendar', resourceType: 'line' },
  services: { view: 'calendar', resourceType: 'specialist' },
  agriculture: { view: 'calendar', resourceType: 'field' },
  retail: { view: 'calendar', resourceType: 'store' },
}

export function scheduleConfig(crmType: string) {
  return SCHEDULE_BY_CRM[crmType] ?? { view: 'calendar' as ScheduleView, resourceType: 'resource' }
}

export function addDays(iso: string, days: number): string {
  const d = new Date(iso + 'T12:00:00')
  d.setDate(d.getDate() + days)
  return d.toISOString().slice(0, 10)
}

export function todayIso(): string {
  return new Date().toISOString().slice(0, 10)
}

export function dateRange(from: string, days: number): string[] {
  const result: string[] = []
  for (let i = 0; i < days; i += 1) {
    result.push(addDays(from, i))
  }
  return result
}

export function formatDayLabel(iso: string, locale: string): string {
  const d = new Date(iso + 'T12:00:00')
  return d.toLocaleDateString(locale === 'ka' ? 'ka-GE' : locale === 'en' ? 'en-GB' : 'ru-RU', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
  })
}

export function formatTime(iso: string, locale: string): string {
  const d = new Date(iso)
  return d.toLocaleTimeString(locale === 'ka' ? 'ka-GE' : locale === 'en' ? 'en-GB' : 'ru-RU', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

const STATUS_COLORS: Record<string, string> = {
  confirmed: 'bg-green-500/90 text-white',
  pending: 'bg-yellow-500/90 text-white',
  cancelled: 'bg-gray-400/80 text-white',
  in_progress: 'bg-blue-500/90 text-white',
  checked_in: 'bg-kinetix-600 text-white',
}

export function eventStatusClass(status: string): string {
  return STATUS_COLORS[status] || 'bg-kinetix-500 text-white'
}
