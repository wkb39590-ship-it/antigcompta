import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

# === SQLITE ===
sqlite_path = r'c:\Users\asus\Desktop\nv - Copie (antig)\backend\test.db'
print("=== SQLITE (test.db) ===")
if os.path.exists(sqlite_path):
    size_kb = os.path.getsize(sqlite_path) / 1024
    print(f"Taille: {size_kb:.1f} KB")
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = cursor.fetchall()
    print(f"Nombre de tables: {len(tables)}")
    for row in tables:
        t = row[0]
        try:
            cursor.execute(f"SELECT COUNT(*) FROM [{t}]")
            c = cursor.fetchone()[0]
            print(f"  {t}: {c} lignes")
        except Exception as e:
            print(f"  {t}: ERREUR - {e}")
    conn.close()
else:
    print("FICHIER INTROUVABLE!")

# === POSTGRESQL ===
print("\n=== POSTGRESQL (compta_db) ===")
try:
    import psycopg2
    
    tentatives = [
        {"host": "127.0.0.1", "port": 5432, "dbname": "compta_db", "user": "postgres", "password": "admin123"},
        {"host": "127.0.0.1", "port": 5432, "dbname": "compta_db", "user": "postgres", "password": ""},
        {"host": "localhost",  "port": 5432, "dbname": "compta_db", "user": "postgres", "password": "admin123"},
    ]
    
    pg_conn = None
    for cfg in tentatives:
        try:
            pg_conn = psycopg2.connect(
                host=cfg["host"],
                port=cfg["port"],
                dbname=cfg["dbname"],
                user=cfg["user"],
                password=cfg["password"],
                connect_timeout=5
            )
            print(f"OK - Connecte avec password={cfg['password'] or '(vide)'}")
            break
        except Exception as e:
            print(f"  Echec ({cfg['password'] or 'vide'}): {e}")
    
    if pg_conn:
        pg_cursor = pg_conn.cursor()
        pg_cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            ORDER BY tablename;
        """)
        pg_tables = pg_cursor.fetchall()
        print(f"Nombre de tables: {len(pg_tables)}")
        for row in pg_tables:
            tname = row[0]
            try:
                pg_cursor.execute(f'SELECT COUNT(*) FROM "{tname}"')
                cnt = pg_cursor.fetchone()[0]
                print(f"  {tname}: {cnt} lignes")
            except Exception as e:
                print(f"  {tname}: ERREUR - {e}")
        pg_conn.close()
    else:
        print("IMPOSSIBLE DE SE CONNECTER A POSTGRESQL")

except ImportError:
    print("psycopg2 non installe - pip install psycopg2-binary")

print("\n=== DIAGNOSTIC TERMINE ===")
