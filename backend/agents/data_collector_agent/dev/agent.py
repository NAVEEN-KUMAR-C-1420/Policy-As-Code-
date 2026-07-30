"""
Agent Runner - Data Collector Agent
=====================================
Combines:
  - the LLM        (from llm_config.py)
  - the tools       (from tools.py, already policy-guarded)
into a LangChain AgentExecutor, and exposes a simple run() function
that the orchestrator calls.
"""

import os
import sys

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..")
sys.path.append(PROJECT_ROOT)

from langchain.agents import create_agent

from agents.data_collector_agent.dev.llm_config import get_agent_llm
from agents.data_collector_agent.dev.tools import get_tools

SYSTEM_PROMPT = """You are the Data Collector Agent in a financial analysis pipeline.

Your job: use your tools to read the account's transactions and search
for one relevant piece of market news. Then summarize both clearly in
plain text for the next agent to use.

You are READ-ONLY. You never write, update, or delete any data."""


def build_agent():
    llm = get_agent_llm()
    tools = get_tools()

    return create_agent(
        model=llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT
    )

def run(account_id: int) -> str:
    agent = build_agent()
    user_message = (
        f"Please collect data for account {account_id}. "
        "Find their transactions and one relevant market news piece."
    )
    result = agent.invoke({"messages": [{"role": "user", "content": user_message}]})
    return result["messages"][-1].content
