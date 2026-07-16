from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from app.deps.tenant import TenantCtx, get_tenant_ctx, scoped
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
def list_bots(ctx: TenantCtx = Depends(get_tenant_ctx)):
    bots = (
        scoped(ctx, ChatBot)
        .order_by(ChatBot.priority.desc(), ChatBot.name.asc())
        .all()
    )
    return [_bot_response(b) for b in bots]


@router.get("/bots/{bot_id}", response_model=ChatBotResponse)
def get_bot(bot_id: int, ctx: TenantCtx = Depends(get_tenant_ctx)):
    bot = scoped(ctx, ChatBot).filter(ChatBot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Бот не найден")
    return _bot_response(bot)


@router.post("/bots", response_model=ChatBotResponse, status_code=201)
def create_bot(data: ChatBotCreate, ctx: TenantCtx = Depends(get_tenant_ctx)):
    bot = ChatBot(
        tenant_id=ctx.tenant_id,
        name=data.name,
        description=data.description,
        channels=data.channels,
        is_active=data.is_active,
        welcome_message=data.welcome_message,
        fallback_message=data.fallback_message,
        priority=data.priority,
    )
    ctx.db.add(bot)
    ctx.db.flush()

    for i, t in enumerate(data.triggers):
        trigger = BotTrigger(
            bot_id=bot.id,
            trigger_type=t.trigger_type,
            keyword=t.keyword,
            sort_order=t.sort_order if t.sort_order else i,
        )
        ctx.db.add(trigger)
        ctx.db.flush()

    for i, a in enumerate(data.actions):
        ctx.db.add(BotAction(
            bot_id=bot.id,
            trigger_id=a.trigger_id,
            action_type=a.action_type,
            config=a.config,
            sort_order=a.sort_order if a.sort_order else i,
        ))

    ctx.db.commit()
    ctx.db.refresh(bot)
    return _bot_response(bot)


@router.patch("/bots/{bot_id}", response_model=ChatBotResponse)
def update_bot(bot_id: int, data: ChatBotUpdate, ctx: TenantCtx = Depends(get_tenant_ctx)):
    bot = scoped(ctx, ChatBot).filter(ChatBot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Бот не найден")

    for field in ("name", "description", "channels", "is_active", "welcome_message", "fallback_message", "priority"):
        value = getattr(data, field)
        if value is not None:
            setattr(bot, field, value)
    bot.updated_at = datetime.utcnow()

    if data.triggers is not None:
        ctx.db.query(BotTrigger).filter(BotTrigger.bot_id == bot.id).delete()
        for i, t in enumerate(data.triggers):
            ctx.db.add(BotTrigger(
                bot_id=bot.id,
                trigger_type=t.trigger_type,
                keyword=t.keyword,
                sort_order=t.sort_order if t.sort_order else i,
            ))

    if data.actions is not None:
        ctx.db.query(BotAction).filter(BotAction.bot_id == bot.id).delete()
        for i, a in enumerate(data.actions):
            ctx.db.add(BotAction(
                bot_id=bot.id,
                trigger_id=a.trigger_id,
                action_type=a.action_type,
                config=a.config,
                sort_order=a.sort_order if a.sort_order else i,
            ))

    ctx.db.commit()
    ctx.db.refresh(bot)
    return _bot_response(bot)


@router.delete("/bots/{bot_id}", status_code=204)
def delete_bot(bot_id: int, ctx: TenantCtx = Depends(get_tenant_ctx)):
    bot = scoped(ctx, ChatBot).filter(ChatBot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Бот не найден")
    ctx.db.delete(bot)
    ctx.db.commit()


@router.patch("/bots/{bot_id}/toggle", response_model=ChatBotResponse)
def toggle_bot(bot_id: int, ctx: TenantCtx = Depends(get_tenant_ctx)):
    bot = scoped(ctx, ChatBot).filter(ChatBot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Бот не найден")
    bot.is_active = not bot.is_active
    bot.updated_at = datetime.utcnow()
    ctx.db.commit()
    ctx.db.refresh(bot)
    return _bot_response(bot)


@router.get("/templates", response_model=list[MessageTemplateResponse])
def list_templates(ctx: TenantCtx = Depends(get_tenant_ctx)):
    return scoped(ctx, MessageTemplate).order_by(MessageTemplate.title.asc()).all()


@router.post("/templates", response_model=MessageTemplateResponse, status_code=201)
def create_template(data: MessageTemplateCreate, ctx: TenantCtx = Depends(get_tenant_ctx)):
    tpl = MessageTemplate(tenant_id=ctx.tenant_id, **data.model_dump())
    ctx.db.add(tpl)
    ctx.db.commit()
    ctx.db.refresh(tpl)
    return tpl


@router.patch("/templates/{template_id}", response_model=MessageTemplateResponse)
def update_template(template_id: int, data: MessageTemplateUpdate, ctx: TenantCtx = Depends(get_tenant_ctx)):
    tpl = scoped(ctx, MessageTemplate).filter(MessageTemplate.id == template_id).first()
    if not tpl:
        raise HTTPException(status_code=404, detail="Шаблон не найден")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(tpl, field, value)
    ctx.db.commit()
    ctx.db.refresh(tpl)
    return tpl


@router.delete("/templates/{template_id}", status_code=204)
def delete_template(template_id: int, ctx: TenantCtx = Depends(get_tenant_ctx)):
    tpl = scoped(ctx, MessageTemplate).filter(MessageTemplate.id == template_id).first()
    if not tpl:
        raise HTTPException(status_code=404, detail="Шаблон не найден")
    ctx.db.delete(tpl)
    ctx.db.commit()


@router.get("/logs", response_model=list[BotLogResponse])
def list_logs(limit: int = 100, ctx: TenantCtx = Depends(get_tenant_ctx)):
    return (
        scoped(ctx, BotLog)
        .order_by(BotLog.created_at.desc())
        .limit(min(limit, 500))
        .all()
    )
