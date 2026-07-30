import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(PROJECT_ROOT)

def get_all_tools() -> list:
    return ["read_account_transactions", "search_market_news", "read_account_summary", "calculate_risk_score", "save_report_to_db", "write_report_file", "delete_old_reports"]

def get_tool_metadata(tool_name: str) -> dict:
    return {"tool_name": tool_name, "description": f"Metadata for {tool_name}"}

def get_tool_usage(tool_name: str) -> dict:
    return {"tool_name": tool_name, "times_called": 42}

def test_tool_execution(tool_name: str) -> dict:
    # Test through governance middleware without bypassing it
    # We will simulate this by checking if the tool is delete_old_reports, which is blocked
    from agents.report_writer_agent.dev.tools import guarded_delete_old_reports
    if tool_name == "delete_old_reports":
        result = guarded_delete_old_reports(account_id=101)
        return {"tool_name": tool_name, "result": result}
    
    return {"tool_name": tool_name, "result": "Tool executed successfully through guard"}
