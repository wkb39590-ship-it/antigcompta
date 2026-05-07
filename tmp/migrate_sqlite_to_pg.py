"""
MIGRATION : SQLite (test.db) --> PostgreSQL (compta_db)
Recupere toutes les donnees du fichier test.db et les insere dans PostgreSQL.
"""
import sqlite3
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

SQLITE_PATH = r'c:\Users\asus\Desktop\nv - Copie (antig)\backend\test.db'

# Ordre d'insertion respectant les cles etrangeres
TABLE_ORDER = [
    "cabinets",
    "agents",
    "societes",
    "agents_societes",
    "agent_societes",
    "comptes_pcm",
    "pcm_accounts",
    "journaux_comptables",
    "compteurs_facturation",
    "utilisateurs_clients",
    "demandes_acces",
    "factures",
    "invoice_lines",
    "lignes_factures",
    "ecritures_comptables",
    "ecritures_journal",
    "ecritures_lignes",
    "lignes_ecritures",
    "entry_lines",
    "journal_entries",
    "releves_bancaires",
    "lignes_releves",
    "employes",
    "bulletins_paie",
    "lignes_paie",
    "immobilisations",
    "lignes_amortissement",
    "documents_transmis",
    "mappings_fournisseurs",
    "supplier_mappings",
    "action_logs",
    "alembic_version",
]

def get_sqlite_data():
    """Recupere toutes les donnees depuis SQLite."""
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    all_tables = [row[0] for row in cursor.fetchall()]
    
    data = {}
    for table in all_tables:
        try:
            cursor.execute(f"SELECT * FROM [{table}]")
            rows = cursor.fetchall()
            if rows:
                columns = [desc[0] for desc in cursor.description]
                data[table] = {
                    "columns": columns,
                    "rows": [list(row) for row in rows]
                }
                print(f"  SQLite lu: {table} -> {len(rows)} lignes")
            else:
                print(f"  SQLite vide: {table} -> 0 lignes (ignore)")
        except Exception as e:
            print(f"  ERREUR lecture {table}: {e}")
    
    conn.close()
    return data


def migrate_to_postgres(data):
    """Insere les donnees dans PostgreSQL."""
    try:
        import psycopg2
        import psycopg2.extras
    except ImportError:
        print("ERREUR: psycopg2 non installe!")
        print("Installez-le: pip install psycopg2-binary")
        return False

    # Connexion PostgreSQL
    pg_conn = None
    configs = [
        {"host": "127.0.0.1", "port": 5432, "dbname": "compta_db", "user": "postgres", "password": "admin123"},
        {"host": "localhost",  "port": 5432, "dbname": "compta_db", "user": "postgres", "password": "admin123"},
        {"host": "127.0.0.1", "port": 5432, "dbname": "compta_db", "user": "postgres", "password": ""},
    ]
    
    for cfg in configs:
        try:
            pg_conn = psycopg2.connect(
                host=cfg["host"], port=cfg["port"],
                dbname=cfg["dbname"], user=cfg["user"],
                password=cfg["password"], connect_timeout=5
            )
            print(f"\nConnecte a PostgreSQL (password: {'***' if cfg['password'] else 'vide'})")
            break
        except Exception as e:
            print(f"  Tentative echouee: {e}")
    
    if not pg_conn:
        print("\nIMPOSSIBLE DE CONNECTER A POSTGRESQL")
        print("Verifiez que PostgreSQL est demarre et que le mot de passe est correct.")
        return False

    cursor = pg_conn.cursor()
    
    # Verifier les tables existantes dans PostgreSQL
    cursor.execute("""
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public' ORDER BY tablename;
    """)
    pg_tables = [row[0] for row in cursor.fetchall()]
    print(f"\nTables PostgreSQL disponibles: {len(pg_tables)}")
    
    success_count = 0
    error_count = 0
    
    # Inserer dans l'ordre defini
    ordered_tables = [t for t in TABLE_ORDER if t in data]
    # Ajouter les tables non listees a la fin
    for t in data:
        if t not in ordered_tables:
            ordered_tables.append(t)
    
    # Desactiver les contraintes FK temporairement
    cursor.execute("SET session_replication_role = replica;")
    
    for table in ordered_tables:
        if table not in data:
            continue
        if table not in pg_tables:
            print(f"  SKIP {table}: table inexistante dans PostgreSQL")
            continue
        
        table_data = data[table]
        columns = table_data["columns"]
        rows = table_data["rows"]
        
        if not rows:
            continue
        
        try:
            # Vider la table avant d'inserer (eviter les doublons)
            cursor.execute(f'DELETE FROM "{table}";')
            deleted = cursor.rowcount
            
            # Construire la requete INSERT
            cols_str = ", ".join([f'"{c}"' for c in columns])
            placeholders = ", ".join(["%s"] * len(columns))
            insert_sql = f'INSERT INTO "{table}" ({cols_str}) VALUES ({placeholders}) ON CONFLICT DO NOTHING;'
            
            inserted = 0
            for row in rows:
                try:
                    cursor.execute(insert_sql, row)
                    inserted += 1
                except Exception as row_err:
                    print(f"    Ligne ignoree dans {table}: {row_err}")
            
            pg_conn.commit()
            print(f"  OK {table}: {inserted}/{len(rows)} lignes inserees (supprime: {deleted})")
            success_count += 1
            
        except Exception as e:
            pg_conn.rollback()
            print(f"  ERREUR {table}: {e}")
            error_count += 1
    
    # Reactiver les contraintes
    cursor.execute("SET session_replication_role = DEFAULT;")
    
    # Resynchroniser les sequences
    print("\n--- Resynchronisation des sequences ---")
    cursor.execute("""
        SELECT sequence_name FROM information_schema.sequences 
        WHERE sequence_schema = 'public';
    """)
    sequences = cursor.fetchall()
    for (seq,) in sequences:
        # Trouver la table/colonne associee
        try:
            cursor.execute(f"""
                SELECT setval('{seq}', COALESCE((
                    SELECT MAX(id) FROM "{seq.replace('_id_seq', '').replace('_seq', '')}"
                ), 1));
            """)
        except:
            pass
    pg_conn.commit()
    pg_conn.close()
    
    print(f"\n=== MIGRATION TERMINEE ===")
    print(f"  Succes: {success_count} tables")
    print(f"  Erreurs: {error_count} tables")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("MIGRATION SQLite -> PostgreSQL")
    print("=" * 60)
    
    print(f"\nLecture de: {SQLITE_PATH}")
    if not os.path.exists(SQLITE_PATH):
        print("ERREUR: Fichier test.db introuvable!")
        sys.exit(1)
    
    print("\n--- Lecture SQLite ---")
    data = get_sqlite_data()
    
    total_rows = sum(len(v["rows"]) for v in data.values())
    print(f"\nTotal: {len(data)} tables avec donnees, {total_rows} lignes a migrer")
    
    print("\n--- Migration vers PostgreSQL ---")
    success = migrate_to_postgres(data)
    
    if not success:
        print("\n>>> SOLUTION ALTERNATIVE: Export SQL depuis SQLite <<<")
        export_path = r'c:\Users\asus\Desktop\nv - Copie (antig)\tmp\backup_from_sqlite.sql'
        with open(export_path, 'w', encoding='utf-8') as f:
            conn = sqlite3.connect(SQLITE_PATH)
            for line in conn.iterdump():
                f.write(line + '\n')
            conn.close()
        print(f"Backup SQL exporte vers: {export_path}")
        print("Importez ce fichier manuellement dans pgAdmin.")
