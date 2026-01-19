"""认证路由：处理登录获取 token。"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from api.core.database import get_db
from api.schemas import LoginRequest, TokenResponse
from api.services.auth_service import authenticate_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """登录并返回 JWT 与过期时间。"""
    return authenticate_user(db=db, username=payload.username, password=payload.password)
