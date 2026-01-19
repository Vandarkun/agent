from typing import Any, Awaitable, Callable, Dict, List, Optional

from pydantic import BaseModel

from langchain.tools import BaseTool
from langchain.agents import create_agent
from langgraph.config import get_stream_writer
from langgraph.prebuilt.tool_node import ToolCallRequest
from langchain.agents.middleware import wrap_tool_call
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from agentchat.core.models.manager import ModelManager
from agentchat.prompts.chat import CALL_END_PROMPT
from agentchat.services.mcp.manager import MCPManager
from agentchat.utils.convert import convert_mcp_config


class MCPConfig(BaseModel):
    url: str
    type: str = "sse"
    tools: List[str] = []
    server_name: str
    mcp_server_id: str


class MCPAgent:
    """
    针对单个 MCP 服务的子代理：负责加载 MCP 工具、处理鉴权参数、并用 ReAct 代理调用工具。

    主要职责：
        - 初始化 MCP 工具并绑定到工具调用模型。
        - 在工具调用前注入用户级配置（如鉴权 token）。
        - 通过中间件发送开始/结束事件，便于前端展示执行进度。
    """
    def __init__(
        self,
        mcp_config: MCPConfig,
        user_id: str,
        user_config: Optional[Dict[str, Any]] = None,
        user_config_provider: Optional[Callable[[str, str], Awaitable[Dict[str, Any]]]] = None,
    ):
        self.mcp_config = mcp_config
        self.mcp_manager = MCPManager([convert_mcp_config(mcp_config.model_dump())])

        self.user_id = user_id
        self.user_config = user_config or {}
        self.user_config_provider = user_config_provider
        self.mcp_tools: List[BaseTool] = []

        self.conversation_model = None
        self.tool_invocation_model = None

        self.react_agent = None
        self.middlewares = None

    async def init_mcp_agent(self):
        """初始化 MCP 子代理：加载工具、模型、中间件并构建 ReAct 代理。"""
        if self.mcp_config:
            self.mcp_tools = await self.setup_mcp_tools()

        await self.setup_language_model()

        self.middlewares = await self.setup_agent_middlewares()

        self.react_agent = self.setup_react_agent()

    async def emit_event(self, event):
        writer = get_stream_writer()
        writer(event)

    async def setup_language_model(self):
        # 普通对话模型（用于 ReAct LLM）
        self.conversation_model = ModelManager.get_conversation_model()

        # 工具调用模型（如需与对话模型区分，可替换为专用模型）
        self.tool_invocation_model = ModelManager.get_tool_invocation_model()

    async def setup_mcp_tools(self):
        mcp_tools = await self.mcp_manager.get_mcp_tools()
        return mcp_tools

    async def setup_agent_middlewares(self):
        """为工具调用链路包裹中间件：注入用户配置并发事件。"""

        @wrap_tool_call
        async def add_tool_call_args(
            request: ToolCallRequest,
            handler
        ):
            await self.emit_event(
                {
                    "status": "START",
                    "title": f"Sub-Agent - {self.mcp_config.server_name}执行可用工具: {request.tool_call["name"]}",
                    "messages": f"正在调用工具 {request.tool_call["name"]}..."
                }
            )

            # 针对鉴权的MCP Server需要用户的单独配置，例如飞书、邮箱
            personal_config = self.user_config
            if self.user_config_provider:
                personal_config = await self.user_config_provider(
                    self.user_id, self.mcp_config.mcp_server_id
                )

            request.tool_call["args"].update(personal_config or {})

            tool_result = await handler(request)

            await self.emit_event(
                {
                    "status": "END",
                    "title": f"Sub-Agent - {self.mcp_config.server_name}执行可用工具: {request.tool_call["name"]}",
                    "messages": f"{tool_result}"
                }
            )
            return tool_result

        return [add_tool_call_args]

    def setup_react_agent(self):
        """创建一个绑定 MCP 工具的 ReAct 代理实例。"""
        return create_agent(
            model=self.conversation_model,
            tools=self.mcp_tools,
            middleware=self.middlewares,
            system_prompt=CALL_END_PROMPT
        )


    async def ainvoke(self, messages: List[BaseMessage]) -> List[BaseMessage] | str:
        """非流式版本"""
        result = await self.react_agent.ainvoke({"messages": messages})
        messages = []

        for message in result["messages"][:-1]:
            if not isinstance(message, HumanMessage) and not isinstance(message, SystemMessage):
                messages.append(message)
        return messages
