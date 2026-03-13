import sqlite3

def check_db(path):
    print(f"Inspection de : {path}")
    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        
        # Liste des tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables : {[t[0] for t in tables]}")
        
        # Nombre d'écritures
        if ('ecritures_journal',) in tables:
            cursor.execute("SELECT COUNT(*) FROM ecritures_journal;")
            print(f"Nombre d'écritures dans ecritures_journal : {cursor.fetchone()[0]}")
            
            # Check colonnes
            cursor.execute("PRAGMA table_info(ecritures_journal);")
            cols = [c[1] for c in cursor.fetchall()]
            print(f"Colonnes : {cols}")
        else:
            print("Table ecritures_journal non trouvée.")
            
        conn.close()
    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    check_db("backend/test.db")
    print("-" * 20)
    check_db("test.db")
