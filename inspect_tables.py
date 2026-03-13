import sqlite3

def inspect_all_entry_tables(path):
    print(f"Inspection de : {path}")
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    
    tables = ['journal_entries', 'ecritures_comptables', 'ecritures_journal']
    
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"Table {table} : {count} entrées")
            if count > 0:
                cursor.execute(f"SELECT id, journal_code, reference, description, is_validated FROM {table} LIMIT 5")
                rows = cursor.fetchall()
                for r in rows:
                    print(f"  {r}")
        except Exception as e:
            print(f"Erreur sur {table} : {e}")
            
    conn.close()

if __name__ == "__main__":
    inspect_all_entry_tables("backend/test.db")
