from loguru import logger
from typing import List, Dict, Any, AsyncGenerator, NotRequired, Union, Optional, Callable, Awaitable
from langchain_core.language_models import BaseChatModel
from langgraph.constants import START, END
from langgraph.graph import MessagesState, StateGraph
from langchain_core.tools import BaseTool
from langchain_core.messages import BaseMessage, SystemMessage, ToolMessage, AIMessageChunk, AIMessage, HumanMessage

from agentchat.prompts.chat import DEFAULT_CALL_PROMPT
from agentchat.services.mcp.manager import MCPManager
from agentchat.utils.convert import convert_mcp_config


class ReactAgentState(MessagesState):
    """
    LangGraph 状态定义，继承自 MessagesState，扩展了额外的跟踪字段。
    
    继承字段 (来自 MessagesState):
        messages (List[BaseMessage]): 完整的对话历史，包括 HumanMessage、AIMessage、ToolMessage 等
    
    扩展字段：
        tool_call_count (NotRequired[int]): 工具被调用的总次数计数器，用于追踪迭代轮次。
                                            初始值为 0，每当 execute_tool_node 完成一次工具执行后就增加 1。
                                            这个计数器帮助 Agent 识别当前是第几轮推理-行动循环。
        model_call_count (NotRequired[int]): 模型被调用的总次数计数器（目前在代码中定义但未被显式使用）。
                                             可用于未来的优化和限制（如防止无限循环）。
    
    设计目的：
        通过扩展状态，将额外的元数据（如循环计数）集成到 LangGraph 的状态管理中，
        允许节点函数根据这些信息做出更智能的决策（如显示不同的提示文本）。
    """
    tool_call_count: NotRequired[int]
    model_call_count: NotRequired[int]


class ReactAgent:
    """
    一个基于 LangGraph 的 ReAct (Reasoning and Acting) 代理的完整实现。
    
    ReAct 架构思想：
        Agent 通过一个循环工作流执行任务：
        1. 推理 (Reasoning): 调用 LLM，让其分析当前状态和可用的工具
        2. 行动 (Acting): 如果 LLM 选择了工具，则执行工具调用
        3. 观察 (Observation): 将工具执行结果反馈给 LLM
        4. 重复: LLM 根据新信息继续推理，直到决定直接回答用户
    
    主要特性：
        - 简单的流式输出：仅返回模型内容片段，便于 demo 演示
        - 灵活的工具集成：支持标准 BaseTool 以及 MCP 协议代理作为工具
        - 完整的错误处理和日志记录
    """

    def __init__(self,
                 model: BaseChatModel,
                 system_prompt: Optional[str] = None,
                 tools: List[BaseTool] = [],
                 mcp_servers: Optional[List[Dict[str, Any]]] = None,
                 user_config_provider: Optional[Callable[[str, Optional[str]], Awaitable[Dict[str, Any]]]] = None):
        """
        初始化 ReactAgent。

        参数：
            model (BaseChatModel): 语言模型实例，如 ChatOpenAI、ChatAnthropic 等。
                                  需要支持 bind_tools() 方法来将工具信息绑定到模型。
            system_prompt (Optional[str]): 系统提示词，指导 Agent 的行为。
                                          如果为 None，将使用 DEFAULT_CALL_PROMPT。
                                          在 astream 中会被自动插入为第一条 SystemMessage。
            tools (List[BaseTool]): 可用的工具列表，Agent 可以在推理时调用这些工具。
                                    默认为空列表。
            mcp_servers (Optional[List[Dict[str, Any]]]): MCP 服务器配置列表。
            user_config_provider (Optional[Callable]): 用户配置提供函数，用于 MCP 工具鉴权。

        初始化过程：
            - 保存模型、提示词和工具列表
            - 创建 mcp_agent_as_tools 列表，用于后续动态添加 MCP 代理作为工具
            - 设置 self.graph 为 None，采用延迟初始化模式（在首次 astream 时初始化）
        """
        self.model = model
        self.system_prompt = system_prompt
        self.tools = tools
        self.mcp_servers = mcp_servers or []
        self.user_config_provider = user_config_provider
        self.user_id: Optional[str] = None  # 可选的用户标识

        # MCP 管理器和工具
        self.mcp_manager: Optional[MCPManager] = None
        self.mcp_tools: List[BaseTool] = []

        # 用于集成其他代理作为工具，支持 Agent 的递归组合
        self.mcp_agent_as_tools: List[BaseTool] = []

        # LangGraph 实例，采用延迟初始化以提高启动速度
        self.graph: Optional[StateGraph] = None

    async def setup_mcp_tools(self) -> List[BaseTool]:
        """加载 MCP 工具：按需创建管理器并异步拉取远端工具列表。

        返回:
            List[BaseTool]: 加载的 MCP 工具列表
        """
        if self.mcp_servers and not self.mcp_manager:
            self.mcp_manager = MCPManager(convert_mcp_config(self.mcp_servers))

        if self.mcp_manager:
            self.mcp_tools = await self.mcp_manager.get_mcp_tools()
        else:
            self.mcp_tools = []

        return self.mcp_tools

    def _prepare_messages(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        """Ensure we have a SystemMessage and a copy of the history to work with."""
        if not messages or not isinstance(messages[-1], (HumanMessage, AIMessage, ToolMessage)):
            raise ValueError("messages must end with a HumanMessage, AIMessage, or ToolMessage")

        prepared = list(messages)
        if not any(isinstance(m, SystemMessage) for m in prepared):
            prompt = self.system_prompt or DEFAULT_CALL_PROMPT
            prepared.insert(0, SystemMessage(prompt))

        return prepared

    async def _init_agent(self):
        """
        延迟初始化 LangGraph 工作流，确保在首次调用 astream 时设置好。
        
        设计模式：延迟初始化（Lazy Initialization）
            - 优点：加快 Agent 对象的创建速度，只在真正需要时才初始化复杂的图结构
            - 确保 _setup_react_graph 中的异步操作只执行一次
        
        触发时机：
            在 astream 方法中首次被调用，如果 self.graph 为 None，
            则调用 _setup_react_graph 来构建 LangGraph 工作流。
        """
        if self.graph is None:
            self.graph = await self._setup_react_graph()

    def get_tool_by_name(self, tool_name: str) -> Optional[BaseTool]:
        """
        根据工具名称查找并返回对应的工具实例。
        
        参数：
            tool_name (str): 要查找的工具名称，必须与工具的 name 属性完全匹配
        
        返回：
            Optional[BaseTool]: 找到的工具实例，如果找不到返回 None
        
        查找范围：
            - self.tools: 初始化时传入的标准工具列表
            - self.mcp_agent_as_tools: 动态添加的 MCP 代理工具列表
        
        用途：
            在 _execute_tool_node 中调用，用于根据 LLM 生成的工具调用名称
            查找实际的工具实现，以便执行工具。
        
        注意：
            如果同一个名称的工具同时存在于 self.tools 和 self.mcp_agent_as_tools 中，
            会优先返回 self.tools 中的版本（因为列表连接的顺序）。
        """
        for tool in self.tools + self.mcp_agent_as_tools:
            if tool.name == tool_name:
                return tool
        return None

    # --- LangGraph Node 定义和 Graph Setup ---

    async def _setup_react_graph(self):
        """
        设置 Agent 决策图，定义所有节点、边和条件转移逻辑。
        
        图结构：
            START
              ⬍
            call_tool_node (LLM 推理：是否需要调用工具)
              ⬍ (based on _should_continue)
            /         \\
        END       execute_tool_node (执行工具调用)
        (no tools)        ⬍
                        call_tool_node (LLM 继续推理)
        
                节点说明：
                        - call_tool_node: 调用 LLM，判断是否以及调用哪些工具。
                            输出 AIMessage，可能包含 tool_calls 或仅包含模型回复。
                        - execute_tool_node: 执行上一阶段选中的工具。
                            将工具执行结果封装成 ToolMessage，添加到状态中。
        
        边的逻辑：
            1. START → call_tool_node: 起点
            2. call_tool_node → (execute_tool_node 或 END): 根据条件转移
               - 如果 LLM 消息中有 tool_calls → execute_tool_node
               - 否则 → END（执行完成）
            3. execute_tool_node → call_tool_node: 执行工具后回到推理阶段
               形成迭代循环，直到 LLM 不需要工具。
        
        返回：
            编译好的 LangGraph，可以直接调用 astream() 方法执行。
        """
        workflow = StateGraph(ReactAgentState) # 固定写法，传入状态管理类 可以是MessagesState

        # 节点定义
        workflow.add_node("call_tool_node", self._call_tool_node)
        workflow.add_node("execute_tool_node", self._execute_tool_node)

        # 边和条件转移配置
        workflow.add_edge(START, "call_tool_node")  # 起点：从 LLM 推理开始
        workflow.add_conditional_edges("call_tool_node", self._should_continue)  # 条件转移：判断是否需要执行工具
        workflow.add_edge("execute_tool_node", "call_tool_node")  # 工具结果反馈为 LLM，可以进一步推理或直接回答

        return workflow.compile()

    # --- LangGraph Node Functions ---

    async def _should_continue(self, state: ReactAgentState) -> Union[str, Any]:
        """
        根据最新的 LLM 响应决定是否需要进入工具执行阶段。

        决策逻辑：
            - 如果最后一条消息包含非空 tool_calls，则跳转到 execute_tool_node
            - 否则跳转到 END

        参数：
            state (ReactAgentState): 当前的 Agent 状态，包括完整的消息历史和跟踪计数

        返回：
            Union[str, Any]: LangGraph 的转移目标
                          - "execute_tool_node": 执行工具
                          - END: 结束并返回答案

        注意：
            - tool_calls 由模型在 bind_tools 之后自动生成
            - 部分模型可能返回空的 tool_calls，这种情况应直接结束
        """
        last_message = state["messages"][-1]

        # 如果模型回复了内容但没有 tool_calls，则直接结束。
        if last_message.tool_calls:
            return "execute_tool_node"

        return END

    async def _call_tool_node(self, state: ReactAgentState) -> Dict[str, List[BaseMessage]]:
        """调用 LLM，判断是否需要使用工具。"""
        tool_invocation_model = self.model.bind_tools(self.tools)
        response: AIMessage = await tool_invocation_model.ainvoke(state["messages"])
        if response.tool_calls:
            tool_names = ", ".join(sorted({tool_call["name"] for tool_call in response.tool_calls}))
            logger.info(f"工具调用命中: {tool_names}")
        state["messages"].append(response)
        return {"messages": state["messages"]}

    async def _execute_tool_node(self, state: ReactAgentState) -> Dict[str, Any]:
        """执行 LLM 上一阶段选中的工具。"""
        last_message = state["messages"][-1]
        tool_calls = last_message.tool_calls
        tool_messages: List[BaseMessage] = []

        if not tool_calls:
            logger.warning("Execute tool node reached without tool calls.")
            return {"messages": state["messages"], "tool_call_count": state.get("tool_call_count", 0)}

        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_call_id = tool_call["id"]

            try:
                current_tool = self.get_tool_by_name(tool_name)

                if current_tool is None:
                    raise ValueError(f"Tool '{tool_name}' not found.")

                if current_tool.coroutine:
                    tool_result = await current_tool.ainvoke(tool_args)
                else:
                    tool_result = current_tool.invoke(tool_args)

                tool_result_str = str(tool_result)
                tool_messages.append(
                    ToolMessage(content=tool_result_str, name=tool_name, tool_call_id=tool_call_id)
                )
                logger.info(f"Tool {tool_name} executed. Args: {tool_args}, Result: {tool_result_str}")

            except Exception as err:
                error_message = f"执行工具 {tool_name} 失败: {str(err)}"
                logger.error(error_message)
                tool_messages.append(
                    ToolMessage(content=error_message, name=tool_name, tool_call_id=tool_call_id)
                )

        state["messages"].extend(tool_messages)
        new_tool_count = state.get("tool_call_count", 0) + 1
        return {"messages": state["messages"], "tool_call_count": new_tool_count}

    # --- 主调用方法 ---

    async def astream(self, messages: List[BaseMessage]) -> AsyncGenerator[str, None]:
        """简单的流式输出，只返回模型内容片段。"""
        # 自动加载 MCP 工具
        await self.setup_mcp_tools()

        prepared_messages = self._prepare_messages(messages)
        await self._init_agent()

        initial_state = {"messages": prepared_messages, "tool_call_count": 0, "model_call_count": 0}
        try:
            async for typ, token in self.graph.astream(input=initial_state, stream_mode="messages"):
                if typ == "messages":
                    message = token[0]
                    if isinstance(message, AIMessageChunk) and message.content:
                        yield message.content
                    elif isinstance(message, AIMessage) and message.content:
                        # 非流式模型时直接返回完整内容
                        yield message.content
        except Exception as err:
            logger.error(f"Agent Execution Error: {err}")

    async def ainvoke(self, messages: List[BaseMessage]) -> str:
        """一次性执行完整的 ReAct 流程并返回最终回复。"""
        # 自动加载 MCP 工具
        await self.setup_mcp_tools()

        prepared_messages = self._prepare_messages(messages)
        await self._init_agent()

        result_state = await self.graph.ainvoke(
            {"messages": prepared_messages, "tool_call_count": 0, "model_call_count": 0}
        )
        final_message = result_state["messages"][-1]
        if isinstance(final_message, AIMessage):
            return final_message.content or ""
        if isinstance(final_message, AIMessageChunk):
            return final_message.content or ""
        return str(final_message)
