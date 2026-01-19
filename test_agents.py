import argparse
import asyncio
import sys
from pathlib import Path

from langchain_core.messages import HumanMessage

from agentchat.core.agents.plan_execute_agent import PlanExecuteAgent
from agentchat.core.agents.react_agent import ReactAgent
from agentchat.core.models.manager import ModelManager
from agentchat.settings import initialize_app_settings
from agentchat.tools import AgentTools


async def run_react(full_response: bool) -> None:
    model = ModelManager.get_tool_invocation_model()
    agent = ReactAgent(model=model, tools=AgentTools)
    message = HumanMessage(content="帮我搜索阿里巴巴2024年的ESG报告，并列出标题和链接")

    if full_response:
        reply = await agent.ainvoke([message])
        print("\nReactAgent response:\n", reply)
    else:
        print("\nReactAgent stream:")
        async for chunk in agent.astream([message]):
            print(chunk, end="", flush=True)
        print()


async def run_plan_execute() -> None:
    agent = PlanExecuteAgent(
        user_id="demo",
        tools=AgentTools,
        mcp_servers=[],
    )
    messages = [HumanMessage(content="查询单号YT3760955655914物流信息，手机号后四位7704")]
    reply = await agent.ainvoke(messages)
    print("\nPlanExecuteAgent response:\n", reply)

async def main() -> None:
    parser = argparse.ArgumentParser(description="Quick functional tests for WDK Agent")
    parser.add_argument(
        "mode",
        choices=["react", "react-stream", "plan"],
        nargs="?",
        default="react",
        help="Which agent flow to run",
    )
    args = parser.parse_args()

    await initialize_app_settings()

    if args.mode == "react":
        await run_react(full_response=True)
    elif args.mode == "react-stream":
        await run_react(full_response=False)
    elif args.mode == "plan":
        await run_plan_execute()


if __name__ == "__main__":
    asyncio.run(main())
