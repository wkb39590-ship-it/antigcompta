
import os
from sqlalchemy import create_engine, text

# Configuration de la base de données
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://admin:admin123@localhost:5454/compta_db"  # Use localhost:5454 if running from outside Docker
)

engine = create_engine(DATABASE_URL)

def apply_migration():
    columns_to_add = [
        ("fournisseur", "VARCHAR"),
        ("operation_type", "VARCHAR(50)"),
        ("operation_confidence", "FLOAT"),
        ("if_frs", "VARCHAR(50)"),
        ("ice_frs", "VARCHAR(50)"),
        ("designation", "VARCHAR(255)"),
        ("id_paie", "VARCHAR(50)"),
        ("date_paie", "DATE"),
        ("updated_at", "TIMESTAMP"),
        ("file_hash", "VARCHAR(64)"),
        ("ded_file_path", "VARCHAR(255)"),
        ("ded_pdf_path", "VARCHAR(255)"),
        ("ded_xlsx_path", "VARCHAR(255)"),
    ]

    print(f"Connecting to database at {DATABASE_URL}...")
    
    with engine.connect() as conn:
        for col_name, col_type in columns_to_add:
            try:
                # Check if column exists
                check_query = text(f"""
                    SELECT count(*) 
                    FROM information_schema.columns 
                    WHERE table_name='factures' AND column_name='{col_name}';
                """)
                exists = conn.execute(check_query).scalar()
                
                if not exists:
                    print(f"Adding column {col_name}...")
                    conn.execute(text(f"ALTER TABLE factures ADD COLUMN {col_name} {col_type};"))
                    conn.commit()
                    print(f"Column {col_name} added successfully.")
                else:
                    print(f"Column {col_name} already exists.")
            except Exception as e:
                print(f"Error adding {col_name}: {e}")
                conn.rollback()

if __name__ == "__main__":
    apply_migration()
