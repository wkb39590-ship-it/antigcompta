import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'test.db')
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables: {tables}")
        
        cursor.execute("SELECT count(*) FROM releves_bancaires;")
        count = cursor.fetchone()[0]
        print(f"Total rows in releves_bancaires: {count}")
        
        if count > 0:
            cursor.execute("SELECT id, banque_nom, societe_id FROM releves_bancaires;")
            rows = cursor.fetchall()
            for r in rows:
                print(f"Row: {r}")
                cursor.execute(f"SELECT count(*) FROM lignes_releve WHERE releve_id={r[0]};")
                lcount = cursor.fetchone()[0]
                print(f"  -> Operations count: {lcount}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
