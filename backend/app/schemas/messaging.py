from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MessageCreate(BaseModel):
    body: str


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_id: int
    direction: str
    body: str
    message_type: str
    external_id: str | None
    status: str
    created_at: datetime


class ConversationLinkUpdate(BaseModel):
    contact_id: int | None = None
    lead_id: int | None = None


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    channel: str
    external_id: str
    contact_name: str | None
    phone: str | None
    contact_id: int | None
    lead_id: int | None
    unread_count: int
    last_message_at: datetime | None
    last_message_preview: str | None
    created_at: datetime
    contact_name_linked: str | None = None
    lead_title: str | None = None
    company_name: str | None = None
    lead_status: str | None = None


class CrmSyncResult(BaseModel):
    conversations: int
    linked_contacts: int
    linked_leads: int
    created_leads: int
    message: str


class CallLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    channel: str
    external_id: str
    conversation_id: int | None
    direction: str
    status: str
    duration_seconds: int | None
    contact_name: str | None
    phone: str | None
    contact_id: int | None
    lead_id: int | None
    started_at: datetime


class MessagingSettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    whatsapp_phone_number_id: str | None
    whatsapp_verify_token: str | None
    messenger_page_id: str | None
    messenger_verify_token: str | None
    telegram_webhook_secret: str | None
    whatsapp_connected: bool
    messenger_connected: bool
    telegram_connected: bool
    whatsapp_configured: bool = False
    messenger_configured: bool = False
    telegram_configured: bool = False
    webhook_whatsapp_url: str | None = None
    webhook_messenger_url: str | None = None
    webhook_telegram_url: str | None = None


class MessagingSettingsUpdate(BaseModel):
    whatsapp_token: str | None = None
    whatsapp_phone_number_id: str | None = None
    whatsapp_verify_token: str | None = None
    messenger_page_token: str | None = None
    messenger_verify_token: str | None = None
    messenger_page_id: str | None = None
    telegram_bot_token: str | None = None
    telegram_webhook_secret: str | None = None


class SyncResult(BaseModel):
    channel: str
    success: bool
    message: str
