import sqlite3
import os

def debug_data(db_path):
    if not os.path.exists(db_path):
        return
    
    print(f"=== Debugging {db_path} ===")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check lignes_amortissement
        print("\n--- Lignes d'amortissement ---")
        cursor.execute("SELECT id, immobilisation_id, annee, ecriture_generee FROM lignes_amortissement")
        lignes = cursor.fetchall()
        for l in lignes:
            print(f"ID: {l[0]} | Immo: {l[1]} | Année: {l[2]} | Générée: {l[3]}")
            
        # Check OD entries
        print("\n--- Écritures OD (Journal OD) ---")
        cursor.execute("SELECT id, reference, description, is_validated FROM ecritures_journal WHERE journal_code='OD'")
        ods = cursor.fetchall()
        for o in ods:
            print(f"ID: {o[0]} | Ref: {o[1]} | Desc: {o[2]} | Validé: {o[3]}")
            
    except Exception as e:
        print(f"Erreur : {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    debug_data("backend/test.db")
    debug_data("test.db")
