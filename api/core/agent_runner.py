"""Agent 调度器：根据 agent_mode 分发到不同智能体实现。"""

from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status
from langchain_core.messages import HumanMessage

from agentchat.core.agents.codeact_agent import CodeActAgent
from agentchat.core.agents.mcp_agent import MCPAgent, MCPConfig
from agentchat.core.agents.plan_execute_agent import PlanExecuteAgent
from agentchat.core.agents.react_agent import ReactAgent
from agentchat.core.models.manager import ModelManager
from agentchat.tools import AgentTools

SUPPORTED_AGENT_MODES = {"react", "plan_execute", "codeact", "mcp"}


async def invoke_agent(
    agent_mode: str,
    content: str,
    user_id: str,
    mcp_servers: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """统一入口：根据模式创建对应 Agent 执行用户消息，返回最终回复。"""
    if agent_mode not in SUPPORTED_AGENT_MODES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported agent mode")

    if agent_mode == "react":
        model = ModelManager.get_tool_invocation_model()
        agent = ReactAgent(model=model, tools=AgentTools, mcp_servers=mcp_servers or [])
        return await agent.ainvoke([HumanMessage(content=content)])

    if agent_mode == "plan_execute":
        agent = PlanExecuteAgent(user_id=user_id, tools=AgentTools, mcp_servers=mcp_servers or [])
        return await agent.ainvoke([HumanMessage(content=content)])

    if agent_mode == "codeact":
        agent = CodeActAgent(tools=AgentTools, user_id=user_id, mcp_servers=mcp_servers or [])
        return await agent.ainvoke([HumanMessage(content=content)])

    if not mcp_servers:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MCP agent requires configuration")

    config = mcp_servers[0]
    mcp_agent = MCPAgent(mcp_config=MCPConfig(**config), user_id=user_id)
    await mcp_agent.init_mcp_agent()
    result = await mcp_agent.ainvoke([HumanMessage(content=content)])

    if isinstance(result, list):
        return "\n".join([getattr(msg, "content", str(msg)) for msg in result])
    return str(result)
