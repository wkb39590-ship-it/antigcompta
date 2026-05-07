import sqlite3
import os

db_path = 'backend/test.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT username FROM agents;")
        rows = cursor.fetchall()
        print(f"Agents in SQLite: {rows}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
else:
    print("test.db not found")
