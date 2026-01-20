"""Agent 服务层：提供可用 Agent 列表。"""

from api.schemas import AgentInfo


# Agent 配置信息
AGENTS_CONFIG = {
    "ReAct": {
        "name": "ReAct智能体",
        "description": "基于 ReAct 范式的基础智能体，实现'推理-行动-观察'循环。适合简单任务和快速响应场景。",
    },
    "PlanExecute": {
        "name": "规划-执行智能体",
        "description": "先规划后执行的智能体，适合复杂任务处理。支持多步骤操作和精细控制。",
    },
    "CodeAct": {
        "name": "代码执行智能体",
        "description": "通过生成和执行 Python 代码来解决问题。适合数据分析、计算任务和编程场景。",
    },
}


def list_agents() -> list[AgentInfo]:
    """返回所有可用的 Agent 列表。"""
    agents = []
    for mode, config in AGENTS_CONFIG.items():
        agents.append(
            AgentInfo(
                mode=mode,
                name=config["name"],
                description=config["description"],
            )
        )
    return agents
