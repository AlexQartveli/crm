"""Интеграция WhatsApp Cloud API и Facebook Messenger (Meta)."""

import os
from typing import Any

import httpx

GRAPH_API = os.getenv("META_GRAPH_API", "https://graph.facebook.com/v21.0")
MOCK_MODE = os.getenv("MESSAGING_MOCK", "true").lower() == "true"


class MetaMessagingError(Exception):
    pass


def _get_whatsapp_token(db_settings: dict | None = None) -> str | None:
    if db_settings and db_settings.get("whatsapp_token"):
        return db_settings["whatsapp_token"]
    return os.getenv("WHATSAPP_TOKEN")


def _get_whatsapp_phone_id(db_settings: dict | None = None) -> str | None:
    if db_settings and db_settings.get("whatsapp_phone_number_id"):
        return db_settings["whatsapp_phone_number_id"]
    return os.getenv("WHATSAPP_PHONE_NUMBER_ID")


def _get_messenger_token(db_settings: dict | None = None) -> str | None:
    if db_settings and db_settings.get("messenger_page_token"):
        return db_settings["messenger_page_token"]
    return os.getenv("MESSENGER_PAGE_TOKEN")


async def send_whatsapp_text(
    to: str,
    body: str,
    db_settings: dict | None = None,
) -> dict:
    if MOCK_MODE:
        return {"messages": [{"id": f"mock-wa-{to}"}]}

    token = _get_whatsapp_token(db_settings)
    phone_id = _get_whatsapp_phone_id(db_settings)
    if not token or not phone_id:
        raise MetaMessagingError("WhatsApp не настроен: укажите WHATSAPP_TOKEN и WHATSAPP_PHONE_NUMBER_ID")

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body},
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{GRAPH_API}/{phone_id}/messages",
            headers={"Authorization": f"Bearer {token}"},
            json=payload,
        )
        if resp.status_code >= 400:
            raise MetaMessagingError(f"WhatsApp API: {resp.text}")
        return resp.json()


async def send_messenger_text(
    recipient_id: str,
    body: str,
    db_settings: dict | None = None,
) -> dict:
    if MOCK_MODE:
        return {"message_id": f"mock-msg-{recipient_id}"}

    token = _get_messenger_token(db_settings)
    if not token:
        raise MetaMessagingError("Messenger не настроен: укажите MESSENGER_PAGE_TOKEN")

    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": body},
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{GRAPH_API}/me/messages",
            headers={"Authorization": f"Bearer {token}"},
            json=payload,
        )
        if resp.status_code >= 400:
            raise MetaMessagingError(f"Messenger API: {resp.text}")
        return resp.json()


def extract_message_body(msg: dict) -> tuple[str, str]:
    msg_type = msg.get("type", "text")
    if msg_type == "text":
        return "text", msg.get("text", {}).get("body", "")
    if msg_type == "image":
        caption = msg.get("image", {}).get("caption", "")
        return "image", caption or "[Изображение]"
    if msg_type == "audio":
        return "audio", "[Голосовое сообщение]"
    if msg_type == "video":
        return "video", "[Видео]"
    if msg_type == "document":
        return "document", "[Документ]"
    if msg_type == "sticker":
        return "sticker", "[Стикер]"
    if msg_type == "location":
        loc = msg.get("location", {})
        return "location", f"[Локация: {loc.get('latitude')}, {loc.get('longitude')}]"
    return msg_type, f"[{msg_type}]"


def parse_whatsapp_webhook(payload: dict) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    if payload.get("object") != "whatsapp_business_account":
        return events

    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            contacts_map = {
                c.get("wa_id"): c.get("profile", {}).get("name")
                for c in value.get("contacts", [])
            }

            for msg in value.get("messages", []):
                msg_type, body = extract_message_body(msg)
                sender = msg.get("from", "")
                events.append({
                    "kind": "message",
                    "channel": "whatsapp",
                    "external_id": sender,
                    "contact_name": contacts_map.get(sender),
                    "phone": f"+{sender}" if sender else None,
                    "message_external_id": msg.get("id"),
                    "body": body,
                    "message_type": msg_type,
                    "timestamp": msg.get("timestamp"),
                })

            for status in value.get("statuses", []):
                events.append({
                    "kind": "status",
                    "channel": "whatsapp",
                    "message_external_id": status.get("id"),
                    "status": status.get("status"),
                })

            for call in value.get("calls", []):
                events.append({
                    "kind": "call",
                    "channel": "whatsapp",
                    "external_id": call.get("from", ""),
                    "phone": f"+{call.get('from', '')}" if call.get("from") else None,
                    "direction": "inbound",
                    "status": call.get("event", "ringing"),
                    "duration_seconds": call.get("duration"),
                })

    return events


def parse_messenger_webhook(payload: dict) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    if payload.get("object") != "page":
        return events

    for entry in payload.get("entry", []):
        for item in entry.get("messaging", []):
            sender = item.get("sender", {}).get("id", "")
            if "message" in item:
                msg = item["message"]
                body = msg.get("text", "")
                if isinstance(body, dict):
                    body = body.get("body", "")
                if msg.get("attachments"):
                    att = msg["attachments"][0]
                    body = body or f"[{att.get('type', 'attachment')}]"
                events.append({
                    "kind": "message",
                    "channel": "messenger",
                    "external_id": sender,
                    "contact_name": None,
                    "phone": None,
                    "message_external_id": msg.get("mid"),
                    "body": body or "[Сообщение]",
                    "message_type": "text",
                    "timestamp": item.get("timestamp"),
                })
            elif "delivery" in item:
                for mid in item["delivery"].get("mids", []):
                    events.append({
                        "kind": "status",
                        "channel": "messenger",
                        "message_external_id": mid,
                        "status": "delivered",
                    })
            elif "read" in item:
                events.append({
                    "kind": "status",
                    "channel": "messenger",
                    "status": "read",
                })

    return events
