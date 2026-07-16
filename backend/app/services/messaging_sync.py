"""Синхронизация диалогов мессенджеров с CRM (контакты, лиды, компании)."""

import re

from sqlalchemy.orm import Session

from app.models.crm import Company, Contact, Lead, LeadStatus
from app.models.messaging import CallLog, Conversation

CHANNEL_SOURCES = {
    "whatsapp": "WhatsApp",
    "messenger": "Facebook Messenger",
    "telegram": "Telegram",
}


def normalize_phone(phone: str | None) -> str | None:
    if not phone:
        return None
    digits = re.sub(r"\D", "", phone)
    if len(digits) >= 10:
        return digits[-10:]
    return digits or None


def channel_source(channel: str) -> str:
    return CHANNEL_SOURCES.get(channel, channel)


def find_contact_by_phone(db: Session, phone: str | None, tenant_id: int) -> Contact | None:
    target = normalize_phone(phone)
    if not target:
        return None
    for contact in (
        db.query(Contact)
        .filter(Contact.tenant_id == tenant_id, Contact.phone.isnot(None))
        .all()
    ):
        if normalize_phone(contact.phone) == target:
            return contact
    return None


def find_lead_by_phone(db: Session, phone: str | None, tenant_id: int) -> Lead | None:
    target = normalize_phone(phone)
    if not target:
        return None
    for lead in (
        db.query(Lead)
        .filter(Lead.tenant_id == tenant_id, Lead.phone.isnot(None))
        .all()
    ):
        if normalize_phone(lead.phone) == target:
            return lead
    return None


def find_lead_by_name(db: Session, name: str | None, tenant_id: int) -> Lead | None:
    if not name or len(name.strip()) < 2:
        return None
    lowered = name.strip().lower()
    for lead in (
        db.query(Lead)
        .filter(Lead.tenant_id == tenant_id, Lead.name.isnot(None))
        .all()
    ):
        if lead.name and lead.name.strip().lower() == lowered:
            return lead
    return None


def _propagate_links_by_phone(
    db: Session,
    phone: str | None,
    contact_id: int | None,
    lead_id: int | None,
    tenant_id: int,
) -> int:
    target = normalize_phone(phone)
    if not target:
        return 0
    updated = 0
    for conv in (
        db.query(Conversation)
        .filter(Conversation.tenant_id == tenant_id, Conversation.phone.isnot(None))
        .all()
    ):
        if normalize_phone(conv.phone) != target:
            continue
        changed = False
        if contact_id and conv.contact_id != contact_id:
            conv.contact_id = contact_id
            changed = True
        if lead_id and conv.lead_id != lead_id:
            conv.lead_id = lead_id
            changed = True
        if changed:
            updated += 1
    for call in (
        db.query(CallLog)
        .filter(CallLog.tenant_id == tenant_id, CallLog.phone.isnot(None))
        .all()
    ):
        if normalize_phone(call.phone) != target:
            continue
        if contact_id:
            call.contact_id = contact_id
        if lead_id:
            call.lead_id = lead_id
    return updated


def _sync_crm_entity_from_conversation(db: Session, conversation: Conversation) -> None:
    """Обновляет телефон/имя в лиде и контакте из диалога."""
    if conversation.phone:
        if conversation.lead_id:
            lead = (
                db.query(Lead)
                .filter(Lead.id == conversation.lead_id, Lead.tenant_id == conversation.tenant_id)
                .first()
            )
            if lead and not lead.phone:
                lead.phone = conversation.phone
        if conversation.contact_id:
            contact = (
                db.query(Contact)
                .filter(
                    Contact.id == conversation.contact_id,
                    Contact.tenant_id == conversation.tenant_id,
                )
                .first()
            )
            if contact and not contact.phone:
                contact.phone = conversation.phone

    if conversation.contact_name:
        if conversation.lead_id:
            lead = (
                db.query(Lead)
                .filter(Lead.id == conversation.lead_id, Lead.tenant_id == conversation.tenant_id)
                .first()
            )
            if lead and not lead.name:
                lead.name = conversation.contact_name
        if conversation.contact_id:
            contact = (
                db.query(Contact)
                .filter(
                    Contact.id == conversation.contact_id,
                    Contact.tenant_id == conversation.tenant_id,
                )
                .first()
            )
            if contact and contact.name != conversation.contact_name:
                pass  # не перезаписываем имя контакта автоматически


def ensure_lead_for_inbound(
    db: Session,
    *,
    tenant_id: int,
    channel: str,
    phone: str | None,
    contact_name: str | None,
    external_id: str | None = None,
) -> Lead | None:
    if phone:
        existing = find_lead_by_phone(db, phone, tenant_id)
        if existing:
            return existing

    contact = find_contact_by_phone(db, phone, tenant_id)
    if contact:
        return None

    if contact_name:
        by_name = find_lead_by_name(db, contact_name, tenant_id)
        if by_name:
            return by_name

    source = channel_source(channel)
    name = contact_name or phone or external_id or "Неизвестный"
    lead = Lead(
        tenant_id=tenant_id,
        title=f"Входящий {source}: {name}",
        name=contact_name,
        phone=phone,
        source=source,
        status=LeadStatus.NEW.value,
        comment=f"Автоматически создан из {source}",
    )
    db.add(lead)
    db.flush()
    return lead


def convert_conversation_to_contact(db: Session, conversation: Conversation) -> Contact:
    tenant_id = conversation.tenant_id
    if conversation.contact_id:
        contact = (
            db.query(Contact)
            .filter(Contact.id == conversation.contact_id, Contact.tenant_id == tenant_id)
            .first()
        )
        if contact:
            return contact

    contact = Contact(
        tenant_id=tenant_id,
        name=conversation.contact_name or conversation.phone or f"Клиент {conversation.external_id}",
        phone=conversation.phone,
    )
    db.add(contact)
    db.flush()

    conversation.contact_id = contact.id
    if conversation.lead_id:
        lead = (
            db.query(Lead)
            .filter(Lead.id == conversation.lead_id, Lead.tenant_id == tenant_id)
            .first()
        )
        if lead:
            lead.status = LeadStatus.CONVERTED.value
            if not lead.name and conversation.contact_name:
                lead.name = conversation.contact_name

    _propagate_links_by_phone(
        db, conversation.phone, contact.id, conversation.lead_id, tenant_id
    )
    return contact


def link_conversation(
    db: Session,
    conversation: Conversation,
    *,
    phone: str | None = None,
    contact_name: str | None = None,
    auto_create_lead: bool = True,
) -> None:
    tenant_id = conversation.tenant_id
    if phone and not conversation.phone:
        conversation.phone = phone
    if contact_name and not conversation.contact_name:
        conversation.contact_name = contact_name

    contact = find_contact_by_phone(db, conversation.phone, tenant_id)
    if contact:
        conversation.contact_id = contact.id
        if not conversation.contact_name:
            conversation.contact_name = contact.name

    lead = find_lead_by_phone(db, conversation.phone, tenant_id)
    if not lead and conversation.contact_name:
        lead = find_lead_by_name(db, conversation.contact_name, tenant_id)

    if lead:
        conversation.lead_id = lead.id
        if contact and lead.status == LeadStatus.NEW.value:
            lead.status = LeadStatus.IN_PROGRESS.value
    elif auto_create_lead:
        new_lead = ensure_lead_for_inbound(
            db,
            tenant_id=tenant_id,
            channel=conversation.channel,
            phone=conversation.phone,
            contact_name=conversation.contact_name,
            external_id=conversation.external_id,
        )
        if new_lead:
            conversation.lead_id = new_lead.id

    _sync_crm_entity_from_conversation(db, conversation)
    _propagate_links_by_phone(
        db,
        conversation.phone,
        conversation.contact_id,
        conversation.lead_id,
        tenant_id,
    )


def sync_conversation(db: Session, conversation: Conversation) -> None:
    link_conversation(
        db,
        conversation,
        phone=conversation.phone,
        contact_name=conversation.contact_name,
        auto_create_lead=True,
    )


def sync_by_contact(db: Session, contact_id: int, tenant_id: int) -> int:
    contact = (
        db.query(Contact)
        .filter(Contact.id == contact_id, Contact.tenant_id == tenant_id)
        .first()
    )
    if not contact:
        return 0
    count = 0
    for conv in db.query(Conversation).filter(Conversation.tenant_id == tenant_id).all():
        matched = False
        if contact.phone and conv.phone and normalize_phone(contact.phone) == normalize_phone(conv.phone):
            matched = True
        if conv.contact_id == contact.id:
            matched = True
        if matched:
            conv.contact_id = contact.id
            if not conv.contact_name:
                conv.contact_name = contact.name
            if not conv.phone and contact.phone:
                conv.phone = contact.phone
            sync_conversation(db, conv)
            count += 1
    return count


def sync_by_lead(db: Session, lead_id: int, tenant_id: int) -> int:
    lead = (
        db.query(Lead)
        .filter(Lead.id == lead_id, Lead.tenant_id == tenant_id)
        .first()
    )
    if not lead:
        return 0
    count = 0
    for conv in db.query(Conversation).filter(Conversation.tenant_id == tenant_id).all():
        matched = False
        if lead.phone and conv.phone and normalize_phone(lead.phone) == normalize_phone(conv.phone):
            matched = True
        if conv.lead_id == lead.id:
            matched = True
        if matched:
            conv.lead_id = lead.id
            if not conv.contact_name and lead.name:
                conv.contact_name = lead.name
            if not conv.phone and lead.phone:
                conv.phone = lead.phone
            sync_conversation(db, conv)
            count += 1
    return count


def sync_all(db: Session, tenant_id: int) -> dict:
    conversations = (
        db.query(Conversation).filter(Conversation.tenant_id == tenant_id).all()
    )

    for conv in conversations:
        sync_conversation(db, conv)

    for contact in db.query(Contact).filter(Contact.tenant_id == tenant_id).all():
        sync_by_contact(db, contact.id, tenant_id)

    for lead in db.query(Lead).filter(Lead.tenant_id == tenant_id).all():
        sync_by_lead(db, lead.id, tenant_id)

    messenger_leads = (
        db.query(Lead)
        .filter(Lead.tenant_id == tenant_id, Lead.source.in_(list(CHANNEL_SOURCES.values())))
        .count()
    )

    return {
        "conversations": len(conversations),
        "linked_contacts": sum(1 for c in conversations if c.contact_id),
        "linked_leads": sum(1 for c in conversations if c.lead_id),
        "created_leads": messenger_leads,
    }


def get_company_name(db: Session, contact_id: int | None, tenant_id: int) -> str | None:
    if not contact_id:
        return None
    contact = (
        db.query(Contact)
        .filter(Contact.id == contact_id, Contact.tenant_id == tenant_id)
        .first()
    )
    if not contact or not contact.company_id:
        return None
    company = (
        db.query(Company)
        .filter(Company.id == contact.company_id, Company.tenant_id == tenant_id)
        .first()
    )
    return company.name if company else None
