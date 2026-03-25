import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://admin:admin123@db:5432/compta_db")
engine = create_engine(DATABASE_URL)

def fix_facture_18():
    with engine.connect() as conn:
        print("Checking Facture 18...")
        
        # 1. Update Facture Header
        conn.execute(text("""
            UPDATE factures 
            SET invoice_type = 'IMMOBILISATION', status = 'CLASSIFIED' 
            WHERE id = 18
        """))
        
        # 2. Update Lines (PCM 2355, Class 2)
        conn.execute(text("""
            UPDATE lignes_factures 
            SET pcm_account_code = '2355', pcm_class = 2, pcm_account_label = 'Matériel informatique'
            WHERE facture_id = 18
        """))
        
        # 3. Handle Journal Entries
        conn.execute(text("DELETE FROM ecritures_journal WHERE facture_id = 18"))
        
        conn.commit()
        print("Facture 18 metadata fixed and old entries deleted.")

if __name__ == "__main__":
    fix_facture_18()
