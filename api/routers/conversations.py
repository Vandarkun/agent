"""会话与消息路由：暴露会话 CRUD 与消息发送/查询接口。"""

from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from api.core.database import get_db
from api.core.security import get_current_user
from api.repositories.models import User
from api.schemas import (
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessagesPage,
    MessageResponse,
)
from api.services.conversation_service import (
    create_conversation,
    delete_conversation,
    list_conversations,
    list_messages,
)
from api.services.message_service import send_message

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation_endpoint(
    payload: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建新对话，返回对话基本信息。"""
    return create_conversation(db=db, user=current_user, payload=payload)


@router.get("", response_model=List[ConversationResponse])
def list_conversations_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """列出当前用户的所有对话。"""
    return list_conversations(db=db, user=current_user)


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation_endpoint(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除指定对话（级联删除消息）。"""
    return delete_conversation(db=db, user=current_user, conversation_id=conversation_id)


@router.get("/{conversation_id}/messages", response_model=MessagesPage)
def list_messages_endpoint(
    conversation_id: str,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """分页查询指定对话的消息列表。"""
    return list_messages(
        db=db,
        user=current_user,
        conversation_id=conversation_id,
        limit=limit,
        offset=offset,
    )


@router.post("/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def send_message_endpoint(
    conversation_id: str,
    payload: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """发送用户消息，按选择的 Agent 模式获取回复并落库。"""
    return await send_message(
        db=db,
        user=current_user,
        conversation_id=conversation_id,
        payload=payload,
    )
