import os
from sqlalchemy import create_engine, text

PG_URL = "postgresql+psycopg2://admin:admin123@localhost:5454/compta_db"

def fix_societe_id():
    print(f"Correction du societe_id pour DOT-1-2026 (passage de 1 à 7)...")
    try:
        engine = create_engine(PG_URL)
        with engine.connect() as conn:
            # 1. Mise à jour de l'écriture
            query_entry = text("""
                UPDATE ecritures_journal 
                SET societe_id = 7,
                    entry_date = '2026-03-28'
                WHERE reference = 'DOT-1-2026';
            """)
            result = conn.execute(query_entry)
            
            # 2. Mise à jour de l'immobilisation correspondante pour éviter les erreurs futures
            # On extrait l'ID immo de la référence DOT-1-2026 -> 1
            query_immo = text("UPDATE immobilisations SET societe_id = 7 WHERE id = 1")
            conn.execute(query_immo)
            
            conn.commit()
            
            if result.rowcount > 0:
                print(f"Succès : Écriture DOT-1-2026 associée à la société 7.")
            else:
                print("Erreur : Écriture non trouvée.")

    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    fix_societe_id()
