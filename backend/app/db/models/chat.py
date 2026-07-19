"""
Chat session and message models.
Supports the Conversation Manager — multi-turn stateful conversations.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class SessionStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class ChatSession(Base):
    """
    Represents a single conversation session.
    Tracks which commerce domain is active and the current workflow state.
    """
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Domain routing
    active_domain = Column(String, nullable=True)           # "grocery" | "food_ordering"
    workflow_state = Column(String, nullable=True)          # current state machine node

    # Conversation health
    status = Column(SAEnum(SessionStatus), default=SessionStatus.ACTIVE, nullable=False)
    turn_count = Column(Integer, default=0)

    # Compressed history injected into LLM context
    conversation_summary = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)

    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan",
                            order_by="ChatMessage.created_at")
    user = relationship("User", back_populates="chat_sessions")


class ChatMessage(Base):
    """
    A single turn in a conversation.
    Stores both the raw content and any structured JSON payload extracted by the LLM.
    """
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False, index=True)

    role = Column(SAEnum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)

    # Structured output extracted from this message (if role == assistant)
    intent = Column(String, nullable=True)
    structured_payload = Column(Text, nullable=True)        # JSON string

    # Token usage for cost tracking
    token_count = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ChatSession", back_populates="messages")
