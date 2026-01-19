"""认证相关的请求/响应模型。"""

from datetime import datetime

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., max_length=64)
    password: str


class TokenResponse(BaseModel):
    access_token: str
    expires_at: datetime

    class Config:
        orm_mode = True
