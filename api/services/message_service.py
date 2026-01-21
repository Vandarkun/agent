"""消息服务层：负责落库用户/Agent 消息并调用对应 Agent 获取回复。"""

from typing import AsyncGenerator

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from api.core.agent_runner import (
    SUPPORTED_AGENT_MODES,
    invoke_agent,
    invoke_agent_stream,
    normalize_agent_mode,
)
from api.repositories.models import Conversation, Message, User
from api.schemas import MessageCreate, MessageResponse


async def send_message(
    db: Session,
    user: User,
    conversation_id: str,
    payload: MessageCreate,
) -> MessageResponse:
    """保存用户消息、调用 Agent 获取回复并存入数据库。"""
    agent_mode = normalize_agent_mode(payload.agent_mode)
    if agent_mode not in SUPPORTED_AGENT_MODES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported agent mode")

    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == user.id)
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=payload.content,
        agent_mode=agent_mode,
    )
    db.add(user_message)
    db.flush()

    try:
        answer = await invoke_agent(agent_mode, payload.content, user_id=user.id)
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    agent_message = Message(
        conversation_id=conversation_id,
        role="agent",
        content=answer,
        agent_mode=agent_mode,
    )
    db.add(agent_message)
    db.commit()
    db.refresh(agent_message)

    return MessageResponse(
        message_id=agent_message.id,
        conversation_id=conversation_id,
        agent_mode=agent_mode,
        answer=answer,
    )


async def stream_message(
    db: Session,
    user: User,
    conversation_id: str,
    payload: MessageCreate,
) -> AsyncGenerator[str, None]:
    """保存用户消息、流式调用 Agent 并最终落库回复内容。"""
    agent_mode = normalize_agent_mode(payload.agent_mode)
    if agent_mode not in SUPPORTED_AGENT_MODES:
        yield "\n[ERROR] Unsupported agent mode"
        return

    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == user.id)
        .first()
    )
    if not conversation:
        yield "\n[ERROR] Conversation not found"
        return

    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=payload.content,
        agent_mode=agent_mode,
    )
    db.add(user_message)
    db.flush()

    answer_chunks: list[str] = []
    received_chunk = False
    try:
        async for chunk in invoke_agent_stream(agent_mode, payload.content, user_id=user.id):
            if chunk:
                received_chunk = True
                answer_chunks.append(chunk)
                yield chunk
    except HTTPException as exc:
        db.rollback()
        yield f"\n[ERROR] {exc.detail}"
        return
    except Exception as exc:
        db.rollback()
        yield f"\n[ERROR] {str(exc)}"
        return

    if not received_chunk:
        try:
            answer = await invoke_agent(agent_mode, payload.content, user_id=user.id)
        except HTTPException as exc:
            db.rollback()
            yield f"\n[ERROR] {exc.detail}"
            return
        except Exception as exc:
            db.rollback()
            yield f"\n[ERROR] {str(exc)}"
            return
        if answer:
            answer_chunks.append(answer)
            yield answer

    answer = "".join(answer_chunks)
    agent_message = Message(
        conversation_id=conversation_id,
        role="agent",
        content=answer,
        agent_mode=agent_mode,
    )
    db.add(agent_message)
    db.commit()
    db.refresh(agent_message)
