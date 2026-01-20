"""Agent 列表路由：展示当前可用的 Agent 类型。"""

from fastapi import APIRouter, Depends

from api.core.security import get_current_user
from api.repositories.models import User
from api.schemas import AgentInfo
from api.services.agent_service import list_agents

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("", response_model=list[AgentInfo])
def list_agents_endpoint(current_user: User = Depends(get_current_user)):
    """返回所有可用的 Agent 类型及其描述。"""
    return list_agents()
