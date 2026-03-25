import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://admin:admin123@db:5432/compta_db")
engine = create_engine(DATABASE_URL)

def fix_all_lines_18():
    with engine.connect() as conn:
        print("Fixing ALL lines for Facture 18...")
        
        # Update ALL lines for this facture
        res = conn.execute(text("""
            UPDATE lignes_factures 
            SET pcm_account_code = '2355', pcm_class = 2, pcm_account_label = 'Matériel informatique'
            WHERE facture_id = 18
        """))
        print(f"Updated {res.rowcount} lines.")
        
        # Delete entries again for safety
        conn.execute(text("DELETE FROM ecritures_journal WHERE facture_id = 18"))
        
        conn.commit()
        print("Done.")

if __name__ == "__main__":
    fix_all_lines_18()
