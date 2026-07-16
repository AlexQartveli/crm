import { useEffect, useState } from 'react'
import Modal from '../Modal'
import type { ScheduleEvent, ScheduleResource } from '../../api/client'
import { useI18n } from '../../i18n/I18nContext'

type Props = {
  open: boolean
  event: Partial<ScheduleEvent> | null
  resources: ScheduleResource[]
  defaultResourceId?: number
  defaultDate?: string
  allDayDefault?: boolean
  onClose: () => void
  onSave: (data: Partial<ScheduleEvent>) => Promise<void>
  onDelete?: (id: number) => Promise<void>
}

export default function EventModal({
  open,
  event,
  resources,
  defaultResourceId,
  defaultDate,
  allDayDefault = false,
  onClose,
  onSave,
  onDelete,
}: Props) {
  const { t } = useI18n()
  const [form, setForm] = useState({
    title: '',
    guest_name: '',
    phone: '',
    resource_id: '' as number | '',
    start_date: '',
    end_date: '',
    start_time: '14:00',
    end_time: '12:00',
    all_day: allDayDefault,
    status: 'confirmed',
    source: 'direct',
    notes: '',
  })
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (!open) return
    if (event?.id) {
      setForm({
        title: event.title || '',
        guest_name: event.guest_name || '',
        phone: event.phone || '',
        resource_id: event.resource_id ?? '',
        start_date: event.start_at?.slice(0, 10) || defaultDate || '',
        end_date: event.end_at?.slice(0, 10) || defaultDate || '',
        start_time: event.start_at?.slice(11, 16) || '14:00',
        end_time: event.end_at?.slice(11, 16) || '12:00',
        all_day: event.all_day ?? allDayDefault,
        status: event.status || 'confirmed',
        source: event.source || 'direct',
        notes: event.notes || '',
      })
    } else {
      setForm({
        title: '',
        guest_name: '',
        phone: '',
        resource_id: defaultResourceId ?? resources[0]?.id ?? '',
        start_date: defaultDate || new Date().toISOString().slice(0, 10),
        end_date: defaultDate || new Date().toISOString().slice(0, 10),
        start_time: '14:00',
        end_time: '12:00',
        all_day: allDayDefault,
        status: 'confirmed',
        source: 'direct',
        notes: '',
      })
    }
  }, [open, event, defaultResourceId, defaultDate, allDayDefault, resources])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    try {
      const start_at = form.all_day
        ? `${form.start_date}T14:00:00`
        : `${form.start_date}T${form.start_time}:00`
      const end_at = form.all_day
        ? `${form.end_date}T12:00:00`
        : `${form.end_date}T${form.end_time}:00`
      await onSave({
        id: event?.id,
        title: form.title || form.guest_name || t.schedule.newEvent,
        guest_name: form.guest_name || undefined,
        phone: form.phone || undefined,
        resource_id: form.resource_id === '' ? undefined : form.resource_id,
        start_at,
        end_at,
        all_day: form.all_day,
        status: form.status,
        source: form.source,
        notes: form.notes || undefined,
      })
      onClose()
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal open={open} onClose={onClose} title={event?.id ? t.schedule.editEvent : t.schedule.newEvent}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="label">{t.schedule.guestName}</label>
          <input className="input" value={form.guest_name} onChange={(e) => setForm({ ...form, guest_name: e.target.value, title: e.target.value })} />
        </div>
        <div>
          <label className="label">{t.schedule.phone}</label>
          <input className="input" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
        </div>
        <div>
          <label className="label">{t.schedule.resource}</label>
          <select className="input" value={form.resource_id} onChange={(e) => setForm({ ...form, resource_id: e.target.value ? +e.target.value : '' })}>
            <option value="">—</option>
            {resources.map((r) => (
              <option key={r.id} value={r.id}>{r.name}</option>
            ))}
          </select>
        </div>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={form.all_day} onChange={(e) => setForm({ ...form, all_day: e.target.checked })} />
          {t.schedule.allDay}
        </label>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label">{form.all_day ? t.schedule.checkIn : t.schedule.startDate}</label>
            <input type="date" className="input" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} required />
          </div>
          <div>
            <label className="label">{form.all_day ? t.schedule.checkOut : t.schedule.endDate}</label>
            <input type="date" className="input" value={form.end_date} onChange={(e) => setForm({ ...form, end_date: e.target.value })} required />
          </div>
        </div>
        {!form.all_day && (
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">{t.schedule.startTime}</label>
              <input type="time" className="input" value={form.start_time} onChange={(e) => setForm({ ...form, start_time: e.target.value })} />
            </div>
            <div>
              <label className="label">{t.schedule.endTime}</label>
              <input type="time" className="input" value={form.end_time} onChange={(e) => setForm({ ...form, end_time: e.target.value })} />
            </div>
          </div>
        )}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label">{t.schedule.status}</label>
            <select className="input" value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
              <option value="confirmed">{t.schedule.statusConfirmed}</option>
              <option value="pending">{t.schedule.statusPending}</option>
              <option value="cancelled">{t.schedule.statusCancelled}</option>
              <option value="in_progress">{t.schedule.statusInProgress}</option>
            </select>
          </div>
          <div>
            <label className="label">{t.schedule.source}</label>
            <select className="input" value={form.source} onChange={(e) => setForm({ ...form, source: e.target.value })}>
              <option value="direct">{t.schedule.sourceDirect}</option>
              <option value="booking.com">Booking.com</option>
              <option value="airbnb">Airbnb</option>
              <option value="ical">iCal</option>
            </select>
          </div>
        </div>
        <div>
          <label className="label">{t.schedule.notes}</label>
          <textarea className="input" rows={2} value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
        </div>
        <div className="flex gap-2 justify-end pt-2">
          {event?.id && onDelete && (
            <button
              type="button"
              className="btn-secondary text-red-600 mr-auto"
              onClick={async () => {
                await onDelete(event.id!)
                onClose()
              }}
            >
              {t.common.delete}
            </button>
          )}
          <button type="button" className="btn-secondary" onClick={onClose}>{t.common.cancel}</button>
          <button type="submit" className="btn-primary" disabled={saving}>{saving ? t.common.loading : t.common.save}</button>
        </div>
      </form>
    </Modal>
  )
}
