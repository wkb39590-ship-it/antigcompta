from database import engine
from sqlalchemy import text
import sys

def migrate():
    print("Attempting to add column cabinet_id to demandes_acces...")
    try:
        with engine.connect() as conn:
            # Use simple SQLite compatible syntax
            conn.execute(text("ALTER TABLE demandes_acces ADD COLUMN cabinet_id INTEGER"))
            conn.commit()
            print("Successfully added column cabinet_id.")
    except Exception as e:
        print(f"Error during migration: {e}")
        # If it fails because column already exists, it's fine
        if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
            print("Column already exists, proceeding.")
        else:
            sys.exit(1)

if __name__ == "__main__":
    migrate()
