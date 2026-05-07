"""
Genere un SQL PostgreSQL ROBUSTE depuis SQLite.
- Pas de BEGIN/COMMIT global : chaque table est independante
- Colonnes verifiees selon models.py
- Compatible pgAdmin direct
"""
import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

SQLITE_PATH = r'c:\Users\asus\Desktop\nv - Copie (antig)\backend\test.db'
OUTPUT_PATH = r'c:\Users\asus\Desktop\nv - Copie (antig)\tmp\restore_v2.sql'

# Colonnes BOOLEAN par table (SQLite stocke 0/1, PostgreSQL veut TRUE/FALSE)
BOOLEAN_COLUMNS = {
    "agents": ["is_active", "is_admin", "is_super_admin"],
    "comptes_pcm": ["is_tva_account"],
    "employes": ["affiliee_cnss"],
    "ecritures_journal": ["is_validated"],
    "lignes_factures": ["is_corrected"],
    "lignes_releves": ["is_rapproche"],
    "lignes_amortissement": ["ecriture_generee"],
    "utilisateurs_clients": ["is_active"],
}

# Mapping : nom table SQLite -> nom table PostgreSQL (quand ils different)
TABLE_NAME_MAP = {
    "invoice_lines": "lignes_factures",
    "supplier_mappings": "mappings_fournisseurs",
    "pcm_accounts": "comptes_pcm",  # en cas de doublon
}

# Colonnes exactes de chaque table selon models.py PostgreSQL
# On filtre pour ne garder QUE les colonnes qui existent dans PG
PG_COLUMNS = {
    "cabinets": ["id", "nom", "email", "telephone", "adresse", "logo_path", "created_at"],
    "agents": ["id", "cabinet_id", "username", "email", "password_hash", "nom", "prenom",
               "is_active", "is_admin", "is_super_admin", "created_at", "updated_at"],
    "societes": ["id", "cabinet_id", "raison_sociale", "ice", "if_fiscal", "rc", "patente",
                 "adresse", "cnss", "logo_path", "created_at", "updated_at"],
    "agents_societes": ["agent_id", "societe_id"],
    "comptes_pcm": ["code", "label", "pcm_class", "group_code", "account_type",
                    "is_tva_account", "tva_type"],
    "journaux_comptables": ["id", "societe_id", "code", "label", "type", "created_at", "updated_at"],
    "compteurs_facturation": ["id", "societe_id", "annee", "dernier_numero", "created_at", "updated_at"],
    "factures": ["id", "societe_id", "numero_facture", "date_facture", "due_date",
                 "invoice_type", "supplier_name", "supplier_ice", "supplier_if",
                 "supplier_rc", "supplier_address", "client_name", "client_ice",
                 "client_if", "client_address", "montant_ht", "montant_tva",
                 "montant_ttc", "taux_tva", "devise", "payment_mode", "payment_terms",
                 "ocr_confidence", "extraction_source", "dgi_flags", "status",
                 "validated_by", "validated_at", "reject_reason", "file_path",
                 "file_hash", "fournisseur", "operation_type", "operation_confidence",
                 "if_frs", "ice_frs", "designation", "id_paie", "date_paie",
                 "created_at", "updated_at"],
    "lignes_factures": ["id", "facture_id", "description", "quantity", "tva_rate", "created_at"],
    "invoice_lines":   ["id", "facture_id", "description", "quantity", "tva_rate"],  # alias SQLite
    "ecritures_journal": ["id", "societe_id", "facture_id", "journal_code", "entry_date",
                           "reference", "description", "is_validated", "validated_by",
                           "validated_at", "total_debit", "total_credit", "created_at"],
    "lignes_ecritures": ["id", "ecriture_journal_id", "line_order", "account_code",
                          "account_label", "debit", "credit", "tiers_name", "tiers_ice",
                          "created_at"],
    "employes": ["id", "societe_id", "nom", "prenom", "cin", "date_naissance", "poste",
                 "date_embauche", "type_contrat", "salaire_base", "nb_enfants",
                 "anciennete_pct", "numero_cnss", "affiliee_cnss", "statut",
                 "created_at", "updated_at"],
    "bulletins_paie": ["id", "employe_id", "mois", "annee", "salaire_base",
                       "prime_anciennete", "autres_gains", "salaire_brut",
                       "cnss_salarie", "amo_salarie", "ir_retenu", "total_retenues",
                       "cnss_patronal", "amo_patronal", "total_patronal", "salaire_net",
                       "cout_total_employeur", "journal_entry_id", "statut",
                       "valide_par", "valide_at", "created_at"],
    "lignes_paie": ["id", "bulletin_id", "libelle", "type_ligne", "montant", "taux",
                    "base_calcul", "ordre"],
    "mappings_fournisseurs": ["id", "cabinet_id", "supplier_ice", "pcm_account_code",
                              "created_at", "updated_at"],
    "supplier_mappings":     ["id", "cabinet_id", "supplier_ice", "pcm_account_code",
                              "created_at", "updated_at"],  # alias SQLite
}

# Tables avec cle primaire string (pas de SETVAL)
STRING_PK_TABLES = {"comptes_pcm"}

# Tables avec sequences a resynchroniser
SEQUENCE_TABLES = [
    "cabinets", "agents", "societes", "factures",
    "journaux_comptables", "compteurs_facturation",
    "ecritures_journal", "lignes_ecritures",
    "employes", "bulletins_paie", "lignes_paie", "supplier_mappings",
]

def val_to_sql(v, is_bool=False):
    if v is None:
        return "NULL"
    if is_bool:
        return "TRUE" if (v == 1 or v is True) else "FALSE"
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        return str(v)
    s = str(v).replace("'", "''")
    return f"'{s}'"


conn = sqlite3.connect(SQLITE_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

lines = []
lines.append("-- ============================================================")
lines.append("-- RESTAURATION POSTGRESQL v2 - Sans transaction globale")
lines.append("-- Chaque table s insere independamment")
lines.append("-- ============================================================")
lines.append("")
lines.append("SET session_replication_role = replica;")
lines.append("")

total_inserted = 0
tables_done = []

# Ordre FK correct
TABLE_ORDER = [
    "cabinets",
    "agents",
    "societes",
    "agents_societes",
    "comptes_pcm",
    "journaux_comptables",
    "compteurs_facturation",
    "factures",
    "invoice_lines",
    "ecritures_journal",
    "lignes_ecritures",
    "employes",
    "bulletins_paie",
    "lignes_paie",
    "supplier_mappings",
]

for sqlite_table in TABLE_ORDER:
    # Nom de la table dans PostgreSQL (peut etre different)
    pg_table = TABLE_NAME_MAP.get(sqlite_table, sqlite_table)

    # Recuperer les colonnes SQLite disponibles
    try:
        cursor.execute(f"SELECT * FROM [{sqlite_table}] LIMIT 1")
    except:
        print(f"  SKIP {sqlite_table}: table absente dans SQLite")
        continue
    
    sqlite_cols = [desc[0] for desc in cursor.description] if cursor.description else []
    if not sqlite_cols:
        continue

    # Filtrer : garder seulement les colonnes communes PG <-> SQLite
    # Chercher dans PG_COLUMNS avec le nom PG ou SQLite
    pg_cols = PG_COLUMNS.get(pg_table, PG_COLUMNS.get(sqlite_table, sqlite_cols))
    common_cols = [c for c in pg_cols if c in sqlite_cols]
    table = sqlite_table  # pour compatibilite
    
    if not common_cols:
        print(f"  SKIP {table}: aucune colonne commune")
        continue

    # Lire les donnees
    cols_select = ", ".join([f"[{c}]" for c in common_cols])
    cursor.execute(f"SELECT {cols_select} FROM [{table}]")
    rows = cursor.fetchall()
    
    if not rows:
        print(f"  VIDE {table}: 0 lignes")
        continue

    lines.append(f"-- === {pg_table} (depuis SQLite:{sqlite_table}, {len(rows)} lignes) ===")
    lines.append(f'DELETE FROM "{pg_table}";')
    
    cols_str = ", ".join([f'"{c}"' for c in common_cols])
    
    bool_cols = BOOLEAN_COLUMNS.get(pg_table, BOOLEAN_COLUMNS.get(sqlite_table, []))
    for row in rows:
        values = ", ".join([
            val_to_sql(row[i], is_bool=(common_cols[i] in bool_cols))
            for i in range(len(common_cols))
        ])
        lines.append(f'INSERT INTO "{pg_table}" ({cols_str}) VALUES ({values}) ON CONFLICT DO NOTHING;')
        total_inserted += 1
    
    lines.append("")
    tables_done.append(pg_table)
    print(f"  OK {sqlite_table} -> {pg_table}: {len(rows)} lignes")

conn.close()

# Resynchronisation des sequences
lines.append("-- === Resynchronisation sequences ===")
for t in SEQUENCE_TABLES:
    lines.append(f"""DO $$ BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{t}') THEN
    PERFORM setval(pg_get_serial_sequence('{t}', 'id'),
      COALESCE((SELECT MAX(id) FROM "{t}"), 1));
  END IF;
END $$;""")

lines.append("")
lines.append("SET session_replication_role = DEFAULT;")
lines.append(f"-- TOTAL: {total_inserted} lignes dans {len(tables_done)} tables")
lines.append("SELECT 'RESTAURATION TERMINEE' as statut;")

with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

size_kb = os.path.getsize(OUTPUT_PATH) / 1024
print(f"\nFichier genere: {OUTPUT_PATH}")
print(f"Taille: {size_kb:.1f} KB")
print(f"Total: {total_inserted} lignes, {len(tables_done)} tables")
