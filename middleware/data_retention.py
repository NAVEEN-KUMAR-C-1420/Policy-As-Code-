"""
Data Retention
===============
Reusable, deterministic functions for identifying and deleting records
and files that exceed configured retention periods.

This module does NOT run automatically or on a schedule.
It is invoked explicitly when retention cleanup is needed.

Dangerous deletion operations are themselves governed - callers
must ensure proper authorization before invoking cleanup.

Usage:
    from middleware.data_retention import (
        find_expired_reports,
        find_expired_audit_logs,
        cleanup_expired_reports,
        cleanup_expired_audit_logs,
    )
"""

import os
import json
import sqlite3
from datetime import datetime, timezone, timedelta


def find_expired_reports(db_path: str, retention_days: int) -> list:
    """
    Find reports older than retention_days.

    Returns a list of dicts with report_id, account_id, created_at.
    Does NOT delete anything.
    """
    if retention_days < 0:
        raise ValueError(f"retention_days must be non-negative, got {retention_days}")

    cutoff = (datetime.now(timezone.utc) - timedelta(days=retention_days)).isoformat()

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT report_id, account_id, created_at FROM reports "
        "WHERE created_at < ?",
        (cutoff,),
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def cleanup_expired_reports(db_path: str, retention_days: int) -> int:
    """
    Delete reports older than retention_days from the database.

    Returns the number of rows deleted.
    """
    if retention_days < 0:
        raise ValueError(f"retention_days must be non-negative, got {retention_days}")

    cutoff = (datetime.now(timezone.utc) - timedelta(days=retention_days)).isoformat()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reports WHERE created_at < ?", (cutoff,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted


def find_expired_audit_entries(log_path: str, retention_days: int) -> list:
    """
    Find audit log entries older than retention_days.

    Returns a list of entries that would be removed.
    Does NOT delete anything.
    """
    if retention_days < 0:
        raise ValueError(f"retention_days must be non-negative, got {retention_days}")

    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    expired = []

    if not os.path.exists(log_path):
        return expired

    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                ts = entry.get("timestamp", "")
                if ts:
                    entry_time = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    if entry_time.tzinfo is None:
                        entry_time = entry_time.replace(tzinfo=timezone.utc)
                    if entry_time < cutoff:
                        expired.append(entry)
            except (json.JSONDecodeError, ValueError):
                continue

    return expired


def cleanup_expired_audit_entries(log_path: str, retention_days: int) -> int:
    """
    Remove audit log entries older than retention_days by rewriting
    the log file with only the retained entries.

    Returns the number of entries removed.
    """
    if retention_days < 0:
        raise ValueError(f"retention_days must be non-negative, got {retention_days}")

    if not os.path.exists(log_path):
        return 0

    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    retained = []
    removed_count = 0

    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                ts = entry.get("timestamp", "")
                if ts:
                    entry_time = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    if entry_time.tzinfo is None:
                        entry_time = entry_time.replace(tzinfo=timezone.utc)
                    if entry_time >= cutoff:
                        retained.append(json.dumps(entry, ensure_ascii=False))
                        continue
                removed_count += 1
            except (json.JSONDecodeError, ValueError):
                retained.append(line)
                continue

    with open(log_path, "w", encoding="utf-8") as f:
        for entry_line in retained:
            f.write(entry_line + "\n")

    return removed_count
