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
from dotenv import load_dotenv

load_dotenv()

from core.paths import DATA_DIR
DB_PATH = DATA_DIR / "finance.db"
PROVIDER = os.getenv("DATABASE_PROVIDER", "sqlite").lower()

def get_db_connection():
    if PROVIDER == "supabase":
        import psycopg2
        from urllib.parse import urlparse, unquote
        
        host_env = os.getenv("SUPABASE_DB_HOST", "")
        if host_env.startswith("postgres://") or host_env.startswith("postgresql://"):
            parsed = urlparse(host_env)
            return psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port,
                dbname=parsed.path.lstrip("/"),
                user=unquote(parsed.username) if parsed.username else None,
                password=unquote(parsed.password) if parsed.password else None
            )
        else:
            return psycopg2.connect(
                host=host_env,
                port=os.getenv("SUPABASE_DB_PORT"),
                dbname=os.getenv("SUPABASE_DB_NAME"),
                user=os.getenv("SUPABASE_DB_USER"),
                password=os.getenv("SUPABASE_DB_PASSWORD")
            )
    return sqlite3.connect(DB_PATH)


def create_tables(cursor):
    pk_type = "SERIAL PRIMARY KEY" if PROVIDER == "supabase" else "INTEGER PRIMARY KEY AUTOINCREMENT"
    pk_type_acc = "INTEGER PRIMARY KEY" if PROVIDER == "supabase" else "INTEGER PRIMARY KEY"
    
    # We must drop tables if doing a fresh init on PG maybe? No, IF NOT EXISTS is safe.
    
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS accounts (
            account_id {pk_type_acc},
            customer_name TEXT,
            account_type TEXT,
            balance REAL
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id {pk_type_acc},
            account_id INTEGER,
            txn_date TEXT,
            amount REAL,
            category TEXT,
            description TEXT
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS reports (
            report_id {pk_type},
            account_id INTEGER,
            conversation_id TEXT,
            report_content TEXT,
            summary TEXT,
            risk_assessment TEXT,
            created_at TEXT,
            generated_by TEXT,
            metadata TEXT
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS audit_logs (
            audit_id {pk_type},
            timestamp TEXT,
            agent_name TEXT,
            tool_name TEXT,
            action TEXT,
            decision TEXT,
            reason TEXT,
            policy_version TEXT,
            risk_score REAL,
            execution_time REAL,
            status TEXT,
            metadata TEXT
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS conversations (
            conversation_id {pk_type},
            user_message TEXT,
            assistant_response TEXT,
            created_at TEXT,
            status TEXT,
            session_id TEXT
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS tool_executions (
            execution_id {pk_type},
            conversation_id TEXT,
            tool_name TEXT,
            allowed INTEGER,
            blocked INTEGER,
            reason TEXT,
            risk_score REAL,
            policy_version TEXT,
            duration REAL,
            timestamp TEXT
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS hitl_requests (
            request_id {pk_type},
            conversation_id TEXT,
            tool_name TEXT,
            risk_score REAL,
            threshold REAL,
            status TEXT,
            approved_by TEXT,
            approval_time TEXT,
            created_at TEXT,
            reason TEXT
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS governance_events (
            event_id {pk_type},
            conversation_id TEXT,
            event_type TEXT,
            description TEXT,
            agent TEXT,
            policy_version TEXT,
            created_at TEXT,
            metadata TEXT
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS governance_versions (
            version_id {pk_type},
            version_number INTEGER,
            git_commit_sha TEXT,
            git_branch TEXT,
            policy_hash TEXT,
            agent_hash TEXT,
            governance_hash TEXT,
            change_summary TEXT,
            created_at TEXT,
            created_by TEXT,
            deployment_status TEXT,
            is_active INTEGER,
            rolled_back_from INTEGER,
            rollback_timestamp TEXT,
            metadata TEXT
        )
    """)

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS policy_versions (
            version_id {pk_type},
            agent_id TEXT,
            commit_sha TEXT,
            policy_hash TEXT,
            policy_yaml TEXT,
            deployed_at TEXT,
            deployed_by TEXT,
            deployment_source TEXT,
            is_active INTEGER,
            notes TEXT
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
    
    placeholder = "%s, %s, %s, %s" if PROVIDER == "supabase" else "?, ?, ?, ?"
    cursor.executemany(
        f"INSERT INTO accounts VALUES ({placeholder})", accounts
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
    
    txn_ph = "%s, %s, %s, %s, %s, %s" if PROVIDER == "supabase" else "?, ?, ?, ?, ?, ?"
    cursor.executemany(
        f"INSERT INTO transactions VALUES ({txn_ph})", transactions
    )


def main():
    connection = get_db_connection()
    cursor = connection.cursor()
    create_tables(cursor)
    seed_data(cursor)
    connection.commit()
    connection.close()
    
    if PROVIDER == "supabase":
        print(f"Supabase (PostgreSQL) database ready!")
    else:
        print(f"Dummy database ready at: {DB_PATH}")


if __name__ == "__main__":
    main()
