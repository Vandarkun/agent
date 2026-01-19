"""认证服务层：处理用户校验与 token 签发逻辑。"""

from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from api.core.security import create_access_token, verify_password, get_password_hash
from api.repositories.models import User, UserSession
from api.schemas import TokenResponse


def authenticate_user(db: Session, username: str, password: str) -> TokenResponse:
    """校验用户名密码并返回新生成的 JWT。"""
    user: User | None = (
        db.query(User).filter(User.username == username, User.is_active.is_(True)).first()
    )
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    # 单用户单会话：登录前清理旧 session
    db.query(UserSession).filter(UserSession.user_id == user.id).delete()

    token, expires_at = create_access_token(user.id)
    session = UserSession(user_id=user.id, access_token=token, expires_at=expires_at)
    db.add(session)
    db.commit()

    return TokenResponse(access_token=token, expires_at=expires_at)


def ensure_default_user(db: Session, username: str = "123", password: str = "123") -> None:
    """确保存在一个默认账号（用户名/密码均为123），仅在未创建时插入。"""
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        return
    user = User(username=username, password_hash=get_password_hash(password), is_active=True)
    db.add(user)
    db.commit()
