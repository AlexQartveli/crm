"""Интеграция Telegram Bot API."""

import os
from typing import Any

import httpx

MOCK_MODE = os.getenv("MESSAGING_MOCK", "true").lower() == "true"


class TelegramError(Exception):
    pass


def _get_bot_token(db_settings: dict | None = None) -> str | None:
    if db_settings and db_settings.get("telegram_bot_token"):
        return db_settings["telegram_bot_token"]
    return os.getenv("TELEGRAM_BOT_TOKEN")


async def send_telegram_text(
    chat_id: str,
    body: str,
    db_settings: dict | None = None,
) -> dict:
    if MOCK_MODE:
        return {"ok": True, "result": {"message_id": f"mock-tg-{chat_id}"}}

    token = _get_bot_token(db_settings)
    if not token:
        raise TelegramError("Telegram не настроен: укажите Bot Token")

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": body},
        )
        data = resp.json()
        if not data.get("ok"):
            raise TelegramError(f"Telegram API: {data.get('description', resp.text)}")
        return data


async def setup_webhook(
    webhook_url: str,
    db_settings: dict | None = None,
    secret_token: str | None = None,
) -> dict:
    if MOCK_MODE:
        return {"ok": True, "description": "Webhook set (mock)"}

    token = _get_bot_token(db_settings)
    if not token:
        raise TelegramError("Telegram не настроен: укажите Bot Token")

    payload: dict[str, Any] = {"url": webhook_url}
    if secret_token:
        payload["secret_token"] = secret_token

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"https://api.telegram.org/bot{token}/setWebhook",
            json=payload,
        )
        data = resp.json()
        if not data.get("ok"):
            raise TelegramError(f"Telegram webhook: {data.get('description', resp.text)}")
        return data


async def get_webhook_info(db_settings: dict | None = None) -> dict:
    if MOCK_MODE:
        return {"ok": True, "result": {"url": "", "has_custom_certificate": False}}

    token = _get_bot_token(db_settings)
    if not token:
        raise TelegramError("Telegram не настроен: укажите Bot Token")

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(f"https://api.telegram.org/bot{token}/getWebhookInfo")
        data = resp.json()
        if not data.get("ok"):
            raise TelegramError(f"Telegram API: {data.get('description', resp.text)}")
        return data


def parse_telegram_webhook(payload: dict) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []

    msg = payload.get("message") or payload.get("edited_message")
    if msg:
        user = msg.get("from", {})
        chat = msg.get("chat", {})
        chat_id = str(chat.get("id", user.get("id", "")))
        name_parts = [user.get("first_name"), user.get("last_name")]
        contact_name = " ".join(p for p in name_parts if p).strip() or user.get("username")
        text = msg.get("text") or msg.get("caption")
        if not text:
            if msg.get("photo"):
                text = "[Фото]"
            elif msg.get("document"):
                text = "[Документ]"
            elif msg.get("voice"):
                text = "[Голосовое сообщение]"
            elif msg.get("contact"):
                text = "[Контакт]"
                phone = msg["contact"].get("phone_number")
            else:
                text = "[Сообщение]"
        phone = None
        if msg.get("contact"):
            phone = msg["contact"].get("phone_number")

        events.append({
            "kind": "message",
            "channel": "telegram",
            "external_id": chat_id,
            "contact_name": contact_name,
            "phone": phone,
            "message_external_id": f"tg-{chat_id}-{msg.get('message_id')}",
            "body": text,
            "message_type": "text",
        })

    return events
