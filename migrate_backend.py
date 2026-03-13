import sqlite3
import os

def migrate_backend_db():
    db_path = "backend/test.db"
    if not os.path.exists(db_path):
        print(f"Fichier {db_path} non trouvé.")
        return

    print(f"Migration de : {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if societe_id exists
        cursor.execute("PRAGMA table_info(ecritures_journal);")
        cols = [c[1] for c in cursor.fetchall()]
        
        if "societe_id" not in cols:
            print("Ajout de la colonne societe_id...")
            cursor.execute("ALTER TABLE ecritures_journal ADD COLUMN societe_id INTEGER;")
            conn.commit()
            print("Colonne ajoutée.")
        else:
            print("La colonne societe_id existe déjà.")
            
    except Exception as e:
        print(f"Erreur : {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_backend_db()
