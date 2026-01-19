"""工具列表路由：展示当前可用的本地工具。"""

from typing import List

from fastapi import APIRouter, Depends

from api.core.security import get_current_user
from api.repositories.models import User
from api.schemas import ToolInfo
from api.services.tool_service import list_tools

router = APIRouter(prefix="/api/tools", tags=["tools"])


@router.get("", response_model=List[ToolInfo])
def list_tools_endpoint(current_user: User = Depends(get_current_user)):
    """返回工具名称与描述列表。"""
    return list_tools()
