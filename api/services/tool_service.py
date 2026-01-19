"""工具服务层：提供工具清单聚合。"""

from typing import List

from agentchat.tools import AgentTools
from api.schemas import ToolInfo


def list_tools() -> List[ToolInfo]:
    """遍历 AgentTools 集合并返回工具名称与描述。"""
    tools = []
    for tool in AgentTools:
        # BaseTool 一定有 name 属性，__name__ 在对象上可能不存在，因此分开取值避免 AttributeError
        name = getattr(tool, "name", None) or getattr(tool, "__name__", tool.__class__.__name__)
        description = getattr(tool, "description", None) or getattr(tool, "__doc__", None)
        tools.append(
            ToolInfo(
                name=name,
                description=description,
            )
        )
    return tools
