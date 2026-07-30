"""
Shared SQLite Helper
=====================
Small, simple functions for talking to the dummy finance.db database.
Agent tool files import these instead of writing raw sqlite3 code
themselves, so the actual SQL stays in one place.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "finance.db")


def run_query(sql, params=()):
    """
    Run a SELECT query and return the results as a list of dictionaries.
    Example: run_query("SELECT * FROM accounts WHERE account_id = ?", (101,))
    """
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row  # lets us read columns by name
    cursor = connection.cursor()
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    connection.close()

    # Convert each sqlite3.Row into a plain dictionary
    return [dict(row) for row in rows]


def run_write(sql, params=()):
    """
    Run an INSERT / UPDATE / DELETE statement and commit it.
    Returns the id of the last inserted row (useful for INSERTs).
    """
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute(sql, params)
    connection.commit()
    last_row_id = cursor.lastrowid
    connection.close()
    return last_row_id
