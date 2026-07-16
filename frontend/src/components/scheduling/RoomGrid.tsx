import { useMemo } from 'react'
import type { ScheduleEvent, ScheduleResource } from '../../api/client'
import { dateRange, eventStatusClass, formatDayLabel } from '../../crm/scheduleConfig'
import type { Locale } from '../../i18n/translations'

type Props = {
  resources: ScheduleResource[]
  events: ScheduleEvent[]
  fromDate: string
  toDate: string
  locale: Locale
  onEventClick: (event: ScheduleEvent) => void
  onCellClick: (resourceId: number, date: string) => void
}

function dayIndex(days: string[], iso: string): number {
  const d = iso.slice(0, 10)
  return days.indexOf(d)
}

export default function RoomGrid({ resources, events, fromDate, toDate, locale, onEventClick, onCellClick }: Props) {
  const days = useMemo(() => {
    const start = new Date(`${fromDate}T12:00:00`)
    const end = new Date(`${toDate}T12:00:00`)
    const count = Math.round((end.getTime() - start.getTime()) / 86400000) + 1
    return dateRange(fromDate, Math.max(1, count))
  }, [fromDate, toDate])

  const eventsByResource = useMemo(() => {
    const map = new Map<number, ScheduleEvent[]>()
    for (const ev of events) {
      if (!ev.resource_id) continue
      const list = map.get(ev.resource_id) || []
      list.push(ev)
      map.set(ev.resource_id, list)
    }
    return map
  }, [events])

  const cellW = 88

  return (
    <div className="card overflow-x-auto">
      <div className="min-w-max">
        <div className="flex border-b border-app-border bg-app-bg-secondary sticky top-0 z-10">
          <div className="w-36 shrink-0 p-3 text-xs font-medium text-app-text-muted border-r border-app-border">
            #
          </div>
          {days.map((day) => (
            <div
              key={day}
              className="shrink-0 p-2 text-center text-xs font-medium text-app-text-muted border-r border-app-border"
              style={{ width: cellW }}
            >
              {formatDayLabel(day, locale)}
            </div>
          ))}
        </div>

        {resources.map((room) => {
          const roomEvents = eventsByResource.get(room.id) || []
          return (
            <div key={room.id} className="flex border-b border-app-border relative min-h-[52px]">
              <div className="w-36 shrink-0 p-3 border-r border-app-border bg-app-bg-secondary">
                <div className="font-medium text-sm text-app-text">{room.code}</div>
                <div className="text-xs text-app-text-muted truncate">{room.name}</div>
                {room.floor != null && (
                  <div className="text-xs text-app-text-muted">F{room.floor}</div>
                )}
              </div>
              <div className="relative flex" style={{ width: days.length * cellW }}>
                {days.map((day) => (
                  <button
                    key={day}
                    type="button"
                    onClick={() => onCellClick(room.id, day)}
                    className="shrink-0 border-r border-app-border/60 hover:bg-kinetix-50/50 dark:hover:bg-kinetix-900/20 transition-colors"
                    style={{ width: cellW, height: '100%' }}
                    aria-label={day}
                  />
                ))}
                {roomEvents.map((ev) => {
                  const start = dayIndex(days, ev.start_at)
                  let end = dayIndex(days, ev.end_at)
                  if (ev.all_day && end > start) end -= 0
                  const span = Math.max(1, (end > start ? end : start + 1) - Math.max(0, start))
                  if (start < 0) return null
                  return (
                    <button
                      key={ev.id}
                      type="button"
                      onClick={() => onEventClick(ev)}
                      className={`absolute top-1.5 bottom-1.5 rounded-md px-2 text-left text-xs truncate shadow-sm ${eventStatusClass(ev.status)}`}
                      style={{ left: start * cellW + 4, width: span * cellW - 8 }}
                      title={ev.guest_name || ev.title}
                    >
                      <div className="font-medium truncate">{ev.title}</div>
                      {ev.source && <div className="opacity-80 truncate text-[10px]">{ev.source}</div>}
                    </button>
                  )
                })}
              </div>
            </div>
          )
        })}

        {resources.length === 0 && (
          <div className="p-8 text-center text-app-text-muted text-sm">—</div>
        )}
      </div>
    </div>
  )
}
