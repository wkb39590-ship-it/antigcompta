import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://admin:admin123@db:5432/compta_db")
engine = create_engine(DATABASE_URL)

def migrate_immo_entries():
    with engine.connect() as conn:
        # Find factures that are IMMOBILISATION
        res = conn.execute(text("""
            SELECT f.id, e.id as entry_id, e.journal_code 
            FROM factures f
            JOIN ecritures_journal e ON f.id = e.facture_id
            WHERE f.invoice_type = 'IMMOBILISATION' AND e.journal_code = 'ACH'
        """)).fetchall()
        
        print(f"Found {len(res)} entries to migrate.")
        for r in res:
            print(f"Migrating Entry {r.entry_id} (Facture {r.id}) from ACH to IMMO")
            conn.execute(text("UPDATE ecritures_journal SET journal_code = 'IMMO' WHERE id = :id"), {"id": r.entry_id})
        
        conn.commit()
        print("Migration complete.")

if __name__ == "__main__":
    migrate_immo_entries()
