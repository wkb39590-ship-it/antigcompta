import sqlite3
import os
import sys

# Ensure we are in the correct directory
db_path = "c:/Users/asus/Desktop/nv - Copie (antig)/backend/test.db"
if not os.path.exists(db_path):
    print(f"File {db_path} not found.")
    sys.exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("--- Fixing 'agents' table ---")
    # Check if is_super_admin exists
    cursor.execute("PRAGMA table_info(agents)")
    columns = [col[1] for col in cursor.fetchall()]
    if "is_super_admin" not in columns:
        print("Adding 'is_super_admin' to 'agents'...")
        cursor.execute("ALTER TABLE agents ADD COLUMN is_super_admin BOOLEAN DEFAULT 0")
    else:
        print("'is_super_admin' already exists.")

    print("\n--- Creating missing tables ---")
    sys.path.append("c:/Users/asus/Desktop/nv - Copie (antig)/backend")
    from database import engine
    from models import Base
    
    Base.metadata.create_all(bind=engine)
    print("Base.metadata.create_all(bind=engine) called successfully.")

    conn.commit()
    print("\n✅ Database fixed successfully.")

except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()
finally:
    conn.close()
