"""
Sequential Pipeline Orchestrator
===================================
Runs the 3 agents ONE AFTER ANOTHER in a fixed order:

    Data Collector Agent -> Risk Analyzer Agent -> Report Writer Agent

This is plain Python sequential execution using LangChain agents -
it does NOT use LangGraph. Each agent's text output is simply passed
in as part of the next agent's input message.

Usage:
    python orchestrator/run_pipeline.py
"""

import os
import sys

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv()  # loads GROQ_API_KEY, TAVILY_API_KEY, etc. from .env

from agents.data_collector_agent.dev.agent import run as run_data_collector
from agents.risk_analyzer_agent.dev.agent import run as run_risk_analyzer
from agents.report_writer_agent.dev.agent import run as run_report_writer


def run_pipeline(account_id):
    print(f"\n=== STEP 1: Data Collector Agent (account {account_id}) ===")
    collected_data = run_data_collector(account_id)
    print(collected_data)

    print("\n=== STEP 2: Risk Analyzer Agent ===")
    risk_report = run_risk_analyzer(account_id, collected_data)
    print(risk_report)

    print("\n=== STEP 3: Report Writer Agent ===")
    final_report = run_report_writer(account_id, collected_data, risk_report)
    print(final_report)

    return final_report


if __name__ == "__main__":
    # Dummy accounts available: 101, 102, 103 (see data/init_db.py)
    ACCOUNT_ID = 101
    run_pipeline(ACCOUNT_ID)
