import os
from sqlalchemy import create_engine, text

PG_URL = "postgresql+psycopg2://admin:admin123@localhost:5454/compta_db"

def inspect_dotation():
    print(f"Inspection de l'écriture DOT-1-2026...")
    try:
        engine = create_engine(PG_URL)
        with engine.connect() as conn:
            query = text("""
                SELECT id, societe_id, journal_code, entry_date, reference, description, is_validated, total_debit, total_credit 
                FROM ecritures_journal 
                WHERE reference = 'DOT-1-2026';
            """)
            result = conn.execute(query)
            row = result.fetchone()
            
            if row:
                print("Détails de l'écriture :")
                print(f" - ID: {row[0]}")
                print(f" - Societe ID: {row[1]}")
                print(f" - Journal: {row[2]}")
                print(f" - Date: {row[3]}")
                print(f" - Ref: {row[4]}")
                print(f" - Validé: {row[6]}")
                print(f" - Débit: {row[7]}")
                print(f" - Crédit: {row[8]}")
                
                # Check lines
                print("\nLignes associées :")
                lines_query = text("SELECT account_code, debit, credit FROM entry_lines WHERE ecriture_journal_id = :eid")
                lines = conn.execute(lines_query, {"eid": row[0]}).fetchall()
                for l in lines:
                    print(f"   Compte: {l[0]} | Débit: {l[1]} | Crédit: {l[2]}")
            else:
                print("Écriture DOT-1-2026 non trouvée.")
                
            # Check current societe_id in session context (approximate)
            # Just listing all societes to compare
            print("\nListe des sociétés :")
            soc_query = text("SELECT id, raison_sociale FROM societes")
            socs = conn.execute(soc_query).fetchall()
            for s in socs:
                print(f" - ID: {s[0]} | Nom: {s[1]}")

    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    inspect_dotation()
