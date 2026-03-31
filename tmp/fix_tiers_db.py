import sys
import os

# Add backend to path
backend_path = r'c:\Users\asus\Desktop\nv - Copie (antig)\backend'
if backend_path not in sys.path:
    sys.path.append(backend_path)

from database import SessionLocal
from models import JournalEntry, EntryLine, Facture, Societe

def fix_all_vte_tiers():
    db = SessionLocal()
    try:
        # On récupère toutes les écritures liées à une facture
        entries = db.query(JournalEntry).filter(JournalEntry.facture_id != None).all()
        print(f"Found {len(entries)} entries with factures. Starting fix...")
        
        count = 0
        for e in entries:
            f = e.facture
            if not f:
                continue
            
            it = (f.invoice_type or "").upper()
            if it not in ["VENTE", "AVOIR_VENTE"]:
                continue
            
            # Company name to avoid
            company_name = (f.societe.raison_sociale or "").lower().strip()
            
            # Get all lines for this entry
            lines = db.query(EntryLine).filter(EntryLine.ecriture_journal_id == e.id).all()
            
            for line in lines:
                tname = (line.tiers_name or "").lower().strip()
                
                # If current Tiers name contains company name, we need to swap it
                if company_name and (company_name in tname or tname in company_name):
                    sn = (f.supplier_name or f.fournisseur or "").lower().strip()
                    cn = (f.client_name or "").lower().strip()
                    
                    # Logic: pick the one that is NOT the company name
                    if cn and not (company_name in cn or cn in company_name):
                        line.tiers_name = f.client_name
                        line.tiers_ice = f.client_ice
                    elif sn and not (company_name in sn or sn in company_name):
                        line.tiers_name = f.supplier_name
                        line.tiers_ice = f.supplier_ice
                    else:
                        # If both contain company name or both empty, fallback
                        line.tiers_name = "Client"
                    
                    count += 1
            
            db.commit() # Commit per entry for safety
            
        print(f"Success: {count} lines updated.")
    except Exception as ex:
        print(f"Error: {ex}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_all_vte_tiers()
