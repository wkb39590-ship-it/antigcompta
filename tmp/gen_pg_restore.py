"""
Genere un fichier SQL compatible PostgreSQL depuis SQLite.
"""
import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

SQLITE_PATH = r'c:\Users\asus\Desktop\nv - Copie (antig)\backend\test.db'
OUTPUT_PATH = r'c:\Users\asus\Desktop\nv - Copie (antig)\tmp\restore_postgres.sql'

# Ordre respectant les FK
TABLE_ORDER = [
    "cabinets",
    "agents",
    "societes",
    "agents_societes",
    "comptes_pcm",
    "pcm_accounts",
    "journaux_comptables",
    "compteurs_facturation",
    "ecritures_journal",
    "lignes_ecritures",
    "factures",
    "invoice_lines",
    "employes",
    "bulletins_paie",
    "lignes_paie",
    "supplier_mappings",
    "alembic_version",
]

def sqlite_val_to_pg(val):
    """Convertit une valeur Python en SQL PostgreSQL."""
    if val is None:
        return "NULL"
    if isinstance(val, bool):
        return "TRUE" if val else "FALSE"
    if isinstance(val, int):
        return str(val)
    if isinstance(val, float):
        return str(val)
    # Chaine : echapper les apostrophes
    s = str(val).replace("'", "''")
    return f"'{s}'"

conn = sqlite3.connect(SQLITE_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

lines = []
lines.append("-- ============================================================")
lines.append("-- RESTAURATION POSTGRESQL depuis SQLite (test.db)")
lines.append("-- Generé automatiquement - Projet Zero Saisie Comptable")
lines.append("-- ============================================================")
lines.append("")
lines.append("BEGIN;")
lines.append("")
lines.append("-- Desactiver les contraintes FK temporairement")
lines.append("SET session_replication_role = replica;")
lines.append("")

total_rows = 0

for table in TABLE_ORDER:
    try:
        cursor.execute(f"SELECT * FROM [{table}]")
        rows = cursor.fetchall()
        if not rows:
            continue
        
        columns = [desc[0] for desc in cursor.description]
        cols_str = ", ".join([f'"{c}"' for c in columns])
        
        lines.append(f"-- Table: {table} ({len(rows)} lignes)")
        lines.append(f'DELETE FROM "{table}";')
        
        for row in rows:
            values = ", ".join([sqlite_val_to_pg(v) for v in row])
            lines.append(f'INSERT INTO "{table}" ({cols_str}) VALUES ({values}) ON CONFLICT DO NOTHING;')
            total_rows += 1
        
        lines.append("")
        print(f"  OK: {table} -> {len(rows)} lignes")
        
    except Exception as e:
        print(f"  ERREUR {table}: {e}")

conn.close()

lines.append("")
lines.append("-- Reactiver les contraintes FK")
lines.append("SET session_replication_role = DEFAULT;")
lines.append("")
lines.append("-- Resynchroniser les sequences auto-increment")
lines.append("SELECT setval(pg_get_serial_sequence('cabinets', 'id'), COALESCE(MAX(id), 1)) FROM cabinets;")
lines.append("SELECT setval(pg_get_serial_sequence('agents', 'id'), COALESCE(MAX(id), 1)) FROM agents;")
lines.append("SELECT setval(pg_get_serial_sequence('societes', 'id'), COALESCE(MAX(id), 1)) FROM societes;")
lines.append("SELECT setval(pg_get_serial_sequence('factures', 'id'), COALESCE(MAX(id), 1)) FROM factures;")
lines.append("SELECT setval(pg_get_serial_sequence('comptes_pcm', 'id'), COALESCE(MAX(id), 1)) FROM comptes_pcm;")
lines.append("SELECT setval(pg_get_serial_sequence('journaux_comptables', 'id'), COALESCE(MAX(id), 1)) FROM journaux_comptables;")
lines.append("SELECT setval(pg_get_serial_sequence('employes', 'id'), COALESCE(MAX(id), 1)) FROM employes;")
lines.append("SELECT setval(pg_get_serial_sequence('bulletins_paie', 'id'), COALESCE(MAX(id), 1)) FROM bulletins_paie;")
lines.append("")
lines.append("COMMIT;")
lines.append("")
lines.append(f"-- TOTAL: {total_rows} lignes inserees")

with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

size_kb = os.path.getsize(OUTPUT_PATH) / 1024
print(f"\nFichier SQL genere: {OUTPUT_PATH}")
print(f"Taille: {size_kb:.1f} KB")
print(f"Total: {total_rows} lignes")
print("\nETAPES POUR IMPORTER DANS PGADMIN:")
print("1. Ouvrir pgAdmin")
print("2. Clic droit sur 'compta_db' -> Query Tool")
print("3. Ouvrir le fichier: tmp/restore_postgres.sql")
print("4. Cliquer sur le bouton EXECUTE (F5)")
print("5. Verifier les resultats!")
