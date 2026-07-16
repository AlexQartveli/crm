"""Стартовые ресурсы и события расписания по отраслям."""

from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.schedule_industry import resource_type_for
from app.models.scheduling import ScheduleEvent, ScheduleResource


def _has_resources(db: Session, tenant_id: int, resource_type: str) -> bool:
    return (
        db.query(ScheduleResource)
        .filter(ScheduleResource.tenant_id == tenant_id, ScheduleResource.resource_type == resource_type)
        .first()
        is not None
    )


def seed_schedule(db: Session, tenant_id: int, crm_type: str) -> None:
    rtype = resource_type_for(crm_type)
    if rtype == "resource" or _has_resources(db, tenant_id, rtype):
        return

    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    if crm_type == "hospitality":
        rooms = [
            ("101", "Standard 101", 2, 1, {"room_type": "standard"}),
            ("102", "Standard 102", 2, 1, {"room_type": "standard"}),
            ("201", "Deluxe 201", 2, 2, {"room_type": "deluxe"}),
            ("202", "Deluxe 202", 3, 2, {"room_type": "deluxe"}),
            ("301", "Suite 301", 4, 3, {"room_type": "suite"}),
            ("302", "Family 302", 5, 3, {"room_type": "family"}),
        ]
        resources: list[ScheduleResource] = []
        for i, (code, name, cap, floor, meta) in enumerate(rooms):
            r = ScheduleResource(
                tenant_id=tenant_id,
                resource_type="room",
                code=code,
                name=name,
                capacity=cap,
                floor=floor,
                meta=meta,
                sort_order=i,
            )
            db.add(r)
            resources.append(r)
        db.flush()

        bookings = [
            (0, "Thomas Mueller", "+49 170 1234567", 2, 3, "confirmed", "booking.com"),
            (2, "Giorgi Beridze", "+995 555 123456", 5, 2, "confirmed", "direct"),
            (1, "Airbnb Guest", "+1 555 0100", 8, 4, "pending", "airbnb"),
            (4, "Corporate — Silk Road", "+995 322 000000", 12, 5, "confirmed", "direct"),
        ]
        for room_idx, guest, phone, start_off, nights, status, source in bookings:
            check_in = today + timedelta(days=start_off)
            check_out = check_in + timedelta(days=nights)
            db.add(ScheduleEvent(
                tenant_id=tenant_id,
                resource_id=resources[room_idx].id,
                title=guest,
                guest_name=guest,
                phone=phone,
                start_at=check_in,
                end_at=check_out,
                all_day=True,
                status=status,
                source=source,
            ))
        db.commit()
        return

    if crm_type == "medical":
        doctors = [
            ("dr-smith", "Dr. Nino Kvirikashvili", 1, {"specialty": "therapy"}),
            ("dr-dent", "Dr. Luka Gvasalia", 1, {"specialty": "dentistry"}),
            ("cab-1", "Cabinet 1", 1, {"specialty": "diagnostics"}),
        ]
        resources = []
        for i, (code, name, cap, meta) in enumerate(doctors):
            r = ScheduleResource(tenant_id=tenant_id, resource_type="doctor", code=code, name=name, capacity=cap, meta=meta, sort_order=i)
            db.add(r)
            resources.append(r)
        db.flush()
        slots = [
            (0, "Patient — Ana", 1, 10, 0, 10, 30),
            (1, "Patient — David", 2, 14, 0, 14, 45),
            (2, "Check-up — Maria", 3, 11, 0, 11, 30),
        ]
        for res_idx, title, day_off, h, m, eh, em in slots:
            start = today + timedelta(days=day_off, hours=h, minutes=m)
            end = today + timedelta(days=day_off, hours=eh, minutes=em)
            db.add(ScheduleEvent(
                tenant_id=tenant_id, resource_id=resources[res_idx].id,
                title=title, guest_name=title, start_at=start, end_at=end,
                status="confirmed", source="direct",
            ))
        db.commit()
        return

    if crm_type == "education":
        rooms = [
            ("aud-a", "Auditorium A", 40, {"building": "main"}),
            ("lab-1", "Computer Lab", 20, {"building": "tech"}),
            ("room-12", "Classroom 12", 25, {"building": "main"}),
        ]
        resources = []
        for i, (code, name, cap, meta) in enumerate(rooms):
            r = ScheduleResource(tenant_id=tenant_id, resource_type="classroom", code=code, name=name, capacity=cap, meta=meta, sort_order=i)
            db.add(r)
            resources.append(r)
        db.flush()
        classes = [
            (0, "Math — Grade 10", 1, 9, 0, 10, 30),
            (1, "Programming Basics", 2, 14, 0, 16, 0),
            (2, "English B2", 3, 11, 0, 12, 30),
        ]
        for res_idx, title, day_off, h, m, eh, em in classes:
            start = today + timedelta(days=day_off, hours=h, minutes=m)
            end = today + timedelta(days=day_off, hours=eh, minutes=em)
            db.add(ScheduleEvent(
                tenant_id=tenant_id, resource_id=resources[res_idx].id,
                title=title, start_at=start, end_at=end,
                status="confirmed", source="schedule",
            ))
        db.commit()
        return

    if crm_type == "logistics":
        vehicles = [
            ("truck-01", "Mercedes Actros — TB-001-AA", 1, {"type": "truck"}),
            ("van-02", "Ford Transit — TB-002-BB", 1, {"type": "van"}),
        ]
        resources = []
        for i, (code, name, cap, meta) in enumerate(vehicles):
            r = ScheduleResource(tenant_id=tenant_id, resource_type="vehicle", code=code, name=name, capacity=cap, meta=meta, sort_order=i)
            db.add(r)
            resources.append(r)
        db.flush()
        trips = [
            (0, "Tbilisi → Batumi", 1, 8, 0, 18, 0),
            (1, "Tbilisi → Kutaisi", 2, 7, 0, 14, 0),
        ]
        for res_idx, title, day_off, h, m, eh, em in trips:
            start = today + timedelta(days=day_off, hours=h, minutes=m)
            end = today + timedelta(days=day_off, hours=eh, minutes=em)
            db.add(ScheduleEvent(
                tenant_id=tenant_id, resource_id=resources[res_idx].id,
                title=title, start_at=start, end_at=end,
                status="confirmed", source="dispatch",
            ))
        db.commit()
        return

    if crm_type == "construction":
        sites = [
            ("obj-1", "ЖК Vake Hills — корпус A", 1, {"city": "tbilisi"}),
            ("obj-2", "Склад Rustavi", 1, {"city": "rustavi"}),
        ]
        resources = []
        for i, (code, name, cap, meta) in enumerate(sites):
            r = ScheduleResource(tenant_id=tenant_id, resource_type="site", code=code, name=name, capacity=cap, meta=meta, sort_order=i)
            db.add(r)
            resources.append(r)
        db.flush()
        phases = [
            (0, "Фундамент — этап 2", 0, 5, 14),
            (1, "Монтаж каркаса", 3, 7, 21),
        ]
        for res_idx, title, start_off, duration in phases:
            start = today + timedelta(days=start_off)
            end = start + timedelta(days=duration)
            db.add(ScheduleEvent(
                tenant_id=tenant_id, resource_id=resources[res_idx].id,
                title=title, start_at=start, end_at=end, all_day=True,
                status="in_progress", source="project",
            ))
        db.commit()
        return

    # factory, services, agriculture, retail — generic sample
    generic_names = {
        "factory": [("line-1", "Линия сборки A"), ("line-2", "Линия упаковки")],
        "services": [("spec-1", "Consultant — Nika"), ("spec-2", "Designer — Eka")],
        "agriculture": [("field-1", "Виноградник Kakheti"), ("field-2", "Ферма фундука")],
        "retail": [("store-1", "Магазин Rustaveli"), ("store-2", "Склад outlet")],
    }
    names = generic_names.get(crm_type)
    if not names:
        return
    resources = []
    for i, (code, name) in enumerate(names):
        r = ScheduleResource(tenant_id=tenant_id, resource_type=rtype, code=code, name=name, capacity=1, sort_order=i)
        db.add(r)
        resources.append(r)
    db.flush()
    db.add(ScheduleEvent(
        tenant_id=tenant_id,
        resource_id=resources[0].id,
        title="Sample event",
        start_at=today + timedelta(days=2),
        end_at=today + timedelta(days=4),
        all_day=True,
        status="confirmed",
        source="demo",
    ))
    db.commit()
