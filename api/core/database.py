"""数据库核心模块：配置 SQLite 引擎、Session 工厂，以及统一的 DB 依赖。"""

import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////data/wdk/wdk_agent/database/wdk_agent.db")

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


@event.listens_for(engine, "connect")
def enable_foreign_keys(dbapi_connection, connection_record):
    """启用 SQLite 外键约束，确保级联删除生效。"""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def get_db():
    """FastAPI 依赖：提供一个生命周期内复用的数据库会话。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
