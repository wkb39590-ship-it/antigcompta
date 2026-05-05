import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://admin:admin123@db:5432/compta_db")
engine = create_engine(DATABASE_URL)

def migrate_paie():
    with engine.connect() as conn:
        print("Migrating payroll entries from OD to PAYE...")
        
        # Identifie et migre les écritures
        res = conn.execute(text("""
            UPDATE ecritures_journal 
            SET journal_code = 'PAYE'
            WHERE journal_code = 'OD' 
              AND (description LIKE '%%Bulletin de paie%%' OR reference LIKE 'PAIE-%%')
        """))
        print(f"Migrated {res.rowcount} entries.")
        conn.commit()
        print("Done.")

if __name__ == "__main__":
    migrate_paie()
