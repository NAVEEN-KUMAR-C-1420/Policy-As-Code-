"""
Agent Runner - Report Writer Agent
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

from agents.report_writer_agent.dev.llm_config import get_agent_llm
from agents.report_writer_agent.dev.tools import get_tools

SYSTEM_PROMPT = """You are the Report Writer Agent in a financial analysis pipeline.

Your job: write a short, clear financial report (4-6 sentences) that
combines the collected transaction data and the risk analysis you are
given. Then use your tools to save that report to the database AND to
a report file.

You can WRITE data, but you are never allowed to delete anything."""


def build_agent():
    llm = get_agent_llm()
    tools = get_tools()

    return create_agent(model=llm, tools=tools, system_prompt=SYSTEM_PROMPT)


def run(account_id: int, collected_data: str, risk_report: str) -> str:
    agent = build_agent()
    user_message = (
        f"Account ID: {account_id}\n\n"
        f"Collected Data:\n{collected_data}\n\n"
        f"Risk Report:\n{risk_report}\n\n"
        "Please write the final report, save it to the DB, and write it to a file."
    )
    result = agent.invoke({"messages": [{"role": "user", "content": user_message}]})
    return result["messages"][-1].content
