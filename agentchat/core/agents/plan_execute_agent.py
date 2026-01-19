import asyncio
import json
from typing import Any, Awaitable, Callable, Dict, List, Optional

from loguru import logger
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool
from pydantic import BaseModel

from agentchat.core.agents.structured_response_agent import StructuredResponseAgent
from agentchat.core.models.manager import ModelManager
from agentchat.prompts.chat import FIX_JSON_PROMPT, PLAN_CALL_TOOL_PROMPT, SINGLE_PLAN_CALL_PROMPT
from agentchat.schema.chat import PlanToolFlow
from agentchat.services.mcp.manager import MCPManager
from agentchat.utils.convert import convert_mcp_config

class PlanExecuteAgent:
    """
    基于“规划-执行”范式的对话式代理：先生成计划，再按计划调用工具或函数。

    设计思路：先用规划模型解析用户需求，输出结构化的执行步骤；再用工具调用模型按步骤挑选并调用工具；支持插件函数与 MCP (Model Context Protocol) 工具，并在执行过程中提供实时事件与错误处理。

    主要特性：
        - 先规划后执行：减少盲目调用工具
        - 同时支持同步/异步函数工具
        - MCP 工具集成，运行时动态装载
        - 流式输出，便于前端实时展示
        - 自动尝试修复模型返回的畸形 JSON
        - 详细日志与错误兜底

    关键属性：
        user_id: 用户标识，用于个性化配置
        tools: 预置的工具列表（BaseTool 子类或 LangChain 工具）
        mcp_servers: MCP 服务器配置，动态加载远端工具
        mcp_manager/mcp_tools: MCP 管理器与运行时加载的工具
        conversation_model: 用于纯对话回复的模型
        tool_call_model: 用于发起工具调用的模型

    使用示例（伪代码）：
        ```python
        @tool
        def get_weather(city: str) -> str:
            return f"Weather in {city}: 22°C, sunny"

        agent = PlanExecuteAgent(user_id="u1", tools=[get_weather])
        messages = [HumanMessage(content="东京天气怎样？")]
        resp = await agent.ainvoke(messages)
        print(resp)
        ```

    注意事项：
        - 工具需提供清晰描述/参数，便于模型规划
        - MCP 服务需可用且参数配置正确
        - 规划阶段先行，工具阶段依赖规划结果
    """
    def __init__(self,
                 user_id: str,
                 tools: List[BaseTool],
                 mcp_servers: Optional[List[Dict[str, Any]]] = None,
                 user_config_provider: Optional[Callable[[str, Optional[str]], Awaitable[Dict[str, Any]]]] = None):
        self.tools = tools
        self.user_id = user_id
        self.mcp_servers = mcp_servers or []
        self.user_config_provider = user_config_provider
        self.mcp_manager: Optional[MCPManager] = None

        self.mcp_tools: List[BaseTool] = []
        self.conversation_model = ModelManager.get_conversation_model()
        self.tool_call_model = ModelManager.get_tool_invocation_model()

    async def setup_mcp_tools(self):
        """加载 MCP 工具：按需创建管理器并异步拉取远端工具列表。"""
        if self.mcp_servers and not self.mcp_manager:
            self.mcp_manager = MCPManager(convert_mcp_config(self.mcp_servers))

        if self.mcp_manager:
            self.mcp_tools = await self.mcp_manager.get_mcp_tools()
        else:
            self.mcp_tools = []

        return self.mcp_tools

    async def _plan_agent_actions(self, messages: List[BaseMessage]):
        """
        规划阶段：
        1) 把可用工具的参数信息注入提示，便于模型挑选。
        2) 调用 StructuredResponseAgent 生成结构化计划 JSON。
        3) 若返回的 JSON 畸形，尝试通过对话模型修复。
        """
        structured_response_agent = StructuredResponseAgent(response_format=PlanToolFlow)

        call_messages: List[BaseMessage] = []
        call_messages.extend(messages)

        # 将所有工具的参数模式拼接，供规划提示词参考
        tools_info = "\n\n".join(self._format_tool_schema(tool) for tool in (self.tools + self.mcp_tools))
        prompt_text = PLAN_CALL_TOOL_PROMPT.replace("{user_query}", messages[-1].content).replace(
            "{tools_info}", tools_info
        )

        if isinstance(call_messages[0], SystemMessage):
            call_messages[0] = SystemMessage(content=prompt_text)
        else:
            call_messages.insert(0, SystemMessage(content=prompt_text))

        # 规划阶段：生成结构化的计划 JSON
        response = structured_response_agent.get_structured_response(call_messages)

        # response may already be a dict/BaseModel per ToolStrategy
        if isinstance(response, BaseModel):
            content = response.model_dump()
        elif isinstance(response, dict):
            content = response
        else:
            try:
                content = json.loads(str(response))
            except Exception as err:
                fix_message = HumanMessage(
                    content=FIX_JSON_PROMPT.format(json_content=str(response), json_error=str(err)))
                fix_response = await self.conversation_model.ainvoke([fix_message])
                try:
                    content = json.loads(fix_response.content)
                except Exception as fix_err:
                    raise ValueError(fix_err)

        self.agent_plans = content
        return content

    async def _execute_agent_actions(self, agent_plans):
        """
        执行阶段（按规划逐步推进）：
        1) 为工具调用模型绑定所有工具（本地 + MCP）。
        2) 遍历规划步骤，逐步把已执行结果作为上下文喂给模型。
        3) 如果当前步骤产生 tool_calls，交给上层继续执行；否则给出占位反馈并进入下一步。
        """
        # 兼容不同格式的计划：可能包含 root，或直接是步骤字典。
        if isinstance(agent_plans, BaseModel):
            plans = agent_plans.model_dump()
        else:
            plans = agent_plans

        plans = plans.get("root", plans) if isinstance(plans, dict) else plans
        if not isinstance(plans, dict):
            logger.error(f"Invalid plans format: {plans}")
            return []

        tool_call_model = self.tool_call_model.bind_tools(self.tools + self.mcp_tools)

        tool_results: List[BaseMessage] = []
        for step, plan in plans.items():
            # plan 可能是列表或单个 dict，统一成列表
            if isinstance(plan, dict):
                plan_list = [plan]
            else:
                plan_list = plan or []

            if plan_list and plan_list[0].get("tool_name") == "call_user":
                tool_results.append(AIMessage(content=str(plan_list)))
                break

            # 针对当前步骤构造一次性的调用提示
            call_tool_messages = []
            system_message = HumanMessage(content=SINGLE_PLAN_CALL_PROMPT.format(plan_actions=str(plan_list)))
            call_tool_messages.append(system_message)
            call_tool_messages.extend(tool_results)

            response = await tool_call_model.ainvoke(call_tool_messages)
            if response.tool_calls:
                # 直接执行工具，并把模型回复和工具结果都纳入上下文
                tool_messages = await self._execute_tool(response)
                tool_results.append(response)
                tool_results.extend(tool_messages)
                continue
            else:
                # 没有可用工具时给出占位回复，继续后续步骤
                ai_message = AIMessage(content="No available tools found")
                tool_messages = await self._execute_tool(ai_message)
                tool_results.append(ai_message)
                tool_results.extend(tool_messages)

        return tool_results

    async def _execute_tool(self, message: AIMessage):
        """具体工具执行子流程：遍历 tool_calls，按名称找到对应工具并执行。"""
        tool_calls = message.tool_calls
        tool_messages: List[BaseMessage] = []

        for tool_call in tool_calls:
            is_mcp_tool, use_tool = self._find_tool_use(tool_call["name"])
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_call_id = tool_call["id"]

            try:
                if use_tool is None:
                    raise ValueError(f"Tool {tool_name} not found")

                # 优先使用工具的异步协程接口（MCP 工具多为异步）
                if hasattr(use_tool, "coroutine") and use_tool.coroutine is not None:
                    if is_mcp_tool and self.user_config_provider:
                        # MCP 工具可按用户注入个性化参数
                        personal_config = await self.user_config_provider(
                            self.user_id, self._get_mcp_id_by_tool(tool_name)
                        )
                        tool_args.update(personal_config or {})

                    tool_result, _ = await use_tool.coroutine(**tool_args)
                else:
                    # 普通函数工具用线程池避免阻塞事件循环
                    tool_result = await asyncio.to_thread(use_tool.func, **tool_args)

                tool_messages.append(
                    ToolMessage(content=tool_result, name=tool_name, tool_call_id=tool_call_id))
                logger.info(f"Plugin Tool {tool_name}, Args: {tool_args}, Result: {tool_result}")

            except Exception as err:
                logger.error(f"Plugin Tool {tool_name} Error: {str(err)}")
                tool_messages.append(
                    ToolMessage(content=str(err), name=tool_name, tool_call_id=tool_call_id))

        return tool_messages

    async def astream(self, messages: List[BaseMessage]):
        """流式调用：先装载 MCP 工具 -> 规划 -> 执行 -> 对话流式输出。"""
        await self.setup_mcp_tools()

        agent_plans = await self._plan_agent_actions(messages)
        if agent_plans:
            tool_results = await self._execute_agent_actions(agent_plans)
        else:
            tool_results = []

        messages.extend(tool_results)
        try:
            response_content = ""
            async for chunk in self.conversation_model.astream(messages):
                if chunk.content:
                    response_content += chunk.content
                    yield {
                        "content": chunk.content
                    }
        except Exception as err:
            logger.error(f"LLM stream error: {err}")


    async def ainvoke(self, messages: List[BaseMessage]):
        """一次性调用：同样先规划后执行，最后返回完整回复文本。"""
        await self.setup_mcp_tools()

        agent_plans = await self._plan_agent_actions(messages)
        if agent_plans:
            tool_results = await self._execute_agent_actions(agent_plans)
        else:
            tool_results = []

        # 确保所有消息都是 BaseMessage，否则转为 HumanMessage
        safe_messages: List[BaseMessage] = []
        for m in list(messages) + list(tool_results):
            if isinstance(m, BaseMessage):
                safe_messages.append(m)
            else:
                safe_messages.append(HumanMessage(content=str(m)))

        response = await self.conversation_model.ainvoke(safe_messages)
        return response.content

    def _get_mcp_id_by_tool(self, tool_name):
        """根据工具名查找其所属的 MCP 服务 ID（用于注入个性化配置）。"""
        for server in self.mcp_servers:
            tool_list = server.get("tools") or []
            param_tools = [param.get("name") for param in server.get("params", []) if isinstance(param, dict)]
            if tool_name in tool_list or tool_name in param_tools:
                return server.get("mcp_server_id") or server.get("server_name")
        return None

    def _find_tool_use(self, tool_name):
        """在本地工具与 MCP 工具中按名称查找，返回 (是否MCP, 工具实例或 None)。"""
        for tool in self.tools:
            if tool.name == tool_name:
                return False, tool
        for tool in self.mcp_tools:
            if tool.name == tool_name:
                return True, tool
        return False, None

    def _format_tool_schema(self, tool: BaseTool) -> str:
        """Return a readable schema string for a tool's args."""
        schema = getattr(tool, "args_schema", None)
        if schema is None:
            return tool.name

        # args_schema can be a BaseModel subclass or instance
        if isinstance(schema, type) and issubclass(schema, BaseModel):
            try:
                return str(schema.model_json_schema())
            except Exception:
                try:
                    return str(schema.model_fields)
                except Exception:
                    return tool.name
        if isinstance(schema, BaseModel):
            try:
                return str(schema.model_dump())
            except Exception:
                return str(schema)
        return str(schema)
