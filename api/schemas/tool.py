"""工具列表响应模型。"""

from typing import Optional

from pydantic import BaseModel


class ToolInfo(BaseModel):
    name: str
    description: Optional[str] = None
