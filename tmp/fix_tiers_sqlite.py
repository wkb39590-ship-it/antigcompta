import sqlite3
import os

db_path = 'test.db'
if not os.path.exists(db_path):
    print(f"File {db_path} not found")
    exit(1)

conn = sqlite3.connect(db_path, timeout=60)
cursor = conn.cursor()

try:
    # Get all sales entries with their factura and societe info
    query = """
    SELECT 
        le.id, 
        le.tiers_name, 
        f.supplier_name, 
        f.client_name, 
        f.supplier_ice, 
        f.client_ice, 
        f.invoice_type, 
        s.raison_sociale
    FROM lignes_ecritures le
    JOIN ecritures_journal ej ON le.ecriture_journal_id = ej.id
    JOIN factures f ON ej.facture_id = f.id
    JOIN societes s ON f.societe_id = s.id
    WHERE (f.invoice_type = 'VENTE' OR f.invoice_type = 'AVOIR_VENTE' OR f.invoice_type = 'vente')
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    print(f"Found {len(rows)} sales lines to check.")
    
    updates = 0
    for row in rows:
        line_id, current_tiers, sn, cn, sice, cice, itype, raison = row
        
        company_name = (raison or "").lower().strip()
        tname = (current_tiers or "").lower().strip()
        
        # If current Tiers is the company (fuzzy check)
        # We check if the company name is in the tiers name or vice versa
        if company_name and (company_name in tname or tname in company_name):
            sn_clean = (sn or "").lower().strip()
            cn_clean = (cn or "").lower().strip()
            
            new_name = None
            new_ice = None
            
            # Decide what the "Other Party" should be
            # If cn is not company, it's likely the customer
            if cn_clean and not (company_name in cn_clean or cn_clean in company_name):
                new_name = cn
                new_ice = cice
            # Otherwise if sn is not company, it's likely the customer (in case of OCR swap)
            elif sn_clean and not (company_name in sn_clean or sn_clean in company_name):
                new_name = sn
                new_ice = sice
            
            if new_name:
                print(f"Updating line {line_id}: '{current_tiers}' -> '{new_name}'")
                cursor.execute("UPDATE lignes_ecritures SET tiers_name = ?, tiers_ice = ? WHERE id = ?", (new_name, new_ice, line_id))
                updates += 1
            
    conn.commit()
    print(f"Success: {updates} lines updated.")

except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
