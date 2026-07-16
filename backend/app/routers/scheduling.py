from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.core.schedule_industry import resource_type_for
from app.deps.tenant import TenantCtx, get_tenant_ctx, scoped
from app.models.scheduling import ICalFeed, ScheduleEvent, ScheduleResource
from app.schemas.scheduling import (
    EventCreate,
    EventResponse,
    EventUpdate,
    GridResponse,
    ICalFeedCreate,
    ICalFeedResponse,
    ICalFeedUpdate,
    ICalSyncResult,
    ResourceCreate,
    ResourceResponse,
    ResourceUpdate,
)
from app.services.ical_sync import export_ics, sync_feed

router = APIRouter(prefix="/scheduling", tags=["Расписание"])


def _resource_response(r: ScheduleResource) -> ResourceResponse:
    return ResourceResponse.model_validate(r)


def _event_response(ev: ScheduleEvent, resource_name: str | None = None) -> EventResponse:
    return EventResponse(
        id=ev.id,
        resource_id=ev.resource_id,
        title=ev.title,
        guest_name=ev.guest_name,
        phone=ev.phone,
        email=ev.email,
        start_at=ev.start_at,
        end_at=ev.end_at,
        all_day=ev.all_day,
        status=ev.status,
        source=ev.source,
        external_uid=ev.external_uid,
        notes=ev.notes,
        custom_data=ev.custom_data,
        lead_id=ev.lead_id,
        deal_id=ev.deal_id,
        contact_id=ev.contact_id,
        resource_name=resource_name,
        created_at=ev.created_at,
        updated_at=ev.updated_at,
    )


def _resource_map(ctx: TenantCtx) -> dict[int, str]:
    rows = scoped(ctx, ScheduleResource).all()
    return {r.id: r.name for r in rows}


def _default_resource_type(ctx: TenantCtx) -> str:
    return resource_type_for(ctx.tenant.crm_type or "general")


def _parse_range(from_date: str, to_date: str) -> tuple[datetime, datetime]:
    try:
        start = datetime.combine(date.fromisoformat(from_date), datetime.min.time())
        end = datetime.combine(date.fromisoformat(to_date), datetime.max.time())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Некорректный формат даты (YYYY-MM-DD)") from exc
    if end < start:
        raise HTTPException(status_code=400, detail="to_date должна быть позже from_date")
    return start, end


def _overlap_filter(q, start: datetime, end: datetime):
    return q.filter(ScheduleEvent.start_at <= end, ScheduleEvent.end_at >= start)


@router.get("/resources", response_model=list[ResourceResponse])
def list_resources(
    resource_type: str | None = None,
    ctx: TenantCtx = Depends(get_tenant_ctx),
):
    q = scoped(ctx, ScheduleResource).filter(ScheduleResource.is_active.is_(True))
    rtype = resource_type or _default_resource_type(ctx)
    q = q.filter(ScheduleResource.resource_type == rtype)
    return [_resource_response(r) for r in q.order_by(ScheduleResource.sort_order, ScheduleResource.code).all()]


@router.post("/resources", response_model=ResourceResponse, status_code=201)
def create_resource(data: ResourceCreate, ctx: TenantCtx = Depends(get_tenant_ctx)):
    existing = (
        scoped(ctx, ScheduleResource)
        .filter(ScheduleResource.resource_type == data.resource_type, ScheduleResource.code == data.code)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Ресурс с таким кодом уже существует")
    resource = ScheduleResource(tenant_id=ctx.tenant_id, **data.model_dump())
    ctx.db.add(resource)
    ctx.db.commit()
    ctx.db.refresh(resource)
    return _resource_response(resource)


@router.patch("/resources/{resource_id}", response_model=ResourceResponse)
def update_resource(resource_id: int, data: ResourceUpdate, ctx: TenantCtx = Depends(get_tenant_ctx)):
    resource = scoped(ctx, ScheduleResource).filter(ScheduleResource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Ресурс не найден")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(resource, key, val)
    ctx.db.commit()
    ctx.db.refresh(resource)
    return _resource_response(resource)


@router.delete("/resources/{resource_id}", status_code=204)
def delete_resource(resource_id: int, ctx: TenantCtx = Depends(get_tenant_ctx)):
    resource = scoped(ctx, ScheduleResource).filter(ScheduleResource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Ресурс не найден")
    ctx.db.delete(resource)
    ctx.db.commit()


@router.get("/events", response_model=list[EventResponse])
def list_events(
    from_date: str = Query(..., alias="from"),
    to_date: str = Query(..., alias="to"),
    resource_type: str | None = None,
    resource_id: int | None = None,
    ctx: TenantCtx = Depends(get_tenant_ctx),
):
    start, end = _parse_range(from_date, to_date)
    rmap = _resource_map(ctx)
    rtype = resource_type or _default_resource_type(ctx)

    q = _overlap_filter(scoped(ctx, ScheduleEvent), start, end)
    if resource_id:
        q = q.filter(ScheduleEvent.resource_id == resource_id)
    else:
        resource_ids = [
            r.id for r in scoped(ctx, ScheduleResource)
            .filter(ScheduleResource.resource_type == rtype, ScheduleResource.is_active.is_(True))
            .all()
        ]
        q = q.filter(ScheduleEvent.resource_id.in_(resource_ids) if resource_ids else False)

    events = q.order_by(ScheduleEvent.start_at).all()
    return [_event_response(ev, rmap.get(ev.resource_id or 0)) for ev in events]


@router.post("/events", response_model=EventResponse, status_code=201)
def create_event(data: EventCreate, ctx: TenantCtx = Depends(get_tenant_ctx)):
    if data.end_at <= data.start_at:
        raise HTTPException(status_code=400, detail="Дата окончания должна быть позже начала")
    if data.resource_id:
        resource = scoped(ctx, ScheduleResource).filter(ScheduleResource.id == data.resource_id).first()
        if not resource:
            raise HTTPException(status_code=404, detail="Ресурс не найден")
    event = ScheduleEvent(tenant_id=ctx.tenant_id, **data.model_dump())
    ctx.db.add(event)
    ctx.db.commit()
    ctx.db.refresh(event)
    rmap = _resource_map(ctx)
    return _event_response(event, rmap.get(event.resource_id or 0))


@router.patch("/events/{event_id}", response_model=EventResponse)
def update_event(event_id: int, data: EventUpdate, ctx: TenantCtx = Depends(get_tenant_ctx)):
    event = scoped(ctx, ScheduleEvent).filter(ScheduleEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(event, key, val)
    if event.end_at <= event.start_at:
        raise HTTPException(status_code=400, detail="Дата окончания должна быть позже начала")
    event.updated_at = datetime.utcnow()
    ctx.db.commit()
    ctx.db.refresh(event)
    rmap = _resource_map(ctx)
    return _event_response(event, rmap.get(event.resource_id or 0))


@router.delete("/events/{event_id}", status_code=204)
def delete_event(event_id: int, ctx: TenantCtx = Depends(get_tenant_ctx)):
    event = scoped(ctx, ScheduleEvent).filter(ScheduleEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    ctx.db.delete(event)
    ctx.db.commit()


@router.get("/grid", response_model=GridResponse)
def room_grid(
    from_date: str = Query(..., alias="from"),
    to_date: str = Query(..., alias="to"),
    resource_type: str | None = None,
    ctx: TenantCtx = Depends(get_tenant_ctx),
):
    start, end = _parse_range(from_date, to_date)
    rtype = resource_type or _default_resource_type(ctx)
    resources = (
        scoped(ctx, ScheduleResource)
        .filter(ScheduleResource.resource_type == rtype, ScheduleResource.is_active.is_(True))
        .order_by(ScheduleResource.sort_order, ScheduleResource.code)
        .all()
    )
    rmap = {r.id: r.name for r in resources}
    resource_ids = [r.id for r in resources]
    q = _overlap_filter(scoped(ctx, ScheduleEvent), start, end)
    if resource_ids:
        q = q.filter(ScheduleEvent.resource_id.in_(resource_ids))
    else:
        q = q.filter(False)
    events = q.order_by(ScheduleEvent.start_at).all()
    return GridResponse(
        from_date=from_date,
        to_date=to_date,
        resource_type=rtype,
        resources=[_resource_response(r) for r in resources],
        events=[_event_response(ev, rmap.get(ev.resource_id or 0)) for ev in events],
    )


@router.get("/ical/export.ics")
def export_ical(
    resource_id: int | None = None,
    ctx: TenantCtx = Depends(get_tenant_ctx),
):
    content = export_ics(ctx.db, ctx.tenant_id, resource_id=resource_id)
    filename = "schedule.ics" if not resource_id else f"room-{resource_id}.ics"
    return Response(
        content=content,
        media_type="text/calendar; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/ical/feeds", response_model=list[ICalFeedResponse])
def list_ical_feeds(ctx: TenantCtx = Depends(get_tenant_ctx)):
    feeds = scoped(ctx, ICalFeed).order_by(ICalFeed.name).all()
    return [ICalFeedResponse.model_validate(f) for f in feeds]


@router.post("/ical/feeds", response_model=ICalFeedResponse, status_code=201)
def create_ical_feed(data: ICalFeedCreate, ctx: TenantCtx = Depends(get_tenant_ctx)):
    if data.resource_id:
        resource = scoped(ctx, ScheduleResource).filter(ScheduleResource.id == data.resource_id).first()
        if not resource:
            raise HTTPException(status_code=404, detail="Ресурс не найден")
    feed = ICalFeed(tenant_id=ctx.tenant_id, **data.model_dump())
    ctx.db.add(feed)
    ctx.db.commit()
    ctx.db.refresh(feed)
    return ICalFeedResponse.model_validate(feed)


@router.patch("/ical/feeds/{feed_id}", response_model=ICalFeedResponse)
def update_ical_feed(feed_id: int, data: ICalFeedUpdate, ctx: TenantCtx = Depends(get_tenant_ctx)):
    feed = scoped(ctx, ICalFeed).filter(ICalFeed.id == feed_id).first()
    if not feed:
        raise HTTPException(status_code=404, detail="Календарь не найден")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(feed, key, val)
    ctx.db.commit()
    ctx.db.refresh(feed)
    return ICalFeedResponse.model_validate(feed)


@router.delete("/ical/feeds/{feed_id}", status_code=204)
def delete_ical_feed(feed_id: int, ctx: TenantCtx = Depends(get_tenant_ctx)):
    feed = scoped(ctx, ICalFeed).filter(ICalFeed.id == feed_id).first()
    if not feed:
        raise HTTPException(status_code=404, detail="Календарь не найден")
    ctx.db.delete(feed)
    ctx.db.commit()


@router.post("/ical/feeds/{feed_id}/sync", response_model=ICalSyncResult)
def sync_ical_feed(feed_id: int, ctx: TenantCtx = Depends(get_tenant_ctx)):
    feed = scoped(ctx, ICalFeed).filter(ICalFeed.id == feed_id).first()
    if not feed:
        raise HTTPException(status_code=404, detail="Календарь не найден")
    try:
        result = sync_feed(ctx.db, feed)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ICalSyncResult(feed_id=feed_id, **result)


@router.post("/ical/sync-all")
def sync_all_feeds(ctx: TenantCtx = Depends(get_tenant_ctx)):
    feeds = scoped(ctx, ICalFeed).filter(ICalFeed.is_active.is_(True)).all()
    results = []
    for feed in feeds:
        try:
            result = sync_feed(ctx.db, feed)
            results.append({"feed_id": feed.id, "name": feed.name, "ok": True, **result})
        except ValueError as exc:
            results.append({"feed_id": feed.id, "name": feed.name, "ok": False, "error": str(exc)})
    return {"results": results}
