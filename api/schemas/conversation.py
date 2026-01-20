"""会话相关的请求/响应模型。"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ConversationCreate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=128)


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: Optional[str]
    created_at: Optional[datetime]
