import sqlite3

def inspect_immos(path):
    print(f"Inspection de : {path}")
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, designation, valeur_acquisition, date_acquisition FROM immobilisations")
        rows = cursor.fetchall()
        print(f"Table immobilisations : {len(rows)} entrées")
        for r in rows:
            print(f"  {r}")
    except Exception as e:
        print(f"Erreur sur immobilisations : {e}")
            
    conn.close()

if __name__ == "__main__":
    inspect_immos("backend/test.db")
    inspect_immos("test.db")
