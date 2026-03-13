import sqlite3

def inspect_societes(path):
    print(f"Inspection de : {path}")
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    
    try:
        print("\n--- Cabinets ---")
        cursor.execute("SELECT id, nom FROM cabinets")
        for r in cursor.fetchall(): print(r)
        
        print("\n--- Sociétés ---")
        cursor.execute("SELECT id, raison_sociale, cabinet_id, ice FROM societes")
        for r in cursor.fetchall(): print(r)
        
        print("\n--- Agents ---")
        cursor.execute("SELECT id, username, cabinet_id FROM agents")
        for r in cursor.fetchall(): print(r)
            
    except Exception as e:
        print(f"Erreur : {e}")
            
    conn.close()

if __name__ == "__main__":
    inspect_societes("backend/test.db")
