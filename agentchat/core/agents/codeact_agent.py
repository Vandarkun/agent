import inspect
from typing import List
from typing import Any, Awaitable, Callable, Optional, Sequence, Type, TypeVar, Union, Dict
from langgraph.types import Command
from langchain_core.messages import BaseMessage
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import StructuredTool, BaseTool
from langchain_core.tools import tool as create_tool
from langgraph.graph import END, START, MessagesState, StateGraph

from agentchat.core.models.manager import ModelManager
from agentchat.services.sandbox import PyodideSandbox
from agentchat.services.mcp.manager import MCPManager
from agentchat.utils.convert import convert_mcp_config
from agentchat.utils.extract import extract_and_combine_codeblocks

# 定义评估函数类型别名
# EvalFunction: 同步函数，接收代码字符串和本地变量字典，返回 (执行输出, 新增变量字典)
EvalFunction = Callable[[str, dict[str, Any]], tuple[str, dict[str, Any]]]
# EvalCoroutine: 异步函数版本，接收代码字符串和本地变量字典，返回 (执行输出, 新增变量字典)
EvalCoroutine = Callable[[str, dict[str, Any]], Awaitable[tuple[str, dict[str, Any]]]]

class CodeActState(MessagesState):
    """CodeAct 智能体的状态定义。"""

    script: Optional[str]
    """即将被执行的 Python 代码脚本。"""
    context: dict[str, Any]
    """包含执行上下文的字典，存储可用的工具函数和执行过程中定义的变量。"""


StateSchema = TypeVar("StateSchema", bound=CodeActState)
StateSchemaType = Type[StateSchema]


def create_default_prompt(tools: list[StructuredTool], base_prompt: Optional[str] = None):
    """为 CodeAct 智能体创建默认系统提示词。
    
    参数:
        tools: 智能体可用的工具列表。
        base_prompt: 可选的基础提示词前缀。
    """
    tools = [t if isinstance(t, StructuredTool) else create_tool(t) for t in tools]
    prompt = f"{base_prompt}\n\n" if base_prompt else ""
    prompt += """You will be given a task to perform. You should output either
- a Python code snippet that provides the solution to the task, or a step towards the solution. Any output you want to extract from the code should be printed to the console. Code should be output in a fenced code block.
- text to be shown directly to the user, if you want to ask for more information or provide the final answer.

In addition to the Python Standard Library, you can use the following functions:
"""

    for tool in tools:
        prompt += f'''
def {tool.name}{str(inspect.signature(tool.func))}:
    """{tool.description}"""
    ...
'''

    prompt += """

Variables defined at the top level of previous code snippets can be referenced in your code.

Reminder: use Python code snippets to call tools"""
    return prompt


class CodeActAgent:
    """CodeActAgent 类实现了 CodeAct (Code Action) 智能体逻辑。
    它采用 LangGraph 管理 '模型生成代码 -> 沙箱执行代码 -> 结果反馈模型' 的循环流程。
    """

    def __init__(
        self,
        tools,
        user_id,
        mcp_servers: Optional[List[Dict[str, Any]]] = None,
        user_config_provider: Optional[Callable] = None
    ):
        """初始化智能体。

        参数:
            tools: 智能体可用的工具列表。
            user_id: 当前用户的唯一标识符。
            mcp_servers: MCP 服务器配置列表。
            user_config_provider: 用户配置提供函数，用于 MCP 工具鉴权。
        """
        self.tools = tools
        self.user_id = user_id
        self.mcp_servers = mcp_servers or []
        self.user_config_provider = user_config_provider

        # MCP 管理器和工具
        self.mcp_manager: Optional[MCPManager] = None
        self.mcp_tools: List[BaseTool] = []

        # 获取预配置的代码生成模型
        self.coder_model = ModelManager.get_conversation_model()

        self.setup_codeact_agent()

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

    def setup_codeact_agent(self):
        """配置底层的沙箱环境和编译 LangGraph 流程。"""
        # 初始化沙箱环境，并允许其进行网络请求
        sandbox = PyodideSandbox(allow_net=True)
        # 创建基于 Pyodide 的评估函数
        eval_fn = self.create_pyodide_eval_fn(sandbox)
        # 构建并编译状态机图 (StateGraph)
        self.codeact_agent = self.create_codeact_agent(self.coder_model, self.tools, eval_fn)


    async def astream(self, messages: List[BaseMessage]):
        """异步流式输出智能体生成的响应和过程消息。

        参数:
            messages: 初始对话历史消息。
        """
        # 自动加载 MCP 工具
        await self.setup_mcp_tools()

        async for typ, chunk in self.codeact_agent.astream(
                {"messages": messages},
                stream_mode=["values", "messages"],
        ):
            if typ == "messages":
                # 返回消息内容块
                yield chunk[0].content
            elif typ == "values":
                # 返回当前的状态更新
                yield chunk

    async def ainvoke(self, messages: List[BaseMessage]) -> str:
        """一次性执行完整的 CodeAct 流程并返回最终回复。

        参数:
            messages: 初始对话历史消息。

        返回:
            str: 最终的回复内容。
        """
        # 自动加载 MCP 工具
        await self.setup_mcp_tools()

        full_response = []
        final_state = None

        async for chunk in self.astream(messages):
            if isinstance(chunk, dict):
                # 状态更新
                final_state = chunk
            elif isinstance(chunk, str):
                # 内容流
                full_response.append(chunk)

        # 返回完整响应
        result = "".join(full_response).strip()
        return result if result else "代码执行完成，无输出内容。"

    def create_pyodide_eval_fn(self, sandbox: PyodideSandbox) -> EvalCoroutine:
        """创建一个评估函数，用于在 PyodideSandbox 中安全地执行生成的 Python 代码。
        
        该函数负责：
        1. 注入现有的上下文变量和工具函数。
        2. 将生成的代码块包装在 execute() 函数中运行，以捕获局部变量。
        3. 提取执行结果中的标准输出 (stdout) 和新增变量。
        """

        async def async_eval_fn(
                code: str, _locals: dict[str, Any]
        ) -> tuple[str, dict[str, Any]]:
            # 构造包装代码，将模型生成的代码放入 try-except 块中运行
            # 缩进处理：将传入的代码每一行都进行 8 空格缩进，以符合 Python 的缩进规范
            wrapper_code = f"""
def execute():
    try:
        # 运行 LLM 提供的代码
{"\n".join(" " * 8 + line for line in code.strip().split("\n"))}
        return locals()
    except Exception as e:
        return {{"error": str(e)}}

execute()
    """
            # 初始化运行环境的内容
            context_setup = ""
            for key, value in _locals.items():
                if callable(value):
                    # 如果是工具函数，通过 inspect 获取其源代码以便在沙箱内定义
                    src = inspect.getsource(value)
                    context_setup += f"\n{src}"
                else:
                    # 如果是普通变量，使用 repr 进行序列化
                    context_setup += f"\n{key} = {repr(value)}"

            try:
                # 在沙箱中执行完整代码
                response = await sandbox.execute(
                    code=context_setup + "\n\n" + wrapper_code,
                )
                # 检查沙箱执行的 stderr (通常指示环境或沙箱层面的错误)
                if response.stderr:
                    return f"Error during execution: {response.stderr}", {}

                # 提取标准输出流的内容
                output = (
                    response.stdout
                    if response.stdout
                    else "<Code ran, no output printed to stdout>"
                )
                result = response.result

                # 检查执行结果中是否包含由 wrapper_code 捕获的运行错误
                if isinstance(result, dict) and "error" in result:
                    return f"Error during execution: {result['error']}", {}

                # 对比执行前后的局部变量，提取出 LLM 新定义的变量（排除私有变量）
                new_vars = {
                    k: v
                    for k, v in result.items()
                    if k not in _locals and not k.startswith("_")
                }
                return output, new_vars

            except Exception as e:
                return f"Error during PyodideSandbox execution: {repr(e)}", {}

        return async_eval_fn


    def create_codeact_agent(
        self,
        model: BaseChatModel,
        tools: Sequence[Union[StructuredTool, Callable]],
        eval_fn: Union[EvalFunction, EvalCoroutine],
        *,
        prompt: Optional[str] = None,
        state_schema: StateSchemaType = CodeActState,
    ) -> StateGraph:
        """创建一个实现 CodeAct 架构的智能体流程图。

        参数:
            model: 用于生成代码或对话的语言模型。
            tools: 可用的工具列表（函数或 StructuredTool）。
            eval_fn: 执行代码的评估函数（同步或异步）。
            prompt: 可选的系统提示词，默认为 create_default_prompt 生成的提示。
            state_schema: 状态架构类，默认为 CodeActState。

        返回:
            一个编译好的 StateGraph (LangGraph)。
        """
        tools = [t if isinstance(t, StructuredTool) else create_tool(t) for t in tools]

        if prompt is None:
            prompt = create_default_prompt(tools)

        # 准备沙箱上下文中可调用的工具函数
        tools_context = {tool.name: tool.func for tool in tools}

        def call_model(state: StateSchema) -> Command:
            """调用语言模型来决定下一步操作：是编写代码还是直接回答。"""
            # 构建消息序列，包含系统角色提示词
            messages = [{"role": "system", "content": prompt}] + state["messages"]
            response = model.invoke(messages)
            # 从模型返回的内容中提取所有的 Python 代码块并合并为一个脚本
            code = extract_and_combine_codeblocks(response.content)
            if code:
                # 如果检测到代码块，则跳转到 sandbox 节点，并将脚本更新到状态
                return Command(goto="sandbox", update={"messages": [response], "script": code})
            else:
                # 如果没有代码块，模型可能已经给出了最终答案或正在对话，此时退出循环
                return Command(update={"messages": [response], "script": None})

        # 判断评估函数是否为异步函数，从而定义相应的图节点逻辑
        if inspect.iscoroutinefunction(eval_fn):

            async def sandbox(state: StateSchema):
                """异步沙箱节点：负责代码执行并将结果反馈回模型。"""
                existing_context = state.get("context", {})
                # 合并现有上下文和预定义工具函数
                context = {**existing_context, **tools_context}
                # 在沙箱中执行脚本
                output, new_vars = await eval_fn(state["script"], context)
                # 更新上下文，包含执行后新定义的变量
                new_context = {**existing_context, **new_vars}
                # 将代码输出结果包装成 user 消息，作为 LLM 的下一步观测输入
                return {
                    "messages": [{"role": "user", "content": output}],
                    "context": new_context,
                }
        else:

            def sandbox(state: StateSchema):
                """同步沙箱节点逻辑。"""
                existing_context = state.get("context", {})
                context = {**existing_context, **tools_context}
                # 在沙箱中执行脚本
                output, new_vars = eval_fn(state["script"], context)
                new_context = {**existing_context, **new_vars}
                return {
                    "messages": [{"role": "user", "content": output}],
                    "context": new_context,
                }

        # 初始化图
        agent = StateGraph(state_schema)
        # 添加核心节点
        # call_model 节点负责决策，destinations 定义了它可以分支到的路径
        agent.add_node(call_model, destinations=(END, "sandbox"))
        # sandbox 节点负责执行
        agent.add_node(sandbox)
        
        # 配置流程连线
        agent.add_edge(START, "call_model")    # 从起点开始
        agent.add_edge("sandbox", "call_model") # 执行完代码后再回到模型进行观察和决策
        
        # 编译并返回最终可执行的图
        return agent.compile()
