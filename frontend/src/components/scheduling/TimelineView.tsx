import type { ScheduleEvent, ScheduleResource } from '../../api/client'
import { eventStatusClass, formatDayLabel, formatTime } from '../../crm/scheduleConfig'
import type { Locale } from '../../i18n/translations'

type Props = {
  resources: ScheduleResource[]
  events: ScheduleEvent[]
  locale: Locale
  onEventClick: (event: ScheduleEvent) => void
}

export default function TimelineView({ resources, events, locale, onEventClick }: Props) {
  const sorted = [...events].sort((a, b) => a.start_at.localeCompare(b.start_at))
  const resourceMap = Object.fromEntries(resources.map((r) => [r.id, r.name]))

  return (
    <div className="card divide-y divide-app-border">
      {sorted.map((ev) => (
        <button
          key={ev.id}
          type="button"
          onClick={() => onEventClick(ev)}
          className="w-full text-left p-4 hover:bg-app-bg-secondary transition-colors flex gap-4 items-start"
        >
          <div className="shrink-0 w-28 text-xs text-app-text-muted">
            <div>{formatDayLabel(ev.start_at.slice(0, 10), locale)}</div>
            {!ev.all_day && (
              <div>{formatTime(ev.start_at, locale)}</div>
            )}
          </div>
          <div className={`flex-1 rounded-lg px-3 py-2 text-sm ${eventStatusClass(ev.status)}`}>
            <div className="font-medium">{ev.title}</div>
            {ev.resource_id && (
              <div className="text-xs opacity-80 mt-0.5">{resourceMap[ev.resource_id]}</div>
            )}
            {!ev.all_day && (
              <div className="text-xs opacity-80 mt-0.5">
                → {formatTime(ev.end_at, locale)}
              </div>
            )}
          </div>
        </button>
      ))}
      {sorted.length === 0 && (
        <div className="p-8 text-center text-app-text-muted text-sm">—</div>
      )}
    </div>
  )
}
