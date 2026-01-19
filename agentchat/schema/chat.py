from typing import Any, Dict, List, Optional, Literal

from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    tool_name: str = Field(..., description="工具名称（如 get_current_time、get_weather）")
    tool_args: Any = Field(..., description="工具参数（可字符串/字典/无参数，根据工具灵活定义）")
    message: str = Field(..., description="该工具调用的说明信息")


class AgentCall(BaseModel):
    """Agent 调用的数据模型。"""
    agent_name: Literal["react_agent", "codeact_agent", "plan_agent"] = Field(
        ...,
        description="要调用的 Agent 名称"
    )
    task: str = Field(
        ...,
        description="给 Agent 的任务描述"
    )
    context: Optional[str] = Field(
        None,
        description="可选的上下文信息（如之前步骤的结果）"
    )
    message: str = Field(
        ...,
        description="该 Agent 调用的说明信息"
    )


class EnhancedStep(BaseModel):
    """增强版步骤，支持工具或 Agent 调用。"""
    type: Literal["tool", "agent"] = Field(
        ...,
        description="调用类型：tool（工具函数）或 agent（智能体）"
    )
    tool_call: Optional[ToolCall] = Field(
        None,
        description="当 type='tool' 时，指定工具调用的详细信息"
    )
    agent_call: Optional[AgentCall] = Field(
        None,
        description="当 type='agent' 时，指定 Agent 调用的详细信息"
    )


StepTools = List[ToolCall]
EnhancedSteps = List[EnhancedStep]


class PlanToolFlow(BaseModel):
    """Structured plan used by the planning agent to sequence tool calls."""

    root: Dict[str, StepTools] = Field(
        ...,
        description="工具调用流程，键为步骤名（step_1/step_2...），值为该步骤的工具调用列表",
    )


class EnhancedPlanFlow(BaseModel):
    """增强版计划，支持 Agent 和工具混合调用。"""

    root: Dict[str, EnhancedSteps] = Field(
        ...,
        description="执行流程，键为步骤名（step_1/step_2...），值为该步骤的调用列表（可以是 Agent 或工具）",
    )
