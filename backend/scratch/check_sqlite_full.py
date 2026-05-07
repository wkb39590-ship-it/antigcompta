import sqlite3
import os

db_path = 'backend/test.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        print("--- Agents in SQLite ---")
        cursor.execute("SELECT id, username, email FROM agents;")
        for row in cursor.fetchall():
            print(row)
        
        print("\n--- Searching for mohammed/khadija ---")
        cursor.execute("SELECT * FROM agents WHERE username LIKE '%mohammed%' OR username LIKE '%khadija%';")
        results = cursor.fetchall()
        if results:
            print(f"Found: {results}")
        else:
            print("Not found in SQLite.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
else:
    print("test.db not found")
