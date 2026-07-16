import type { ScheduleEvent, ScheduleResource } from '../../api/client'
import { eventStatusClass, formatDayLabel, formatTime } from '../../crm/scheduleConfig'
import type { Locale } from '../../i18n/translations'

type Props = {
  resources: ScheduleResource[]
  events: ScheduleEvent[]
  fromDate: string
  locale: Locale
  onEventClick: (event: ScheduleEvent) => void
  onSlotClick?: (resourceId: number, date: string) => void
}

export default function EventCalendar({ resources, events, fromDate, locale, onEventClick, onSlotClick }: Props) {
  const grouped = events.reduce<Record<string, ScheduleEvent[]>>((acc, ev) => {
    const day = ev.start_at.slice(0, 10)
    acc[day] = acc[day] || []
    acc[day].push(ev)
    return acc
  }, {})

  const days = Object.keys(grouped).sort()
  if (days.length === 0 && events.length > 0) {
    days.push(fromDate)
  }

  const displayDays = days.length ? days : [fromDate]

  return (
    <div className="space-y-4">
      {resources.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {resources.map((r) => (
            <span key={r.id} className="text-xs px-2 py-1 rounded-full bg-app-bg-secondary border border-app-border">
              {r.name}
            </span>
          ))}
        </div>
      )}

      {displayDays.map((day) => (
        <div key={day} className="card p-4">
          <h3 className="font-semibold text-app-text mb-3">{formatDayLabel(day, locale)}</h3>
          <div className="space-y-2">
            {(grouped[day] || []).map((ev) => (
              <button
                key={ev.id}
                type="button"
                onClick={() => onEventClick(ev)}
                className={`w-full text-left rounded-lg px-3 py-2 text-sm ${eventStatusClass(ev.status)}`}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="font-medium">{ev.title}</span>
                  {!ev.all_day && (
                    <span className="text-xs opacity-90">
                      {formatTime(ev.start_at, locale)} – {formatTime(ev.end_at, locale)}
                    </span>
                  )}
                </div>
                {ev.resource_name && <div className="text-xs opacity-80 mt-0.5">{ev.resource_name}</div>}
              </button>
            ))}
            {(grouped[day] || []).length === 0 && (
              <button
                type="button"
                onClick={() => onSlotClick?.(resources[0]?.id ?? 0, day)}
                className="w-full text-sm text-app-text-muted py-4 border border-dashed border-app-border rounded-lg hover:border-kinetix-400"
              >
                +
              </button>
            )}
          </div>
        </div>
      ))}

      {events.length === 0 && (
        <div className="card p-8 text-center text-app-text-muted text-sm">—</div>
      )}
    </div>
  )
}
