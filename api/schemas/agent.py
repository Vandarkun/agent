"""Agent 相关的响应模型。"""

from typing import Optional

from pydantic import BaseModel


class AgentInfo(BaseModel):
    """单个 Agent 的信息。"""

    mode: str
    """Agent 模式标识，用于 API 调用"""

    name: str
    """Agent 显示名称"""

    description: Optional[str] = None
    """Agent 功能描述"""


class AgentList(BaseModel):
    """Agent 列表响应。"""

    agents: list[AgentInfo]
    """可用 Agent 列表"""
