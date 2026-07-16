"""Движок чат-ботов: триггеры, автоответы, CRM-действия (AmoCRM/Bitrix стиль)."""

from __future__ import annotations

import asyncio
import json
import re
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.automation import BotAction, BotLog, BotTrigger, ChatBot
from app.models.crm import Deal, Lead
from app.models.messaging import Conversation, Message, MessagingSettings
from app.services import meta_messaging, telegram_messaging
from app.services.messaging_sync import ensure_lead_for_inbound, link_conversation


def _settings_dict(settings: MessagingSettings | None) -> dict | None:
    if not settings:
        return None
    return {
        "whatsapp_token": settings.whatsapp_token,
        "whatsapp_phone_number_id": settings.whatsapp_phone_number_id,
        "messenger_page_token": settings.messenger_page_token,
        "telegram_bot_token": settings.telegram_bot_token,
    }


def _bot_matches_channel(bot: ChatBot, channel: str) -> bool:
    if bot.channels in (None, "", "all"):
        return True
    allowed = {c.strip() for c in bot.channels.split(",") if c.strip()}
    return channel in allowed


def _is_first_inbound(db: Session, conversation_id: int) -> bool:
    count = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id, Message.direction == "inbound")
        .count()
    )
    return count <= 1


def _trigger_matches(trigger: BotTrigger, body: str, is_first: bool) -> bool:
    text = (body or "").strip().lower()
    ttype = trigger.trigger_type

    if ttype == "first_message":
        return is_first
    if ttype == "any_message":
        return bool(text)
    if ttype == "keyword":
        kw = (trigger.keyword or "").strip().lower()
        return bool(kw) and kw in text
    if ttype == "regex":
        pattern = trigger.keyword or ""
        if not pattern:
            return False
        try:
            return bool(re.search(pattern, body or "", re.IGNORECASE))
        except re.error:
            return False
    return False


def _parse_config(raw: str) -> dict:
    try:
        return json.loads(raw or "{}")
    except json.JSONDecodeError:
        return {}


async def _send_channel_message(conv: Conversation, body: str, settings_data: dict | None) -> str | None:
    if conv.channel == "whatsapp":
        result = await meta_messaging.send_whatsapp_text(conv.external_id, body, settings_data)
        return result.get("messages", [{}])[0].get("id")
    if conv.channel == "telegram":
        result = await telegram_messaging.send_telegram_text(conv.external_id, body, settings_data)
        return str(result.get("result", {}).get("message_id"))
    result = await meta_messaging.send_messenger_text(conv.external_id, body, settings_data)
    return result.get("message_id")


def _store_outbound(db: Session, conv: Conversation, body: str, ext_id: str | None = None) -> Message:
    message = Message(
        conversation_id=conv.id,
        direction="outbound",
        body=body,
        message_type="text",
        external_id=ext_id,
        status="sent" if ext_id else "mock",
    )
    db.add(message)
    conv.last_message_at = datetime.utcnow()
    conv.last_message_preview = body[:200]
    conv.updated_at = datetime.utcnow()
    return message


def _log(db: Session, *, bot_id: int | None, conversation_id: int, trigger_type: str | None,
         action_type: str | None, detail: str) -> None:
    db.add(BotLog(
        bot_id=bot_id,
        conversation_id=conversation_id,
        trigger_type=trigger_type,
        action_type=action_type,
        detail=detail,
    ))


def _execute_action(
    db: Session,
    *,
    bot: ChatBot,
    action: BotAction,
    conv: Conversation,
    trigger_type: str | None,
    settings_data: dict | None,
    outbound_messages: list[str],
) -> None:
    cfg = _parse_config(action.config)
    atype = action.action_type

    if atype == "send_message":
        text = cfg.get("text") or bot.welcome_message or ""
        if text:
            outbound_messages.append(text)
            _log(db, bot_id=bot.id, conversation_id=conv.id, trigger_type=trigger_type,
                 action_type=atype, detail=text[:500])

    elif atype == "create_lead":
        lead = ensure_lead_for_inbound(
            db,
            channel=conv.channel,
            phone=conv.phone,
            contact_name=conv.contact_name,
            external_id=conv.external_id,
        )
        if lead:
            conv.lead_id = lead.id
            title = cfg.get("title")
            if title:
                lead.title = title
            _log(db, bot_id=bot.id, conversation_id=conv.id, trigger_type=trigger_type,
                 action_type=atype, detail=f"Lead #{lead.id}")

    elif atype == "update_lead_status":
        if conv.lead_id:
            lead = db.query(Lead).filter(Lead.id == conv.lead_id).first()
            if lead and cfg.get("status"):
                lead.status = cfg["status"]
                lead.updated_at = datetime.utcnow()
                _log(db, bot_id=bot.id, conversation_id=conv.id, trigger_type=trigger_type,
                     action_type=atype, detail=f"status={cfg['status']}")

    elif atype == "create_deal":
        deal = Deal(
            title=cfg.get("title") or f"Сделка из {conv.channel}: {conv.contact_name or conv.external_id}",
            amount=float(cfg.get("amount") or 0),
            stage=cfg.get("stage") or "new",
            contact_id=conv.contact_id,
            lead_id=conv.lead_id,
        )
        db.add(deal)
        db.flush()
        _log(db, bot_id=bot.id, conversation_id=conv.id, trigger_type=trigger_type,
             action_type=atype, detail=f"Deal #{deal.id}")

    elif atype == "add_lead_comment":
        if conv.lead_id:
            lead = db.query(Lead).filter(Lead.id == conv.lead_id).first()
            if lead:
                note = cfg.get("text") or ""
                lead.comment = f"{lead.comment or ''}\n{note}".strip()
                lead.updated_at = datetime.utcnow()
                _log(db, bot_id=bot.id, conversation_id=conv.id, trigger_type=trigger_type,
                     action_type=atype, detail=note[:500])


def process_inbound_message(db: Session, conversation_id: int, message_body: str) -> int:
    """Запускает ботов для входящего сообщения. Возвращает число отправленных ответов."""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        return 0

    settings = db.query(MessagingSettings).first()
    settings_data = _settings_dict(settings)
    is_first = _is_first_inbound(db, conv.id)

    bots = (
        db.query(ChatBot)
        .filter(ChatBot.is_active.is_(True))
        .order_by(ChatBot.priority.desc(), ChatBot.id.asc())
        .all()
    )

    outbound_messages: list[str] = []
    matched_any = False

    for bot in bots:
        if not _bot_matches_channel(bot, conv.channel):
            continue

        matched_triggers: list[BotTrigger] = []
        for trigger in sorted(bot.triggers, key=lambda t: t.sort_order):
            if _trigger_matches(trigger, message_body, is_first):
                matched_triggers.append(trigger)

        if not matched_triggers and bot.triggers:
            continue

        if not bot.triggers and (is_first or message_body):
            matched_triggers = [None]  # type: ignore[list-item]

        if matched_triggers:
            matched_any = True
            trigger_ids = {t.id for t in matched_triggers if t is not None}
            trigger_type = matched_triggers[0].trigger_type if matched_triggers[0] else "default"

            actions = sorted(bot.actions, key=lambda a: a.sort_order)
            for action in actions:
                if action.trigger_id and action.trigger_id not in trigger_ids:
                    continue
                _execute_action(
                    db, bot=bot, action=action, conv=conv,
                    trigger_type=trigger_type, settings_data=settings_data,
                    outbound_messages=outbound_messages,
                )

            if bot.welcome_message and is_first and bot.welcome_message not in outbound_messages:
                has_send = any(a.action_type == "send_message" for a in actions)
                if not has_send:
                    outbound_messages.append(bot.welcome_message)

    if not matched_any:
        for bot in bots:
            if bot.fallback_message and _bot_matches_channel(bot, conv.channel):
                outbound_messages.append(bot.fallback_message)
                _log(db, bot_id=bot.id, conversation_id=conv.id, trigger_type="fallback",
                     action_type="send_message", detail=bot.fallback_message[:500])
                break

    link_conversation(db, conv, phone=conv.phone, contact_name=conv.contact_name)

    sent = 0
    unique_messages = []
    for msg in outbound_messages:
        if msg and msg not in unique_messages:
            unique_messages.append(msg)

    async def _send_all():
        nonlocal sent
        for text in unique_messages:
            try:
                ext_id = await _send_channel_message(conv, text, settings_data)
                _store_outbound(db, conv, text, ext_id)
                sent += 1
            except (meta_messaging.MetaMessagingError, telegram_messaging.TelegramError) as e:
                _store_outbound(db, conv, text, None)
                _log(db, bot_id=None, conversation_id=conv.id, trigger_type="error",
                     action_type="send_message", detail=str(e))
                sent += 1

    if unique_messages:
        try:
            asyncio.run(_send_all())
        except RuntimeError:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(_send_all())
            loop.close()

    db.commit()
    return sent
