import sys
import os
from sqlalchemy import text
from database import engine, SessionLocal
from models import Base

def fix_database():
    print("--- Fixing Database Schema (Agnostic - Separate Transactions) ---")
    
    def add_column(table, column, type_def):
        print(f"Checking {table}.{column}...")
        with engine.connect() as conn:
            try:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {type_def}"))
                conn.commit()
                print(f"✅ Successfully added {column} to {table}.")
            except Exception as e:
                # conn.rollback() # SQLAlchemy 1.4+ / psycopg usually handles this or it's non-transactional in some dialects
                if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                    print(f"ℹ️  {column} already exists in {table}.")
                else:
                    print(f"⚠️  Could not add {column}: {e}")

    # 1. Add missing columns independently
    add_column("agents", "is_super_admin", "BOOLEAN DEFAULT FALSE")
    add_column("societes", "cnss", "VARCHAR(50)")
    
    # 2. Create missing tables
    print("\n--- Creating missing tables ---")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Base.metadata.create_all(bind=engine) called successfully.")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")

    print("\n✅ Database fix attempt completed.")

if __name__ == "__main__":
    fix_database()
