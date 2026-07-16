from datetime import datetime

from pydantic import BaseModel, Field


class BotTriggerBase(BaseModel):
    trigger_type: str
    keyword: str | None = None
    sort_order: int = 0


class BotTriggerCreate(BotTriggerBase):
    pass


class BotTriggerResponse(BotTriggerBase):
    id: int
    bot_id: int

    model_config = {"from_attributes": True}


class BotActionBase(BaseModel):
    trigger_id: int | None = None
    action_type: str
    config: str = "{}"
    sort_order: int = 0


class BotActionCreate(BotActionBase):
    pass


class BotActionResponse(BotActionBase):
    id: int
    bot_id: int

    model_config = {"from_attributes": True}


class ChatBotBase(BaseModel):
    name: str
    description: str | None = None
    channels: str = "all"
    is_active: bool = True
    welcome_message: str | None = None
    fallback_message: str | None = None
    priority: int = 0


class ChatBotCreate(ChatBotBase):
    triggers: list[BotTriggerCreate] = Field(default_factory=list)
    actions: list[BotActionCreate] = Field(default_factory=list)


class ChatBotUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    channels: str | None = None
    is_active: bool | None = None
    welcome_message: str | None = None
    fallback_message: str | None = None
    priority: int | None = None
    triggers: list[BotTriggerCreate] | None = None
    actions: list[BotActionCreate] | None = None


class ChatBotResponse(ChatBotBase):
    id: int
    created_at: datetime
    updated_at: datetime
    triggers: list[BotTriggerResponse] = Field(default_factory=list)
    actions: list[BotActionResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class MessageTemplateBase(BaseModel):
    title: str
    body: str
    channel: str | None = None
    shortcut: str | None = None


class MessageTemplateCreate(MessageTemplateBase):
    pass


class MessageTemplateUpdate(BaseModel):
    title: str | None = None
    body: str | None = None
    channel: str | None = None
    shortcut: str | None = None


class MessageTemplateResponse(MessageTemplateBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class BotLogResponse(BaseModel):
    id: int
    bot_id: int | None
    conversation_id: int | None
    trigger_type: str | None
    action_type: str | None
    detail: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
