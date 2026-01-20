"""会话服务层：封装对话及消息的业务操作。"""

from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from api.repositories.models import Conversation, Message, User
from api.schemas import ConversationCreate, ConversationResponse, MessagesPage, MessageListItem


def create_conversation(db: Session, user: User, payload: ConversationCreate) -> ConversationResponse:
    """创建对话并持久化。"""
    conversation = Conversation(user_id=user.id, title=payload.title)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def list_conversations(db: Session, user: User) -> List[ConversationResponse]:
    """返回用户所有对话（按创建时间倒序）。"""
    return (
        db.query(Conversation)
        .filter(Conversation.user_id == user.id)
        .order_by(Conversation.created_at.desc())
        .all()
    )


def delete_conversation(db: Session, user: User, conversation_id: str) -> None:
    """删除指定对话，不存在则抛 404。"""
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == user.id)
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    db.delete(conversation)
    db.commit()


def list_messages(
    db: Session,
    user: User,
    conversation_id: str,
    limit: int,
    offset: int,
) -> MessagesPage:
    """分页查询指定对话的消息列表。"""
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == user.id)
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    query = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    total = query.count()
    items = query.offset(offset).limit(limit).all()
    return MessagesPage(items=[MessageListItem.model_validate(item) for item in items], total=total)
