import { useCallback, useEffect, useState } from 'react'
import { ChevronLeft, ChevronRight, Plus } from 'lucide-react'
import { api, ICalFeed, ScheduleEvent, ScheduleResource } from '../api/client'
import EventCalendar from '../components/scheduling/EventCalendar'
import EventModal from '../components/scheduling/EventModal'
import ICalPanel from '../components/scheduling/ICalPanel'
import RoomGrid from '../components/scheduling/RoomGrid'
import TimelineView from '../components/scheduling/TimelineView'
import { useCrmConfig } from '../crm/CrmConfigContext'
import { addDays, scheduleConfig, todayIso } from '../crm/scheduleConfig'
import { useI18n } from '../i18n/I18nContext'

const GRID_DAYS = 14
const CALENDAR_DAYS = 7

export default function Schedule() {
  const { t, locale } = useI18n()
  const { config, entityLabel } = useCrmConfig()
  const crmType = config?.crm_type || 'general'
  const { view, resourceType } = scheduleConfig(crmType)
  const isHospitality = view === 'grid'

  const [fromDate, setFromDate] = useState(todayIso())
  const [resources, setResources] = useState<ScheduleResource[]>([])
  const [events, setEvents] = useState<ScheduleEvent[]>([])
  const [feeds, setFeeds] = useState<ICalFeed[]>([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [editEvent, setEditEvent] = useState<ScheduleEvent | null>(null)
  const [defaultResourceId, setDefaultResourceId] = useState<number | undefined>()
  const [defaultDate, setDefaultDate] = useState<string | undefined>()

  const rangeDays = isHospitality ? GRID_DAYS : CALENDAR_DAYS
  const toDate = addDays(fromDate, rangeDays - 1)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const [resList, feedList] = await Promise.all([
        api.scheduling.resources.list(resourceType),
        api.scheduling.ical.feeds.list().catch(() => [] as ICalFeed[]),
      ])
      setResources(resList)
      setFeeds(feedList)

      if (isHospitality) {
        const grid = await api.scheduling.grid(fromDate, toDate, resourceType)
        setEvents(grid.events)
      } else {
        const evList = await api.scheduling.events.list(fromDate, toDate, { resource_type: resourceType })
        setEvents(evList)
      }
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }, [fromDate, toDate, resourceType, isHospitality])

  useEffect(() => { load() }, [load])

  const title = entityLabel('schedule', t.schedule.title)

  const openCreate = (resourceId?: number, date?: string) => {
    setEditEvent(null)
    setDefaultResourceId(resourceId)
    setDefaultDate(date)
    setModalOpen(true)
  }

  const openEdit = (ev: ScheduleEvent) => {
    setEditEvent(ev)
    setModalOpen(true)
  }

  const handleSave = async (data: Partial<ScheduleEvent>) => {
    if (data.id) {
      await api.scheduling.events.update(data.id, data)
    } else {
      await api.scheduling.events.create({ ...data, all_day: data.all_day ?? isHospitality })
    }
    await load()
  }

  const handleDelete = async (id: number) => {
    await api.scheduling.events.delete(id)
    await load()
  }

  const shiftRange = (delta: number) => {
    setFromDate(addDays(fromDate, delta * rangeDays))
  }

  return (
    <div className="p-8 space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="page-title">{title}</h1>
          <p className="text-sm text-app-text-muted mt-1">{t.schedule.subtitle}</p>
        </div>
        <div className="flex items-center gap-2">
          <button type="button" className="btn-secondary p-2" onClick={() => shiftRange(-1)}>
            <ChevronLeft size={18} />
          </button>
          <span className="text-sm text-app-text min-w-[140px] text-center">
            {fromDate} — {toDate}
          </span>
          <button type="button" className="btn-secondary p-2" onClick={() => shiftRange(1)}>
            <ChevronRight size={18} />
          </button>
          <button type="button" className="btn-primary flex items-center gap-1" onClick={() => openCreate()}>
            <Plus size={16} />
            {t.schedule.addEvent}
          </button>
        </div>
      </div>

      {isHospitality && (
        <ICalPanel feeds={feeds} resources={resources} onRefresh={load} />
      )}

      {loading ? (
        <div className="text-app-text-muted">{t.common.loading}</div>
      ) : view === 'grid' ? (
        <RoomGrid
          resources={resources}
          events={events}
          fromDate={fromDate}
          toDate={toDate}
          locale={locale}
          onEventClick={openEdit}
          onCellClick={(resourceId, date) => openCreate(resourceId, date)}
        />
      ) : view === 'timeline' ? (
        <TimelineView resources={resources} events={events} locale={locale} onEventClick={openEdit} />
      ) : (
        <EventCalendar
          resources={resources}
          events={events}
          fromDate={fromDate}
          locale={locale}
          onEventClick={openEdit}
          onSlotClick={(resourceId, date) => openCreate(resourceId, date)}
        />
      )}

      <EventModal
        open={modalOpen}
        event={editEvent}
        resources={resources}
        defaultResourceId={defaultResourceId}
        defaultDate={defaultDate}
        allDayDefault={isHospitality}
        onClose={() => setModalOpen(false)}
        onSave={handleSave}
        onDelete={editEvent ? handleDelete : undefined}
      />
    </div>
  )
}
