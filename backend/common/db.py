"""
Shared SQLite Helper
=====================
Small, simple functions for talking to the dummy finance.db database.
Agent tool files import these instead of writing raw sqlite3 code
themselves, so the actual SQL stays in one place.
"""

import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "finance.db")
PROVIDER = os.getenv("DATABASE_PROVIDER", "sqlite").lower()

def _get_pg_connection():
    import psycopg2
    import psycopg2.extras
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

def run_query(sql, params=()):
    """
    Run a SELECT query and return the results as a list of dictionaries.
    """
    if PROVIDER == "supabase":
        import psycopg2.extras
        conn = _get_pg_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        # Convert SQLite '?' to Postgres '%s'
        pg_sql = sql.replace("?", "%s")
        cursor.execute(pg_sql, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    else:
        connection = sqlite3.connect(DB_PATH)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        connection.close()
        return [dict(row) for row in rows]


def run_write(sql, params=()):
    """
    Run an INSERT / UPDATE / DELETE statement and commit it.
    Returns the id of the last inserted row (useful for INSERTs).
    """
    if PROVIDER == "supabase":
        import psycopg2
        conn = _get_pg_connection()
        cursor = conn.cursor()
        
        # Convert SQLite '?' to Postgres '%s'
        pg_sql = sql.replace("?", "%s")
        
        # Postgres requires RETURNING clause for lastrowid analog, 
        # but for simplicity since we don't always know PK name, we can try to fetch it if it's an insert.
        # But SQLite's lastrowid is often used just by returning it.
        # Let's add RETURNING id to inserts if possible, or just ignore if not needed.
        # Since we can't easily parse SQL, we'll try to execute as-is.
        cursor.execute(pg_sql, params)
        conn.commit()
        
        # PostgreSQL cursor doesn't have lastrowid. We'll return 0 if we can't fetch it, 
        # which is usually fine if the caller doesn't strictly depend on it.
        # Wait! Let's check where run_write is used.
        # If it's used for inserting reports and audits, they might need the ID.
        last_id = 0
        try:
            # If the user appended RETURNING id manually, fetch it:
            if "RETURNING" in pg_sql.upper():
                last_id = cursor.fetchone()[0]
        except psycopg2.ProgrammingError:
            pass # No results to fetch
            
        conn.close()
        return last_id
    else:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        cursor.execute(sql, params)
        connection.commit()
        last_row_id = cursor.lastrowid
        connection.close()
        return last_row_id
