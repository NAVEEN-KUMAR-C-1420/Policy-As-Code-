"""
Agent Runner - Risk Analyzer Agent
=====================================
Combines the LLM + guarded tools into an AgentExecutor and exposes
a simple run() function for the orchestrator to call.
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from langchain.agents import create_agent

from agents.risk_analyzer_agent.dev.llm_config import get_agent_llm
from agents.risk_analyzer_agent.dev.tools import get_tools

SYSTEM_PROMPT = """You are the Risk Analyzer Agent in a financial analysis pipeline.

Your job: use your tools to look up the account summary and calculate a
risk score, using the transaction data you are given as context to
estimate a reasonable monthly_outflow number. Then explain the risk
level in 3-4 plain-language sentences.

You can READ data and COMPUTE with it, but you never write or delete
any data."""


def build_agent():
    llm = get_agent_llm()
    tools = get_tools()

    return create_agent(model=llm, tools=tools, system_prompt=SYSTEM_PROMPT)


def run(account_id: int, collected_data: str) -> str:
    agent = build_agent()
    user_message = (
        f"Account ID: {account_id}\n\n" f"Data from previous agent:\n{collected_data}\n\n" "Please analyze the risk."
    )
    result = agent.invoke({"messages": [{"role": "user", "content": user_message}]})
    return result["messages"][-1].content
