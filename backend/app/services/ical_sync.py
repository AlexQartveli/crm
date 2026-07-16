"""Синхронизация iCal (Booking.com, Airbnb, Google Calendar)."""

from __future__ import annotations

from datetime import date, datetime, timedelta

import httpx
from icalendar import Calendar, Event as ICalEvent
from sqlalchemy.orm import Session

from app.models.scheduling import ICalFeed, ScheduleEvent, ScheduleResource

SYNC_TIMEOUT = 20.0


def _parse_dt(value) -> datetime | None:
    if value is None:
        return None
    if hasattr(value, "dt"):
        dt = value.dt
        if isinstance(dt, date) and not isinstance(dt, datetime):
            return datetime.combine(dt, datetime.min.time())
        if isinstance(dt, datetime):
            return dt.replace(tzinfo=None) if dt.tzinfo else dt
    return None


def _event_response_fields(event: ScheduleEvent, resource_name: str | None = None) -> dict:
    return {
        "id": event.id,
        "resource_id": event.resource_id,
        "title": event.title,
        "guest_name": event.guest_name,
        "phone": event.phone,
        "email": event.email,
        "start_at": event.start_at,
        "end_at": event.end_at,
        "all_day": event.all_day,
        "status": event.status,
        "source": event.source,
        "external_uid": event.external_uid,
        "notes": event.notes,
        "custom_data": event.custom_data,
        "lead_id": event.lead_id,
        "deal_id": event.deal_id,
        "contact_id": event.contact_id,
        "resource_name": resource_name,
        "created_at": event.created_at,
        "updated_at": event.updated_at,
    }


def export_ics(db: Session, tenant_id: int, *, resource_id: int | None = None) -> bytes:
    cal = Calendar()
    cal.add("prodid", "-//Kinetix CRM//Room Grid//RU")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("method", "PUBLISH")

    q = db.query(ScheduleEvent).filter(ScheduleEvent.tenant_id == tenant_id)
    if resource_id:
        q = q.filter(ScheduleEvent.resource_id == resource_id)
    events = q.order_by(ScheduleEvent.start_at).all()

    resources = {
        r.id: r.name
        for r in db.query(ScheduleResource).filter(ScheduleResource.tenant_id == tenant_id).all()
    }

    for ev in events:
        ical_ev = ICalEvent()
        uid = ev.external_uid or f"kinetix-{tenant_id}-event-{ev.id}@kinetix.local"
        ical_ev.add("uid", uid)
        ical_ev.add("summary", ev.title)
        if ev.guest_name:
            ical_ev.add("description", ev.guest_name)
        if ev.all_day:
            ical_ev.add("dtstart", ev.start_at.date())
            ical_ev.add("dtend", ev.end_at.date())
        else:
            ical_ev.add("dtstart", ev.start_at)
            ical_ev.add("dtend", ev.end_at)
        if ev.resource_id and ev.resource_id in resources:
            ical_ev.add("location", resources[ev.resource_id])
        ical_ev.add("dtstamp", datetime.utcnow())
        cal.add_component(ical_ev)

    return cal.to_ical()


def sync_feed(db: Session, feed: ICalFeed) -> dict[str, int]:
    imported = updated = skipped = 0
    try:
        resp = httpx.get(feed.url, timeout=SYNC_TIMEOUT, follow_redirects=True)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise ValueError(f"Не удалось загрузить iCal: {exc}") from exc

    cal = Calendar.from_ical(resp.content)
    for component in cal.walk():
        if component.name != "VEVENT":
            continue

        uid_raw = component.get("UID")
        if not uid_raw:
            skipped += 1
            continue
        uid = str(uid_raw)

        start = _parse_dt(component.get("DTSTART"))
        end = _parse_dt(component.get("DTEND"))
        if not start:
            skipped += 1
            continue
        if not end:
            end = start + timedelta(days=1)

        summary = str(component.get("SUMMARY", "Бронь"))
        description = str(component.get("DESCRIPTION", "")) if component.get("DESCRIPTION") else None
        all_day = not isinstance(component.get("DTSTART").dt, datetime) if component.get("DTSTART") else False

        existing = (
            db.query(ScheduleEvent)
            .filter(ScheduleEvent.tenant_id == feed.tenant_id, ScheduleEvent.external_uid == uid)
            .first()
        )

        payload = {
            "title": summary[:255],
            "guest_name": (description or summary)[:255] if description else None,
            "start_at": start,
            "end_at": end,
            "all_day": all_day,
            "status": "confirmed",
            "source": "ical",
            "resource_id": feed.resource_id,
        }

        if existing:
            for key, val in payload.items():
                setattr(existing, key, val)
            existing.updated_at = datetime.utcnow()
            updated += 1
        else:
            db.add(ScheduleEvent(
                tenant_id=feed.tenant_id,
                external_uid=uid,
                **payload,
            ))
            imported += 1

    feed.last_synced_at = datetime.utcnow()
    db.commit()
    return {"imported": imported, "updated": updated, "skipped": skipped}
