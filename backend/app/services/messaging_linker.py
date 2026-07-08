"""Обратная совместимость — используйте messaging_sync."""

from app.services.messaging_sync import (
    ensure_lead_for_inbound,
    find_contact_by_phone,
    find_lead_by_phone,
    link_conversation,
    normalize_phone,
)

__all__ = [
    "ensure_lead_for_inbound",
    "find_contact_by_phone",
    "find_lead_by_phone",
    "link_conversation",
    "normalize_phone",
]
