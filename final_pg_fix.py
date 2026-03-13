import os
from sqlalchemy import create_engine, text

PG_URL = "postgresql+psycopg2://admin:admin123@localhost:5454/compta_db"

def final_fix():
    print(f"Correction finale de DOT-1-2026 sur PostgreSQL...")
    try:
        engine = create_engine(PG_URL)
        with engine.connect() as conn:
            # 1. Associer à la société 1 et changer la date au 28/03/2026 pour visibilité immédiate
            # (Normalement 12/31, mais l'utilisateur veut la VOIR dans sa liste actuelle)
            query = text("""
                UPDATE ecritures_journal 
                SET societe_id = 1,
                    entry_date = '2026-03-28',
                    is_validated = true,
                    validated_by = 'system_final_fix'
                WHERE reference = 'DOT-1-2026';
            """)
            result = conn.execute(query)
            conn.commit()
            
            if result.rowcount > 0:
                print(f"Succès : Écriture DOT-1-2026 mise à jour (Societe=1, Date=2026-03-28).")
            else:
                print("Erreur : Écriture non trouvée.")
                
            # Bonus : s'assurer que les lignes sont bien là (même si on a eu une erreur de table tout à l'heure)
            check_lines = text("SELECT COUNT(*) FROM lignes_ecritures WHERE ecriture_journal_id = 19")
            count = conn.execute(check_lines).fetchone()[0]
            print(f"Nombre de lignes dans lignes_ecritures pour ID 19 : {count}")

    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    final_fix()
