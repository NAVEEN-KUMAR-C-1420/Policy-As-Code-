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

from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

from agents.data_collector_agent.dev.llm_config import get_agent_llm
from agents.data_collector_agent.dev.tools import get_tools

SYSTEM_PROMPT = """You are the Data Collector Agent in a financial analysis pipeline.

Your job: use your tools to read the account's transactions and search
for one relevant piece of market news. Then summarize both clearly in
plain text for the next agent to use.

You are READ-ONLY. You never write, update, or delete any data."""


def build_agent_executor():
    llm = get_agent_llm()
    tools = get_tools()

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)


def run(account_id):
    """
    Entry point called by the orchestrator.
    Takes an account_id and returns the collected data as text.
    """
    executor = build_agent_executor()
    user_message = (
        f"Collect the transactions for account_id {account_id} and search "
        f"for one recent piece of market news relevant to personal finance."
    )
    result = executor.invoke({"input": user_message})
    return result["output"]
