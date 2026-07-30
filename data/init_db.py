"""
Dummy Database Setup
======================
Run this file once to create the dummy finance.db SQLite database:

    python data/init_db.py

It creates 3 tables:
  - accounts      (read by agents)
  - transactions   (read by agents)
  - reports        (written by the Report Writer Agent)

and fills accounts + transactions with a few sample rows so the
agents have realistic data to work with.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "finance.db")


def create_tables(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            account_id INTEGER PRIMARY KEY,
            customer_name TEXT,
            account_type TEXT,
            balance REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY,
            account_id INTEGER,
            txn_date TEXT,
            amount REAL,
            category TEXT,
            description TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            report_id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER,
            created_at TEXT,
            summary TEXT
        )
    """)


def seed_data(cursor):
    # Only insert sample rows the first time (accounts table is empty)
    cursor.execute("SELECT COUNT(*) FROM accounts")
    existing_rows = cursor.fetchone()[0]
    if existing_rows > 0:
        return

    accounts = [
        (101, "Asha Mehta", "savings", 52000.0),
        (102, "Ravi Kumar", "current", 118500.0),
        (103, "Priya Nair", "savings", 8400.0),
    ]
    cursor.executemany(
        "INSERT INTO accounts VALUES (?, ?, ?, ?)", accounts
    )

    transactions = [
        (1, 101, "2026-07-01", -1200.0, "groceries", "Big Bazaar"),
        (2, 101, "2026-07-05", -4500.0, "rent", "Monthly rent"),
        (3, 101, "2026-07-10", 52000.0, "salary", "Monthly salary credit"),
        (4, 102, "2026-07-03", -25000.0, "investment", "Mutual fund SIP"),
        (5, 102, "2026-07-15", -1800.0, "dining", "Restaurant"),
        (6, 103, "2026-07-02", -300.0, "utility", "Electricity bill"),
        (7, 103, "2026-07-20", -6000.0, "shopping", "Online shopping"),
    ]
    cursor.executemany(
        "INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?)", transactions
    )


def main():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    create_tables(cursor)
    seed_data(cursor)
    connection.commit()
    connection.close()
    print(f"Dummy database ready at: {DB_PATH}")


if __name__ == "__main__":
    main()
