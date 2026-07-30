"""
Agent Runner - Risk Analyzer Agent
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

from agents.risk_analyzer_agent.dev.llm_config import get_agent_llm
from agents.risk_analyzer_agent.dev.tools import get_tools

SYSTEM_PROMPT = """You are the Risk Analyzer Agent in a financial analysis pipeline.

Your job: use your tools to look up the account summary and calculate a
risk score, using the transaction data you are given as context to
estimate a reasonable monthly_outflow number. Then explain the risk
level in 3-4 plain-language sentences.

You can READ data and COMPUTE with it, but you never write or delete
any data."""


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


def run(account_id, collected_data):
    """
    Entry point called by the orchestrator.
    Takes the account_id and the output of the Data Collector Agent,
    and returns a risk analysis as text.
    """
    executor = build_agent_executor()
    user_message = (
        f"Account ID: {account_id}\n\n"
        f"Here is the data collected so far:\n{collected_data}\n\n"
        f"Use your tools to check the account summary and calculate a "
        f"risk score for this account."
    )
    result = executor.invoke({"input": user_message})
    return result["output"]
