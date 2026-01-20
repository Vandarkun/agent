"""安全模块：封装 JWT、密码哈希和当前用户解析的通用逻辑。"""

import os
from datetime import datetime, timedelta, timezone
from typing import Tuple

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from api.core.database import get_db
from api.repositories.models import User, UserSession
from api.utils.current_time import get_current_datetime

SECRET_KEY = os.getenv("JWT_SECRET", "dev-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """校验明文密码与哈希是否匹配。"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """生成密码哈希，供预置用户入库时使用。"""
    return pwd_context.hash(password)


def create_access_token(user_id: str) -> Tuple[str, datetime]:
    """生成短期有效的 JWT（使用 UTC，带时区），返回 token 与过期时间。"""
    now = get_current_datetime()
    expires_at = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": user_id, "exp": expires_at}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, expires_at


def _normalize_dt(value: datetime) -> datetime:
    """将 datetime 转为带 UTC 时区，便于安全比较。"""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """解析并验证请求头中的 JWT，返回当前活跃用户。"""
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing credentials")

    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            print(f"=== DEBUG: JWT decoded but 'sub' field is missing. Payload: {payload}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: missing user_id in payload. Please login again.")
    except jwt.PyJWTError as e:
        print(f"=== DEBUG: JWT decode error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # Debug: 检查数据库中的所有session
    all_sessions = db.query(UserSession).all()
    print(f"=== DEBUG: Total sessions in DB: {len(all_sessions)}")
    for s in all_sessions:
        print(f"  - Session ID: {s.id}, User ID: {s.user_id}, Token: {s.access_token[:50]}..., Revoked: {s.revoked_at}")

    print(f"=== DEBUG: Looking for token: {token[:50]}...")
    print(f"=== DEBUG: Looking for user_id: {user_id}")

    session = (
        db.query(UserSession)
        .filter(
            UserSession.access_token == token,
            UserSession.user_id == user_id,
            UserSession.revoked_at.is_(None),
        )
        .first()
    )

    if not session:
        print(f"=== DEBUG: Session NOT FOUND!")
        print(f"=== DEBUG: Checking by token only...")
        session_by_token = db.query(UserSession).filter(UserSession.access_token == token).first()
        if session_by_token:
            print(f"=== DEBUG: Found by token! user_id={session_by_token.user_id}, revoked_at={session_by_token.revoked_at}")
        else:
            print(f"=== DEBUG: Not found by token either!")

        print(f"=== DEBUG: Checking by user_id only...")
        sessions_by_user = db.query(UserSession).filter(UserSession.user_id == user_id).all()
        print(f"=== DEBUG: Found {len(sessions_by_user)} sessions for user_id")
        for s in sessions_by_user:
            print(f"  - Token matches: {s.access_token == token}")

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired or revoked")

    now_utc = get_current_datetime()
    session_exp = _normalize_dt(session.expires_at)
    if session_exp < now_utc:
        print(session_exp, now_utc)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired or revoked")

    user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    return user
