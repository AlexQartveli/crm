from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.automation import BotAction, BotLog, BotTrigger, ChatBot, MessageTemplate
from app.schemas.automation import (
    BotLogResponse,
    ChatBotCreate,
    ChatBotResponse,
    ChatBotUpdate,
    MessageTemplateCreate,
    MessageTemplateResponse,
    MessageTemplateUpdate,
)

router = APIRouter(prefix="/automations", tags=["Automations"])


def _bot_response(bot: ChatBot) -> ChatBotResponse:
    return ChatBotResponse.model_validate(bot)


@router.get("/bots", response_model=list[ChatBotResponse])
def list_bots(db: Session = Depends(get_db)):
    bots = db.query(ChatBot).order_by(ChatBot.priority.desc(), ChatBot.name.asc()).all()
    return [_bot_response(b) for b in bots]


@router.get("/bots/{bot_id}", response_model=ChatBotResponse)
def get_bot(bot_id: int, db: Session = Depends(get_db)):
    bot = db.query(ChatBot).filter(ChatBot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Бот не найден")
    return _bot_response(bot)


@router.post("/bots", response_model=ChatBotResponse, status_code=201)
def create_bot(data: ChatBotCreate, db: Session = Depends(get_db)):
    bot = ChatBot(
        name=data.name,
        description=data.description,
        channels=data.channels,
        is_active=data.is_active,
        welcome_message=data.welcome_message,
        fallback_message=data.fallback_message,
        priority=data.priority,
    )
    db.add(bot)
    db.flush()

    trigger_map: dict[int, int] = {}
    for i, t in enumerate(data.triggers):
        trigger = BotTrigger(
            bot_id=bot.id,
            trigger_type=t.trigger_type,
            keyword=t.keyword,
            sort_order=t.sort_order if t.sort_order else i,
        )
        db.add(trigger)
        db.flush()
        trigger_map[i] = trigger.id

    for i, a in enumerate(data.actions):
        db.add(BotAction(
            bot_id=bot.id,
            trigger_id=a.trigger_id,
            action_type=a.action_type,
            config=a.config,
            sort_order=a.sort_order if a.sort_order else i,
        ))

    db.commit()
    db.refresh(bot)
    return _bot_response(bot)


@router.patch("/bots/{bot_id}", response_model=ChatBotResponse)
def update_bot(bot_id: int, data: ChatBotUpdate, db: Session = Depends(get_db)):
    bot = db.query(ChatBot).filter(ChatBot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Бот не найден")

    for field in ("name", "description", "channels", "is_active", "welcome_message", "fallback_message", "priority"):
        value = getattr(data, field)
        if value is not None:
            setattr(bot, field, value)
    bot.updated_at = datetime.utcnow()

    if data.triggers is not None:
        db.query(BotTrigger).filter(BotTrigger.bot_id == bot.id).delete()
        for i, t in enumerate(data.triggers):
            db.add(BotTrigger(
                bot_id=bot.id,
                trigger_type=t.trigger_type,
                keyword=t.keyword,
                sort_order=t.sort_order if t.sort_order else i,
            ))

    if data.actions is not None:
        db.query(BotAction).filter(BotAction.bot_id == bot.id).delete()
        for i, a in enumerate(data.actions):
            db.add(BotAction(
                bot_id=bot.id,
                trigger_id=a.trigger_id,
                action_type=a.action_type,
                config=a.config,
                sort_order=a.sort_order if a.sort_order else i,
            ))

    db.commit()
    db.refresh(bot)
    return _bot_response(bot)


@router.delete("/bots/{bot_id}", status_code=204)
def delete_bot(bot_id: int, db: Session = Depends(get_db)):
    bot = db.query(ChatBot).filter(ChatBot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Бот не найден")
    db.delete(bot)
    db.commit()


@router.patch("/bots/{bot_id}/toggle", response_model=ChatBotResponse)
def toggle_bot(bot_id: int, db: Session = Depends(get_db)):
    bot = db.query(ChatBot).filter(ChatBot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Бот не найден")
    bot.is_active = not bot.is_active
    bot.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(bot)
    return _bot_response(bot)


@router.get("/templates", response_model=list[MessageTemplateResponse])
def list_templates(db: Session = Depends(get_db)):
    return db.query(MessageTemplate).order_by(MessageTemplate.title.asc()).all()


@router.post("/templates", response_model=MessageTemplateResponse, status_code=201)
def create_template(data: MessageTemplateCreate, db: Session = Depends(get_db)):
    tpl = MessageTemplate(**data.model_dump())
    db.add(tpl)
    db.commit()
    db.refresh(tpl)
    return tpl


@router.patch("/templates/{template_id}", response_model=MessageTemplateResponse)
def update_template(template_id: int, data: MessageTemplateUpdate, db: Session = Depends(get_db)):
    tpl = db.query(MessageTemplate).filter(MessageTemplate.id == template_id).first()
    if not tpl:
        raise HTTPException(status_code=404, detail="Шаблон не найден")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(tpl, field, value)
    db.commit()
    db.refresh(tpl)
    return tpl


@router.delete("/templates/{template_id}", status_code=204)
def delete_template(template_id: int, db: Session = Depends(get_db)):
    tpl = db.query(MessageTemplate).filter(MessageTemplate.id == template_id).first()
    if not tpl:
        raise HTTPException(status_code=404, detail="Шаблон не найден")
    db.delete(tpl)
    db.commit()


@router.get("/logs", response_model=list[BotLogResponse])
def list_logs(limit: int = 100, db: Session = Depends(get_db)):
    return (
        db.query(BotLog)
        .order_by(BotLog.created_at.desc())
        .limit(min(limit, 500))
        .all()
    )
