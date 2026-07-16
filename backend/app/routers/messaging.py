from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps.tenant import TenantCtx, get_tenant_ctx, scoped
from app.models.crm import Contact, Lead
from app.models.messaging import CallLog, Conversation, Message, MessagingSettings
from app.models.tenant import Tenant
from app.schemas.messaging import (
    CallLogResponse,
    ConversationLinkUpdate,
    ConversationResponse,
    CrmSyncResult,
    MessageCreate,
    MessageResponse,
    MessagingSettingsResponse,
    MessagingSettingsUpdate,
    SyncResult,
)
from app.services import meta_messaging, telegram_messaging
from app.services.messaging_sync import (
    convert_conversation_to_contact,
    get_company_name,
    link_conversation,
    sync_all,
    sync_conversation,
)

router = APIRouter(prefix="/messaging", tags=["Messaging"])


def _settings_dict(settings: MessagingSettings | None) -> dict | None:
    if not settings:
        return None
    return {
        "whatsapp_token": settings.whatsapp_token,
        "whatsapp_phone_number_id": settings.whatsapp_phone_number_id,
        "messenger_page_token": settings.messenger_page_token,
        "telegram_bot_token": settings.telegram_bot_token,
    }


def _resolve_tenant(db: Session, tenant_slug: str) -> Tenant:
    tenant = db.query(Tenant).filter(Tenant.slug == tenant_slug).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Компания не найдена")
    return tenant


def _get_or_create_settings(db: Session, tenant_id: int) -> MessagingSettings:
    settings = (
        db.query(MessagingSettings)
        .filter(MessagingSettings.tenant_id == tenant_id)
        .first()
    )
    if not settings:
        settings = MessagingSettings(tenant_id=tenant_id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


def _tenant_slug(db: Session, tenant_id: int) -> str:
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    return tenant.slug if tenant else "demo"


def _conversation_response(db: Session, conv: Conversation) -> ConversationResponse:
    contact_name_linked = None
    lead_title = None
    lead_status = None
    tenant_id = conv.tenant_id
    company_name = get_company_name(db, conv.contact_id, tenant_id)
    if conv.contact_id:
        contact = (
            db.query(Contact)
            .filter(Contact.id == conv.contact_id, Contact.tenant_id == tenant_id)
            .first()
        )
        contact_name_linked = contact.name if contact else None
    if conv.lead_id:
        lead = (
            db.query(Lead)
            .filter(Lead.id == conv.lead_id, Lead.tenant_id == tenant_id)
            .first()
        )
        if lead:
            lead_title = lead.title
            lead_status = lead.status
    return ConversationResponse(
        id=conv.id,
        channel=conv.channel,
        external_id=conv.external_id,
        contact_name=conv.contact_name,
        phone=conv.phone,
        contact_id=conv.contact_id,
        lead_id=conv.lead_id,
        unread_count=conv.unread_count,
        last_message_at=conv.last_message_at,
        last_message_preview=conv.last_message_preview,
        created_at=conv.created_at,
        contact_name_linked=contact_name_linked,
        lead_title=lead_title,
        company_name=company_name,
        lead_status=lead_status,
    )


def _get_or_create_conversation(
    db: Session,
    tenant_id: int,
    *,
    channel: str,
    external_id: str,
    contact_name: str | None = None,
    phone: str | None = None,
) -> Conversation:
    conv = (
        db.query(Conversation)
        .filter(
            Conversation.tenant_id == tenant_id,
            Conversation.channel == channel,
            Conversation.external_id == external_id,
        )
        .first()
    )
    if conv:
        if contact_name and not conv.contact_name:
            conv.contact_name = contact_name
        if phone and not conv.phone:
            conv.phone = phone
        link_conversation(db, conv, phone=phone, contact_name=contact_name)
        return conv

    conv = Conversation(
        tenant_id=tenant_id,
        channel=channel,
        external_id=external_id,
        contact_name=contact_name,
        phone=phone,
    )
    db.add(conv)
    db.flush()
    link_conversation(db, conv, phone=phone, contact_name=contact_name, auto_create_lead=True)
    return conv


def _store_inbound_message(db: Session, tenant_id: int, event: dict) -> Message | None:
    external_msg_id = event.get("message_external_id")
    if external_msg_id:
        existing = (
            db.query(Message)
            .filter(Message.tenant_id == tenant_id, Message.external_id == external_msg_id)
            .first()
        )
        if existing:
            return None

    conv = _get_or_create_conversation(
        db,
        tenant_id,
        channel=event["channel"],
        external_id=event["external_id"],
        contact_name=event.get("contact_name"),
        phone=event.get("phone"),
    )

    message = Message(
        tenant_id=tenant_id,
        conversation_id=conv.id,
        direction="inbound",
        body=event.get("body", ""),
        message_type=event.get("message_type", "text"),
        external_id=external_msg_id,
        status="received",
    )
    db.add(message)

    preview = (event.get("body") or "")[:200]
    conv.unread_count += 1
    conv.last_message_at = datetime.utcnow()
    conv.last_message_preview = preview
    conv.updated_at = datetime.utcnow()
    return message


def _store_call(db: Session, tenant_id: int, event: dict) -> CallLog:
    conv = None
    if event.get("external_id"):
        conv = _get_or_create_conversation(
            db,
            tenant_id,
            channel=event["channel"],
            external_id=event["external_id"],
            phone=event.get("phone"),
        )

    call = CallLog(
        tenant_id=tenant_id,
        channel=event["channel"],
        external_id=event.get("external_id", ""),
        conversation_id=conv.id if conv else None,
        direction=event.get("direction", "inbound"),
        status=event.get("status", "ringing"),
        duration_seconds=event.get("duration_seconds"),
        contact_name=conv.contact_name if conv else None,
        phone=event.get("phone") or (conv.phone if conv else None),
        contact_id=conv.contact_id if conv else None,
        lead_id=conv.lead_id if conv else None,
    )
    db.add(call)

    if conv:
        call_msg = Message(
            tenant_id=tenant_id,
            conversation_id=conv.id,
            direction="inbound",
            body=f"📞 Входящий звонок ({event.get('status', 'ringing')})",
            message_type="call",
            status=event.get("status", "ringing"),
        )
        db.add(call_msg)
        conv.unread_count += 1
        conv.last_message_at = datetime.utcnow()
        conv.last_message_preview = "📞 Входящий звонок"
        conv.updated_at = datetime.utcnow()

    return call


def _process_events(db: Session, events: list[dict], tenant_id: int) -> dict:
    from app.services.bot_engine import process_inbound_message

    stored_messages = 0
    stored_calls = 0
    bot_queue: list[tuple[int, str]] = []
    for event in events:
        if event["kind"] == "message":
            msg = _store_inbound_message(db, tenant_id, event)
            if msg:
                stored_messages += 1
                bot_queue.append((msg.conversation_id, event.get("body", "")))
        elif event["kind"] == "call":
            _store_call(db, tenant_id, event)
            stored_calls += 1
        elif event["kind"] == "status":
            ext_id = event.get("message_external_id")
            if ext_id:
                msg = (
                    db.query(Message)
                    .filter(Message.tenant_id == tenant_id, Message.external_id == ext_id)
                    .first()
                )
                if msg:
                    msg.status = event.get("status", msg.status)
    db.commit()
    for conv_id, body in bot_queue:
        try:
            process_inbound_message(db, conv_id, body)
        except Exception:
            pass
    return {"stored_messages": stored_messages, "stored_calls": stored_calls}


@router.get("/webhooks/{tenant_slug}/whatsapp")
def whatsapp_webhook_verify(
    tenant_slug: str,
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    db: Session = Depends(get_db),
):
    tenant = _resolve_tenant(db, tenant_slug)
    settings = _get_or_create_settings(db, tenant.id)
    expected = (
        settings.whatsapp_verify_token
        or __import__("os").getenv("WHATSAPP_VERIFY_TOKEN", "kinetix-verify")
    )
    if hub_mode == "subscribe" and hub_verify_token == expected:
        return Response(content=hub_challenge or "", media_type="text/plain")
    raise HTTPException(status_code=403, detail="Неверный verify token")


@router.post("/webhooks/{tenant_slug}/whatsapp")
async def whatsapp_webhook_receive(
    tenant_slug: str,
    request: Request,
    db: Session = Depends(get_db),
):
    tenant = _resolve_tenant(db, tenant_slug)
    payload = await request.json()
    events = meta_messaging.parse_whatsapp_webhook(payload)
    return _process_events(db, events, tenant.id)


@router.get("/webhooks/{tenant_slug}/messenger")
def messenger_webhook_verify(
    tenant_slug: str,
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    db: Session = Depends(get_db),
):
    tenant = _resolve_tenant(db, tenant_slug)
    settings = _get_or_create_settings(db, tenant.id)
    expected = (
        settings.messenger_verify_token
        or __import__("os").getenv("MESSENGER_VERIFY_TOKEN", "kinetix-verify")
    )
    if hub_mode == "subscribe" and hub_verify_token == expected:
        return Response(content=hub_challenge or "", media_type="text/plain")
    raise HTTPException(status_code=403, detail="Неверный verify token")


@router.post("/webhooks/{tenant_slug}/messenger")
async def messenger_webhook_receive(
    tenant_slug: str,
    request: Request,
    db: Session = Depends(get_db),
):
    tenant = _resolve_tenant(db, tenant_slug)
    payload = await request.json()
    events = meta_messaging.parse_messenger_webhook(payload)
    return _process_events(db, events, tenant.id)


@router.post("/webhooks/{tenant_slug}/telegram")
async def telegram_webhook_receive(
    tenant_slug: str,
    request: Request,
    db: Session = Depends(get_db),
    x_telegram_bot_api_secret_token: str | None = Header(None),
):
    tenant = _resolve_tenant(db, tenant_slug)
    settings = _get_or_create_settings(db, tenant.id)
    expected_secret = settings.telegram_webhook_secret or __import__("os").getenv("TELEGRAM_WEBHOOK_SECRET")
    if expected_secret and x_telegram_bot_api_secret_token != expected_secret:
        raise HTTPException(status_code=403, detail="Неверный secret token")

    payload = await request.json()
    events = telegram_messaging.parse_telegram_webhook(payload)
    return _process_events(db, events, tenant.id)


@router.get("/conversations", response_model=list[ConversationResponse])
def list_conversations(
    channel: str | None = None,
    contact_id: int | None = None,
    lead_id: int | None = None,
    ctx: TenantCtx = Depends(get_tenant_ctx),
):
    q = scoped(ctx, Conversation).order_by(Conversation.last_message_at.desc().nullslast())
    if channel:
        q = q.filter(Conversation.channel == channel)
    if contact_id:
        q = q.filter(Conversation.contact_id == contact_id)
    if lead_id:
        q = q.filter(Conversation.lead_id == lead_id)
    return [_conversation_response(ctx.db, c) for c in q.all()]


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id: int, ctx: TenantCtx = Depends(get_tenant_ctx)):
    conv = scoped(ctx, Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Диалог не найден")
    return _conversation_response(ctx.db, conv)


@router.patch("/conversations/{conversation_id}/link", response_model=ConversationResponse)
def link_conversation_manual(
    conversation_id: int,
    data: ConversationLinkUpdate,
    ctx: TenantCtx = Depends(get_tenant_ctx),
):
    conv = scoped(ctx, Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Диалог не найден")

    if data.contact_id is not None:
        contact = scoped(ctx, Contact).filter(Contact.id == data.contact_id).first()
        if not contact:
            raise HTTPException(status_code=404, detail="Контакт не найден")
        conv.contact_id = contact.id
        if not conv.contact_name:
            conv.contact_name = contact.name
        if not conv.phone and contact.phone:
            conv.phone = contact.phone

    if data.lead_id is not None:
        lead = scoped(ctx, Lead).filter(Lead.id == data.lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Лид не найден")
        conv.lead_id = lead.id
        if not conv.phone and lead.phone:
            conv.phone = lead.phone

    sync_conversation(ctx.db, conv)
    ctx.db.commit()
    ctx.db.refresh(conv)
    return _conversation_response(ctx.db, conv)


@router.post("/conversations/{conversation_id}/convert-contact", response_model=ConversationResponse)
def convert_to_contact(conversation_id: int, ctx: TenantCtx = Depends(get_tenant_ctx)):
    conv = scoped(ctx, Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Диалог не найден")
    convert_conversation_to_contact(ctx.db, conv)
    ctx.db.commit()
    ctx.db.refresh(conv)
    return _conversation_response(ctx.db, conv)


@router.post("/sync-crm", response_model=CrmSyncResult)
def sync_crm(ctx: TenantCtx = Depends(get_tenant_ctx)):
    stats = sync_all(ctx.db, ctx.tenant_id)
    ctx.db.commit()
    return CrmSyncResult(
        **stats,
        message=(
            f"Синхронизировано {stats['conversations']} диалогов: "
            f"{stats['linked_contacts']} с контактами, {stats['linked_leads']} с лидами"
        ),
    )


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageResponse])
def list_messages(conversation_id: int, ctx: TenantCtx = Depends(get_tenant_ctx)):
    conv = scoped(ctx, Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Диалог не найден")
    return (
        ctx.db.query(Message)
        .filter(Message.conversation_id == conversation_id, Message.tenant_id == ctx.tenant_id)
        .order_by(Message.created_at.asc())
        .all()
    )


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse, status_code=201)
async def send_message(
    conversation_id: int,
    data: MessageCreate,
    ctx: TenantCtx = Depends(get_tenant_ctx),
):
    conv = scoped(ctx, Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Диалог не найден")

    settings = _get_or_create_settings(ctx.db, ctx.tenant_id)
    settings_data = _settings_dict(settings)

    try:
        if conv.channel == "whatsapp":
            result = await meta_messaging.send_whatsapp_text(
                conv.external_id, data.body, settings_data
            )
            ext_id = result.get("messages", [{}])[0].get("id")
        elif conv.channel == "telegram":
            result = await telegram_messaging.send_telegram_text(
                conv.external_id, data.body, settings_data
            )
            ext_id = str(result.get("result", {}).get("message_id"))
        else:
            result = await meta_messaging.send_messenger_text(
                conv.external_id, data.body, settings_data
            )
            ext_id = result.get("message_id")
    except (meta_messaging.MetaMessagingError, telegram_messaging.TelegramError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    message = Message(
        tenant_id=ctx.tenant_id,
        conversation_id=conv.id,
        direction="outbound",
        body=data.body,
        message_type="text",
        external_id=ext_id,
        status="sent",
    )
    ctx.db.add(message)
    conv.last_message_at = datetime.utcnow()
    conv.last_message_preview = data.body[:200]
    conv.updated_at = datetime.utcnow()
    ctx.db.commit()
    ctx.db.refresh(message)
    return message


@router.patch("/conversations/{conversation_id}/read", response_model=ConversationResponse)
def mark_conversation_read(conversation_id: int, ctx: TenantCtx = Depends(get_tenant_ctx)):
    conv = scoped(ctx, Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Диалог не найден")
    conv.unread_count = 0
    ctx.db.commit()
    ctx.db.refresh(conv)
    return _conversation_response(ctx.db, conv)


@router.get("/calls", response_model=list[CallLogResponse])
def list_calls(channel: str | None = None, ctx: TenantCtx = Depends(get_tenant_ctx)):
    q = scoped(ctx, CallLog).order_by(CallLog.started_at.desc())
    if channel:
        q = q.filter(CallLog.channel == channel)
    return q.limit(100).all()


def _build_settings_response(
    request: Request, db: Session, settings: MessagingSettings, tenant_id: int
) -> MessagingSettingsResponse:
    base_url = str(request.base_url).rstrip("/")
    slug = _tenant_slug(db, tenant_id)
    webhook_base = f"{base_url}/api/messaging/webhooks/{slug}"
    return MessagingSettingsResponse(
        id=settings.id,
        whatsapp_phone_number_id=settings.whatsapp_phone_number_id,
        whatsapp_verify_token=settings.whatsapp_verify_token,
        messenger_page_id=settings.messenger_page_id,
        messenger_verify_token=settings.messenger_verify_token,
        telegram_webhook_secret=getattr(settings, "telegram_webhook_secret", None),
        whatsapp_connected=settings.whatsapp_connected,
        messenger_connected=settings.messenger_connected,
        telegram_connected=getattr(settings, "telegram_connected", False),
        whatsapp_configured=bool(
            settings.whatsapp_token or settings.whatsapp_phone_number_id
            or __import__("os").getenv("WHATSAPP_TOKEN")
        ),
        messenger_configured=bool(
            settings.messenger_page_token or __import__("os").getenv("MESSENGER_PAGE_TOKEN")
        ),
        telegram_configured=bool(
            getattr(settings, "telegram_bot_token", None) or __import__("os").getenv("TELEGRAM_BOT_TOKEN")
        ),
        webhook_whatsapp_url=f"{webhook_base}/whatsapp",
        webhook_messenger_url=f"{webhook_base}/messenger",
        webhook_telegram_url=f"{webhook_base}/telegram",
    )


@router.get("/settings", response_model=MessagingSettingsResponse)
def get_messaging_settings(request: Request, ctx: TenantCtx = Depends(get_tenant_ctx)):
    settings = _get_or_create_settings(ctx.db, ctx.tenant_id)
    return _build_settings_response(request, ctx.db, settings, ctx.tenant_id)


@router.post("/settings", response_model=MessagingSettingsResponse)
def save_messaging_settings(
    data: MessagingSettingsUpdate,
    request: Request,
    ctx: TenantCtx = Depends(get_tenant_ctx),
):
    settings = _get_or_create_settings(ctx.db, ctx.tenant_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(settings, key, value)
    settings.whatsapp_connected = bool(
        settings.whatsapp_token and settings.whatsapp_phone_number_id
    )
    settings.messenger_connected = bool(
        settings.messenger_page_token and settings.messenger_page_id
    )
    settings.telegram_connected = bool(getattr(settings, "telegram_bot_token", None))
    settings.updated_at = datetime.utcnow()
    ctx.db.commit()
    ctx.db.refresh(settings)
    return _build_settings_response(request, ctx.db, settings, ctx.tenant_id)


@router.post("/sync/{channel}", response_model=SyncResult)
async def sync_channel(channel: str, request: Request, ctx: TenantCtx = Depends(get_tenant_ctx)):
    settings = _get_or_create_settings(ctx.db, ctx.tenant_id)
    settings_data = _settings_dict(settings)
    base_url = str(request.base_url).rstrip("/")
    slug = _tenant_slug(ctx.db, ctx.tenant_id)
    webhook_base = f"{base_url}/api/messaging/webhooks/{slug}"

    if channel == "whatsapp":
        if not (settings.whatsapp_token or __import__("os").getenv("WHATSAPP_TOKEN")):
            return SyncResult(channel=channel, success=False, message="Укажите WhatsApp Access Token и Phone Number ID")
        if not settings.whatsapp_phone_number_id:
            return SyncResult(channel=channel, success=False, message="Укажите Phone Number ID")
        settings.whatsapp_connected = True
        ctx.db.commit()
        return SyncResult(
            channel=channel,
            success=True,
            message=f"Webhook URL для Meta: {webhook_base}/whatsapp",
        )

    if channel == "messenger":
        if not (settings.messenger_page_token or __import__("os").getenv("MESSENGER_PAGE_TOKEN")):
            return SyncResult(channel=channel, success=False, message="Укажите Page Access Token")
        if not settings.messenger_page_id:
            return SyncResult(channel=channel, success=False, message="Укажите Page ID")
        settings.messenger_connected = True
        ctx.db.commit()
        return SyncResult(
            channel=channel,
            success=True,
            message=f"Webhook URL для Meta: {webhook_base}/messenger",
        )

    if channel == "telegram":
        token = settings_data.get("telegram_bot_token") if settings_data else None
        if not token:
            return SyncResult(channel=channel, success=False, message="Укажите Telegram Bot Token")
        try:
            await telegram_messaging.setup_webhook(
                f"{webhook_base}/telegram",
                settings_data,
                settings.telegram_webhook_secret,
            )
            settings.telegram_connected = True
            ctx.db.commit()
            return SyncResult(channel=channel, success=True, message="Telegram webhook установлен")
        except telegram_messaging.TelegramError as e:
            return SyncResult(channel=channel, success=False, message=str(e))

    raise HTTPException(status_code=404, detail="Неизвестный канал")
