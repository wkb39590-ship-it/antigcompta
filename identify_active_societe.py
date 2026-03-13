import os
from sqlalchemy import create_engine, text

PG_URL = "postgresql+psycopg2://admin:admin123@localhost:5454/compta_db"

def identify_active_societe():
    print(f"Recherche de la société pour les écritures de paie visibles...")
    try:
        engine = create_engine(PG_URL)
        with engine.connect() as conn:
            # On cherche l'une des écritures que l'utilisateur voit
            query = text("""
                SELECT reference, societe_id, journal_code, entry_date, is_validated 
                FROM ecritures_journal 
                WHERE reference IN ('PAIE-6-02/2026', 'PAIE-2-03/2026', 'PAIE-3-03/2026', 'PAIE-4-03/2026');
            """)
            result = conn.execute(query)
            rows = result.fetchall()
            
            if rows:
                print("Écritures trouvées :")
                for r in rows:
                    print(f" - Ref: {r[0]} | Societe ID: {r[1]} | Journal: {r[2]} | Date: {r[3]} | Validé: {r[4]}")
                
                # On check aussi l'écriture DOT-1-2026 actuelle
                query_dot = text("SELECT reference, societe_id, is_validated FROM ecritures_journal WHERE reference = 'DOT-1-2026'")
                dot = conn.execute(query_dot).fetchone()
                if dot:
                    print(f"\nÉtat actuel de DOT-1-2026 :")
                    print(f" - Ref: {dot[0]} | Societe ID: {dot[1]} | Validé: {dot[2]}")
            else:
                print("Aucune de ces écritures de paie n'a été trouvée dans la base de données PostgreSQL.")

    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    identify_active_societe()
