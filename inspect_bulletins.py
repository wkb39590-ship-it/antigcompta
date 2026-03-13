import sqlite3

def inspect_bulletins(path):
    print(f"Inspection de : {path}")
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM bulletins_paie")
        count = cursor.fetchone()[0]
        print(f"Table bulletins_paie : {count} entrées")
        if count > 0:
            cursor.execute("SELECT id, employe_id, mois, annee, salaire_brut, statut FROM bulletins_paie LIMIT 5")
            rows = cursor.fetchall()
            for r in rows:
                print(f"  {r}")
    except Exception as e:
        print(f"Erreur sur bulletins_paie : {e}")
            
    conn.close()

if __name__ == "__main__":
    inspect_bulletins("backend/test.db")
    inspect_bulletins("test.db")
