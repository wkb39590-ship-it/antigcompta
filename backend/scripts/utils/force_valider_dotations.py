import sqlite3
import os
from datetime import datetime

def fix_db(db_path):
    if not os.path.exists(db_path):
        print(f"Skipping {db_path} (not found)")
        return
    
    print(f"Checking {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # On cherche les écritures de dotation non validées
        cursor.execute("SELECT id, reference FROM ecritures_journal WHERE journal_code='OD' AND reference LIKE 'DOT-%' AND is_validated=0")
        entries = cursor.fetchall()
        
        if not entries:
            print("Aucune écriture de dotation à valider trouvée.")
            return
            
        print(f"Trouvé {len(entries)} écritures à valider.")
        for eid, ref in entries:
            print(f"Validation de {ref}...")
            cursor.execute("UPDATE ecritures_journal SET is_validated=1, validated_at=?, validated_by='system_fix' WHERE id=?", (datetime.now().isoformat(), eid))
            
        conn.commit()
        print("Mise à jour effectuée.")
    except Exception as e:
        print(f"Erreur sur {db_path}: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_db("backend/test.db")
    fix_db("test.db")
