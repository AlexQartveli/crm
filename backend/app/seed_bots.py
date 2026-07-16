import json

from sqlalchemy.orm import Session

from app.models.automation import BotAction, BotTrigger, ChatBot, MessageTemplate


def seed_bots(db: Session, tenant_id: int, crm_type: str = "general") -> None:
    if db.query(ChatBot).filter(ChatBot.tenant_id == tenant_id).count() > 0:
        return

    welcome_texts = {
        "general": "Здравствуйте! Спасибо за обращение. Менеджер свяжется с вами в ближайшее время.",
        "education": "Gamarjoba! Madloba interesistvis. Shevigzavt tqven chanawer da dagikavshirdit.",
        "factory": "Здравствуйте! Отдел продаж обработает ваш запрос на поставку.",
        "retail": "Gamarjoba! Madloba shekvetistvis. Male dagikavshirdit.",
        "hospitality": "Welcome! Thank you for contacting us. We will confirm your booking shortly.",
        "construction": "Здравствуйте! Оценим ваш проект и свяжемся для уточнения деталей.",
        "agriculture": "Gamarjoba! Свяжемся для обсуждения объёма и условий поставки.",
        "medical": "Здравствуйте! Администратор клиники запишет вас на приём.",
        "logistics": "Здравствуйте! Рассчитаем стоимость перевозки и ответим в течение часа.",
        "services": "Здравствуйте! Обсудим ваш проект и подготовим коммерческое предложение.",
    }
    welcome_msg = welcome_texts.get(crm_type, welcome_texts["general"])

    welcome = ChatBot(
        tenant_id=tenant_id,
        name="Приветствие",
        description="Автоответ на первое сообщение и создание лида",
        channels="all",
        is_active=True,
        welcome_message=welcome_msg,
        priority=10,
    )
    db.add(welcome)
    db.flush()

    db.add(BotTrigger(
        bot_id=welcome.id,
        trigger_type="first_message",
        sort_order=0,
    ))
    db.add(BotAction(
        bot_id=welcome.id,
        action_type="send_message",
        config=json.dumps({"text": welcome_msg}),
        sort_order=0,
    ))
    db.add(BotAction(
        bot_id=welcome.id,
        action_type="create_lead",
        config=json.dumps({"title": "Входящий чат"}),
        sort_order=1,
    ))
    db.add(BotAction(
        bot_id=welcome.id,
        action_type="update_lead_status",
        config=json.dumps({"status": "in_progress"}),
        sort_order=2,
    ))

    price = ChatBot(
        tenant_id=tenant_id,
        name="Запрос цены",
        description="Ответ на ключевые слова: цена, прайс, стоимость",
        channels="all",
        is_active=True,
        priority=5,
    )
    db.add(price)
    db.flush()

    price_trigger = BotTrigger(
        bot_id=price.id,
        trigger_type="keyword",
        keyword="цена",
        sort_order=0,
    )
    db.add(price_trigger)
    db.flush()

    db.add(BotTrigger(
        bot_id=price.id,
        trigger_type="keyword",
        keyword="прайс",
        sort_order=1,
    ))
    db.add(BotAction(
        bot_id=price.id,
        trigger_id=price_trigger.id,
        action_type="send_message",
        config=json.dumps({
            "text": "Актуальный прайс отправим в течение 15 минут. Уточните, пожалуйста, какие позиции вас интересуют?",
        }),
        sort_order=0,
    ))
    db.add(BotAction(
        bot_id=price.id,
        action_type="update_lead_status",
        config=json.dumps({"status": "in_progress"}),
        sort_order=1,
    ))
    db.add(BotAction(
        bot_id=price.id,
        action_type="add_lead_comment",
        config=json.dumps({"text": "Клиент запросил цену через чат-бот"}),
        sort_order=2,
    ))

    deal_bot = ChatBot(
        tenant_id=tenant_id,
        name="Создание сделки",
        description="При слове «заказ» создаёт сделку в CRM",
        channels="all",
        is_active=True,
        priority=3,
    )
    db.add(deal_bot)
    db.flush()

    order_trigger = BotTrigger(
        bot_id=deal_bot.id,
        trigger_type="keyword",
        keyword="заказ",
        sort_order=0,
    )
    db.add(order_trigger)
    db.flush()

    db.add(BotAction(
        bot_id=deal_bot.id,
        trigger_id=order_trigger.id,
        action_type="send_message",
        config=json.dumps({"text": "Отлично! Оформляем заявку. Наш менеджер уточнит детали."}),
        sort_order=0,
    ))
    db.add(BotAction(
        bot_id=deal_bot.id,
        trigger_id=order_trigger.id,
        action_type="create_deal",
        config=json.dumps({"title": "Заказ из мессенджера", "stage": "new", "amount": 0}),
        sort_order=1,
    ))

    templates = [
        ("Приветствие", "Здравствуйте! Чем могу помочь?", "/hi"),
        ("Уточнение", "Подскажите, пожалуйста, ваш город и объём заказа.", "/ask"),
        ("Прайс", "Отправляю актуальный прайс-лист. Если нужна консультация — напишите.", "/price"),
        ("Спасибо", "Спасибо за обращение! Хорошего дня.", "/thanks"),
    ]
    for title, body, shortcut in templates:
        db.add(MessageTemplate(tenant_id=tenant_id, title=title, body=body, shortcut=shortcut))

    db.commit()
