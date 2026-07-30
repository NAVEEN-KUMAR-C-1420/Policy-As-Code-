import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "finance.db")
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

print("Tables:")
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
print([r[0] for r in c.fetchall()])

print("\nAccounts:")
c.execute("SELECT * FROM accounts")
print(c.fetchall())

print("\nTransactions:")
c.execute("SELECT * FROM transactions")
print(c.fetchall())

print("\nReports:")
c.execute("SELECT * FROM reports")
print(c.fetchall())

print("\nIntegrity:")
c.execute("PRAGMA integrity_check")
print(c.fetchall())

conn.close()
