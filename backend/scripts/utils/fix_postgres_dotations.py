import os
from sqlalchemy import create_engine, text

# URL de connexion à PostgreSQL (via le port exposé 5454 sur localhost)
PG_URL = "postgresql+psycopg2://admin:admin123@localhost:5454/compta_db"

def fix_postgres():
    print(f"Tentative de connexion à PostgreSQL sur {PG_URL}...")
    try:
        # On utilise psycopg2 s'il est dispo, sinon on essaiera sans le driver spécifique dans l'URL
        engine = create_engine(PG_URL)
        with engine.connect() as conn:
            # On cherche les écritures de dotation non validées (is_validated = False ou 0)
            # Dans Postgres, le type boolean est utilisé
            query = text("""
                UPDATE ecritures_journal 
                SET is_validated = true, 
                    validated_at = NOW(), 
                    validated_by = 'system_fix_pg' 
                WHERE journal_code = 'OD' 
                  AND reference LIKE 'DOT-%' 
                  AND is_validated = false
                RETURNING reference;
            """)
            result = conn.execute(query)
            conn.commit()
            
            rows = result.fetchall()
            if not rows:
                print("Aucune écriture de dotation à valider trouvée dans PostgreSQL.")
            else:
                print(f"Validé {len(rows)} écritures :")
                for r in rows:
                    print(f" - {r[0]}")
                    
    except Exception as e:
        print(f"Erreur avec psycopg2 : {e}")
        print("Tentative avec le driver psycopg (v3)...")
        try:
            PG_URL_V3 = "postgresql+psycopg://admin:admin123@localhost:5454/compta_db"
            engine = create_engine(PG_URL_V3)
            with engine.connect() as conn:
                query = text("""
                    UPDATE ecritures_journal 
                    SET is_validated = true, 
                        validated_at = NOW(), 
                        validated_by = 'system_fix_pg' 
                    WHERE journal_code = 'OD' 
                      AND reference LIKE 'DOT-%' 
                      AND is_validated = false
                    RETURNING reference;
                """)
                result = conn.execute(query)
                conn.commit()
                rows = result.fetchall()
                if not rows:
                    print("Aucune écriture de dotation à valider trouvée dans PostgreSQL.")
                else:
                    print(f"Validé {len(rows)} écritures.")
        except Exception as e2:
            print(f"Erreur finale : {e2}")

if __name__ == "__main__":
    fix_postgres()
