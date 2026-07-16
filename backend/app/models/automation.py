from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ChatBot(Base):
    __tablename__ = "chat_bots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("tenants.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    channels: Mapped[str] = mapped_column(String(100), default="all")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    welcome_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    fallback_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    triggers: Mapped[list["BotTrigger"]] = relationship(
        back_populates="bot", cascade="all, delete-orphan", order_by="BotTrigger.sort_order"
    )
    actions: Mapped[list["BotAction"]] = relationship(
        back_populates="bot", cascade="all, delete-orphan", order_by="BotAction.sort_order"
    )


class BotTrigger(Base):
    __tablename__ = "bot_triggers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    bot_id: Mapped[int] = mapped_column(Integer, ForeignKey("chat_bots.id"), index=True)
    trigger_type: Mapped[str] = mapped_column(String(50))
    keyword: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    bot: Mapped["ChatBot"] = relationship(back_populates="triggers")


class BotAction(Base):
    __tablename__ = "bot_actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    bot_id: Mapped[int] = mapped_column(Integer, ForeignKey("chat_bots.id"), index=True)
    trigger_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("bot_triggers.id"), nullable=True
    )
    action_type: Mapped[str] = mapped_column(String(50))
    config: Mapped[str] = mapped_column(Text, default="{}")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    bot: Mapped["ChatBot"] = relationship(back_populates="actions")


class MessageTemplate(Base):
    __tablename__ = "message_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("tenants.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    channel: Mapped[str | None] = mapped_column(String(20), nullable=True)
    shortcut: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class BotLog(Base):
    __tablename__ = "bot_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("tenants.id"), index=True)
    bot_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("chat_bots.id"), nullable=True)
    conversation_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("conversations.id"), nullable=True
    )
    trigger_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    action_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
