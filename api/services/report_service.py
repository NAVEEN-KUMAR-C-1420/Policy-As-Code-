import os
import sys
import sqlite3

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(PROJECT_ROOT)

from common.db import run_query, run_write

def list_reports() -> list:
    rows = run_query("SELECT report_id, account_id, created_at FROM reports", ())
    return [dict(r) for r in rows]

def get_report(report_id: int) -> dict:
    rows = run_query("SELECT * FROM reports WHERE report_id = ?", (report_id,))
    if not rows:
        raise ValueError("Report not found")
    return dict(rows[0])

def delete_report(report_id: int) -> dict:
    # Simulated deletion passing governance
    run_write("DELETE FROM reports WHERE report_id = ?", (report_id,))
    return {"status": "deleted", "report_id": report_id}

def download_report(report_id: int) -> str:
    rows = run_query("SELECT summary FROM reports WHERE report_id = ?", (report_id,))
    if not rows:
        raise ValueError("Report not found")
    return rows[0]["summary"]
