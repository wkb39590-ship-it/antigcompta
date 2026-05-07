"""
Script de diagnostic : vérifie PostgreSQL ET SQLite
pour voir où sont tes données.
"""
import sqlite3
import os
import sys

# ─── 1. CHECK SQLITE ──────────────────────────────────────────────────────────
print("=" * 60)
print("📁 ANALYSE DU FICHIER SQLite (test.db)")
print("=" * 60)

sqlite_path = os.path.join(os.path.dirname(__file__), "..", "backend", "test.db")
sqlite_path = os.path.abspath(sqlite_path)

if os.path.exists(sqlite_path):
    size_kb = os.path.getsize(sqlite_path) / 1024
    print(f"✅ Fichier trouvé : {sqlite_path}")
    print(f"   Taille : {size_kb:.1f} KB")
    try:
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()

        # Lister toutes les tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = cursor.fetchall()
        print(f"\n📊 Tables trouvées ({len(tables)}) :")
        
        for (table_name,) in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM [{table_name}]")
                count = cursor.fetchone()[0]
                print(f"   - {table_name:<30} : {count} enregistrements")
            except Exception as e:
                print(f"   - {table_name:<30} : erreur - {e}")
        
        conn.close()
    except Exception as e:
        print(f"❌ Erreur SQLite : {e}")
else:
    print(f"❌ Fichier introuvable : {sqlite_path}")

# ─── 2. CHECK POSTGRESQL ──────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("🐘 ANALYSE DE POSTGRESQL (compta_db)")
print("=" * 60)

try:
    import psycopg2
    
    configs = [
        {"host": "127.0.0.1", "port": 5432, "dbname": "compta_db", "user": "postgres", "password": "admin123"},
        {"host": "127.0.0.1", "port": 5432, "dbname": "compta_db", "user": "postgres", "password": ""},
        {"host": "localhost",  "port": 5432, "dbname": "compta_db", "user": "postgres", "password": "admin123"},
    ]
    
    pg_conn = None
    for cfg in configs:
        try:
            pg_conn = psycopg2.connect(**cfg, connect_timeout=5)
            print(f"✅ Connecté avec : user={cfg['user']}, password={'***' if cfg['password'] else '(vide)'}")
            break
        except Exception as e:
            print(f"   ⚠️  Tentative échouée ({cfg['password'] or 'vide'}) : {e}")
    
    if pg_conn:
        pg_cursor = pg_conn.cursor()
        
        # Lister les tables
        pg_cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            ORDER BY tablename;
        """)
        pg_tables = pg_cursor.fetchall()
        print(f"\n📊 Tables PostgreSQL ({len(pg_tables)}) :")
        
        for (tname,) in pg_tables:
            try:
                pg_cursor.execute(f'SELECT COUNT(*) FROM "{tname}"')
                cnt = pg_cursor.fetchone()[0]
                print(f"   - {tname:<30} : {cnt} enregistrements")
            except Exception as e:
                print(f"   - {tname:<30} : erreur - {e}")
        
        pg_conn.close()
    else:
        print("❌ Impossible de se connecter à PostgreSQL")

except ImportError:
    print("⚠️  psycopg2 non installé. Test PostgreSQL ignoré.")
    print("   → Installe-le avec : pip install psycopg2-binary")

print("\n" + "=" * 60)
print("✅ Diagnostic terminé")
print("=" * 60)
