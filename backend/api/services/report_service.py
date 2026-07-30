import os
import sqlite3
import sys

from core.paths import BASE_DIR as PROJECT_ROOT

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

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
    rows = run_query("SELECT report_content, summary FROM reports WHERE report_id = ?", (report_id,))
    if not rows:
        raise ValueError("Report not found")
    # Return report_content if it exists, fallback to summary for backward compatibility
    content = rows[0].get("report_content")
    if content:
        return content
    return rows[0].get("summary", "")
