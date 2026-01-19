"""数据访问层模型：定义 SQLite 表结构与关系。"""

import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text, text
from sqlalchemy.orm import relationship

from api.core.database import Base

TIMESTAMP_DEFAULT = text("(strftime('%Y-%m-%dT%H:%M:%fZ','now'))")


class User(Base):
    """用户表：预置账号，无注册流程。"""

    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    username = Column(String(64), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=TIMESTAMP_DEFAULT)

    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")


class UserSession(Base):
    """用户会话表：存储 JWT 以及过期/吊销状态。"""

    __tablename__ = "user_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    access_token = Column(Text, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=TIMESTAMP_DEFAULT)
    revoked_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="sessions")


class Conversation(Base):
    """对话表：记录用户对话头信息。"""

    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(128), nullable=True)
    created_at = Column(DateTime, server_default=TIMESTAMP_DEFAULT)
    updated_at = Column(DateTime, server_default=TIMESTAMP_DEFAULT, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="conversations")
    messages = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan", passive_deletes=True
    )


class Message(Base):
    """消息表：存储每条用户/Agent 消息及使用的智能体模式。"""

    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    conversation_id = Column(
        String, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role = Column(String(16), nullable=False)  # user | agent
    content = Column(Text, nullable=False)
    agent_mode = Column(String(32), nullable=False)
    created_at = Column(DateTime, server_default=TIMESTAMP_DEFAULT)

    conversation = relationship("Conversation", back_populates="messages")
