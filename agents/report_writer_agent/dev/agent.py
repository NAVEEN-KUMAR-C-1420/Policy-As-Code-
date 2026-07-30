"""
Agent Runner - Report Writer Agent
=====================================
Combines the LLM + guarded tools into an AgentExecutor and exposes
a simple run() function for the orchestrator to call.
"""

import os
import sys

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..")
sys.path.append(PROJECT_ROOT)

from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

from agents.report_writer_agent.dev.llm_config import get_agent_llm
from agents.report_writer_agent.dev.tools import get_tools

SYSTEM_PROMPT = """You are the Report Writer Agent in a financial analysis pipeline.

Your job: write a short, clear financial report (4-6 sentences) that
combines the collected transaction data and the risk analysis you are
given. Then use your tools to save that report to the database AND to
a report file.

You can WRITE data, but you are never allowed to delete anything."""


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


def run(account_id, collected_data, risk_report):
    """
    Entry point called by the orchestrator.
    Takes everything collected so far and produces + saves the
    final report.
    """
    executor = build_agent_executor()
    user_message = (
        f"Account ID: {account_id}\n\n"
        f"Collected data:\n{collected_data}\n\n"
        f"Risk analysis:\n{risk_report}\n\n"
        f"Write the final report and save it using your tools."
    )
    result = executor.invoke({"input": user_message})
    return result["output"]
