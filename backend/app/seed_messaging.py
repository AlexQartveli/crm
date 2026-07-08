from datetime import datetime, timedelta

from app.models.messaging import CallLog, Conversation, Message


def seed_messaging(db):
    if db.query(Conversation).first():
        return

    now = datetime.utcnow()

    wa_conv = Conversation(
        channel="whatsapp",
        external_id="79001234567",
        contact_name="Георгий Беридзе",
        phone="+79001234567",
        unread_count=2,
        last_message_at=now - timedelta(minutes=5),
        last_message_preview="Здравствуйте, интересует поставка оборудования",
    )
    db.add(wa_conv)
    db.flush()

    db.add_all([
        Message(
            conversation_id=wa_conv.id,
            direction="inbound",
            body="Здравствуйте, интересует поставка оборудования",
            message_type="text",
            status="received",
            created_at=now - timedelta(minutes=10),
        ),
        Message(
            conversation_id=wa_conv.id,
            direction="outbound",
            body="Добрый день! Подскажите, какое оборудование вас интересует?",
            message_type="text",
            status="delivered",
            created_at=now - timedelta(minutes=8),
        ),
        Message(
            conversation_id=wa_conv.id,
            direction="inbound",
            body="Нужны 10 единиц ноутбуков для офиса",
            message_type="text",
            status="received",
            created_at=now - timedelta(minutes=5),
        ),
    ])

    msg_conv = Conversation(
        channel="messenger",
        external_id="1234567890123456",
        contact_name="Nino Kvlividze",
        unread_count=1,
        last_message_at=now - timedelta(hours=1),
        last_message_preview="Можно узнать цену на мониторы?",
    )
    db.add(msg_conv)
    db.flush()

    db.add(Message(
        conversation_id=msg_conv.id,
        direction="inbound",
        body="Можно узнать цену на мониторы?",
        message_type="text",
        status="received",
        created_at=now - timedelta(hours=1),
    ))

    tg_conv = Conversation(
        channel="telegram",
        external_id="987654321",
        contact_name="David Chkheidze",
        unread_count=1,
        last_message_at=now - timedelta(minutes=30),
        last_message_preview="Добрый день, есть в наличии?",
        created_at=now,
    )
    db.add(tg_conv)
    db.flush()
    db.add(Message(
        conversation_id=tg_conv.id,
        direction="inbound",
        body="Добрый день, есть в наличии?",
        message_type="text",
        status="received",
        created_at=now - timedelta(minutes=30),
    ))

    db.add(CallLog(
        channel="whatsapp",
        external_id="79009876543",
        conversation_id=wa_conv.id,
        direction="inbound",
        status="missed",
        contact_name="Георгий Беридзе",
        phone="+79009876543",
        started_at=now - timedelta(hours=2),
    ))

    db.commit()
