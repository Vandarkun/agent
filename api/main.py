"""FastAPI 入口：加载配置、初始化表结构并挂载路由。"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agentchat.settings import initialize_app_settings

from api.core.database import Base, SessionLocal, engine
from api.repositories import models as _  # noqa: F401 ensure models are registered
from api.routers.agents import router as agents_router
from api.routers.auth import router as auth_router
from api.routers.conversations import router as conversations_router
from api.routers.tools import router as tools_router
from api.routers.test import router as test_router
from api.services.auth_service import ensure_default_user


app = FastAPI(title="WDK Agent API")

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源（开发环境）
    allow_credentials=True,  # 允许携带 Cookie
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)


@app.on_event("startup")
async def startup_event():
    """应用启动时加载配置并创建表。"""
    await initialize_app_settings()
    Base.metadata.create_all(bind=engine)
    # 初始化默认账户（用户名/密码：123），仅在不存在时创建
    db = SessionLocal()
    try:
        ensure_default_user(db)
    finally:
        db.close()


app.include_router(auth_router)
app.include_router(agents_router)
app.include_router(conversations_router)
app.include_router(tools_router)
app.include_router(test_router)
