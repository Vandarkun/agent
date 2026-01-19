from pydantic import BaseModel
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy

from agentchat.core.models.manager import ModelManager


class StructuredResponseAgent:
    """包装 LangChain 的 structured output 能力，用指定 schema 返回结构化结果。

    使用场景：
        - 需要让模型严格按给定 Pydantic/BaseModel/TypedDict 格式输出时。
        - 作为规划阶段或解析阶段的子组件，保证下游拿到稳定结构。
    """

    def __init__(self, response_format):
        self.response_format = response_format
        self.structured_agent = self._create_structured_agent()

    def _create_structured_agent(self):
        """基于当前对话模型创建一个带 ToolStrategy 的代理，强制结构化输出。"""
        return create_agent(
            model=ModelManager.get_conversation_model(),
            response_format=ToolStrategy(self.response_format)
        )

    def get_structured_response(self, messages):
        """执行一次调用，返回解析后的结构化字段 `structured_response`。"""
        result = self.structured_agent.invoke({"messages": messages})
        return result["structured_response"]