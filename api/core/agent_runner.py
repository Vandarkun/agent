"""Agent 调度器：根据 agent_mode 分发到不同智能体实现。"""

from typing import Any, AsyncGenerator, Dict, List, Optional

from fastapi import HTTPException, status
from langchain_core.messages import HumanMessage

from agentchat.core.agents.codeact_agent import CodeActAgent
from agentchat.core.agents.mcp_agent import MCPAgent, MCPConfig
from agentchat.core.agents.plan_execute_agent import PlanExecuteAgent
from agentchat.core.agents.react_agent import ReactAgent
from agentchat.core.models.manager import ModelManager
from agentchat.tools import AgentTools

SUPPORTED_AGENT_MODES = {"react", "plan_execute", "codeact", "mcp"}

def normalize_agent_mode(agent_mode: str) -> str:
    """Normalize legacy/variant agent mode names to canonical values."""
    if not agent_mode:
        return agent_mode
    normalized = agent_mode.strip().lower().replace("-", "_")
    if normalized == "planexecute":
        return "plan_execute"
    return normalized


def _stringify_agent_result(result: Any) -> str:
    if isinstance(result, list):
        return "\n".join([getattr(msg, "content", str(msg)) for msg in result])
    return str(result)


async def invoke_agent(
    agent_mode: str,
    content: str,
    user_id: str,
    mcp_servers: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """统一入口：根据模式创建对应 Agent 执行用户消息，返回最终回复。"""
    agent_mode = normalize_agent_mode(agent_mode)
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

    return _stringify_agent_result(result)


async def invoke_agent_stream(
    agent_mode: str,
    content: str,
    user_id: str,
    mcp_servers: Optional[List[Dict[str, Any]]] = None,
) -> AsyncGenerator[str, None]:
    """流式执行 Agent，按内容片段产出回复。"""
    agent_mode = normalize_agent_mode(agent_mode)
    if agent_mode not in SUPPORTED_AGENT_MODES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported agent mode")

    if agent_mode == "react":
        model = ModelManager.get_tool_invocation_model()
        agent = ReactAgent(model=model, tools=AgentTools, mcp_servers=mcp_servers or [])
        async for chunk in agent.astream([HumanMessage(content=content)]):
            if chunk:
                yield chunk
        return

    if agent_mode == "plan_execute":
        agent = PlanExecuteAgent(user_id=user_id, tools=AgentTools, mcp_servers=mcp_servers or [])
        async for chunk in agent.astream([HumanMessage(content=content)]):
            if isinstance(chunk, dict):
                content_piece = chunk.get("content")
                if content_piece:
                    yield content_piece
            elif isinstance(chunk, str):
                yield chunk
        return

    if agent_mode == "codeact":
        agent = CodeActAgent(tools=AgentTools, user_id=user_id, mcp_servers=mcp_servers or [])
        async for chunk in agent.astream([HumanMessage(content=content)]):
            if isinstance(chunk, str):
                yield chunk
        return

    if not mcp_servers:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MCP agent requires configuration")

    config = mcp_servers[0]
    mcp_agent = MCPAgent(mcp_config=MCPConfig(**config), user_id=user_id)
    await mcp_agent.init_mcp_agent()
    result = await mcp_agent.ainvoke([HumanMessage(content=content)])
    yield _stringify_agent_result(result)
