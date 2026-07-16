from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ResourceBase(BaseModel):
    resource_type: str
    name: str
    code: str
    capacity: int = 1
    floor: int | None = None
    meta: dict | None = None
    sort_order: int = 0
    is_active: bool = True


class ResourceCreate(ResourceBase):
    pass


class ResourceUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    capacity: int | None = None
    floor: int | None = None
    meta: dict | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class ResourceResponse(ResourceBase):
    id: int
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class EventBase(BaseModel):
    resource_id: int | None = None
    title: str
    guest_name: str | None = None
    phone: str | None = None
    email: str | None = None
    start_at: datetime
    end_at: datetime
    all_day: bool = False
    status: str = "confirmed"
    source: str | None = None
    notes: str | None = None
    custom_data: dict | None = None
    lead_id: int | None = None
    deal_id: int | None = None
    contact_id: int | None = None


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    resource_id: int | None = None
    title: str | None = None
    guest_name: str | None = None
    phone: str | None = None
    email: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    all_day: bool | None = None
    status: str | None = None
    source: str | None = None
    notes: str | None = None
    custom_data: dict | None = None


class EventResponse(EventBase):
    id: int
    external_uid: str | None = None
    resource_name: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class GridResponse(BaseModel):
    from_date: str
    to_date: str
    resource_type: str
    resources: list[ResourceResponse]
    events: list[EventResponse]


class ICalFeedBase(BaseModel):
    name: str
    url: str = Field(min_length=8, max_length=1000)
    resource_id: int | None = None
    is_active: bool = True


class ICalFeedCreate(ICalFeedBase):
    pass


class ICalFeedUpdate(BaseModel):
    name: str | None = None
    url: str | None = None
    resource_id: int | None = None
    is_active: bool | None = None


class ICalFeedResponse(ICalFeedBase):
    id: int
    last_synced_at: datetime | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ICalSyncResult(BaseModel):
    feed_id: int
    imported: int
    updated: int
    skipped: int
