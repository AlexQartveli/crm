import { useState } from 'react'
import { Download, Plus, RefreshCw, Trash2 } from 'lucide-react'
import { api, getAuthToken, ICalFeed, ScheduleResource } from '../../api/client'
import { useI18n } from '../../i18n/I18nContext'

type Props = {
  feeds: ICalFeed[]
  resources: ScheduleResource[]
  onRefresh: () => void
}

export default function ICalPanel({ feeds, resources, onRefresh }: Props) {
  const { t } = useI18n()
  const [name, setName] = useState('')
  const [url, setUrl] = useState('')
  const [resourceId, setResourceId] = useState<number | ''>('')
  const [busy, setBusy] = useState<number | 'all' | null>(null)

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim() || !url.trim()) return
    await api.scheduling.ical.feeds.create({
      name: name.trim(),
      url: url.trim(),
      resource_id: resourceId === '' ? undefined : resourceId,
    })
    setName('')
    setUrl('')
    setResourceId('')
    onRefresh()
  }

  const handleSync = async (id: number) => {
    setBusy(id)
    try {
      await api.scheduling.ical.feeds.sync(id)
      onRefresh()
    } finally {
      setBusy(null)
    }
  }

  const handleSyncAll = async () => {
    setBusy('all')
    try {
      await api.scheduling.ical.feeds.syncAll()
      onRefresh()
    } finally {
      setBusy(null)
    }
  }

  const handleExport = async (resourceId?: number) => {
    const token = getAuthToken()
    const exportUrl = api.scheduling.ical.exportUrl(resourceId)
    const res = await fetch(exportUrl, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
    const blob = await res.blob()
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = resourceId ? `room-${resourceId}.ics` : 'schedule.ics'
    a.click()
    URL.revokeObjectURL(a.href)
  }

  return (
    <div className="card p-5 space-y-4">
      <div className="flex items-center justify-between gap-2 flex-wrap">
        <h3 className="font-semibold text-app-text">{t.schedule.icalTitle}</h3>
        <div className="flex gap-2">
          <button type="button" className="btn-secondary text-sm flex items-center gap-1" onClick={() => handleExport()}>
            <Download size={14} />
            {t.schedule.exportAll}
          </button>
          {feeds.length > 0 && (
            <button
              type="button"
              className="btn-secondary text-sm flex items-center gap-1"
              disabled={busy === 'all'}
              onClick={handleSyncAll}
            >
              <RefreshCw size={14} className={busy === 'all' ? 'animate-spin' : ''} />
              {t.schedule.syncAll}
            </button>
          )}
        </div>
      </div>

      <p className="text-xs text-app-text-muted">{t.schedule.icalHint}</p>

      <form onSubmit={handleAdd} className="grid sm:grid-cols-2 gap-3">
        <input className="input" placeholder={t.schedule.feedName} value={name} onChange={(e) => setName(e.target.value)} />
        <input className="input sm:col-span-2" placeholder="https://..." value={url} onChange={(e) => setUrl(e.target.value)} />
        <select className="input" value={resourceId} onChange={(e) => setResourceId(e.target.value ? +e.target.value : '')}>
          <option value="">{t.schedule.allResources}</option>
          {resources.map((r) => (
            <option key={r.id} value={r.id}>{r.name}</option>
          ))}
        </select>
        <button type="submit" className="btn-primary flex items-center justify-center gap-1">
          <Plus size={14} />
          {t.schedule.addFeed}
        </button>
      </form>

      {feeds.length > 0 && (
        <ul className="divide-y divide-app-border text-sm">
          {feeds.map((feed) => (
            <li key={feed.id} className="py-3 flex items-start justify-between gap-3">
              <div className="min-w-0">
                <div className="font-medium text-app-text">{feed.name}</div>
                <div className="text-xs text-app-text-muted truncate">{feed.url}</div>
                {feed.last_synced_at && (
                  <div className="text-xs text-app-text-muted mt-0.5">
                    {t.schedule.lastSync}: {new Date(feed.last_synced_at).toLocaleString()}
                  </div>
                )}
              </div>
              <div className="flex gap-1 shrink-0">
                <button
                  type="button"
                  className="p-2 rounded hover:bg-app-bg-secondary"
                  disabled={busy === feed.id}
                  onClick={() => handleSync(feed.id)}
                  title={t.schedule.sync}
                >
                  <RefreshCw size={14} className={busy === feed.id ? 'animate-spin' : ''} />
                </button>
                <button
                  type="button"
                  className="p-2 rounded hover:bg-app-bg-secondary text-red-500"
                  onClick={async () => {
                    await api.scheduling.ical.feeds.delete(feed.id)
                    onRefresh()
                  }}
                >
                  <Trash2 size={14} />
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
