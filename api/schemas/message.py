"""消息相关的请求/响应模型。"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    content: str
    agent_mode: str = Field(..., description="react | plan_execute | codeact | mcp")


class MessageResponse(BaseModel):
    message_id: str
    conversation_id: str
    agent_mode: str
    answer: str


class MessageListItem(BaseModel):
    id: str
    role: str
    content: str
    agent_mode: str
    created_at: Optional[datetime]

    class Config:
        orm_mode = True


class MessagesPage(BaseModel):
    items: List[MessageListItem]
    total: int
