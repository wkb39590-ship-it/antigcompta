
import sys
import os
from sqlalchemy import select

# Set CWD to backend to allow relative imports inside the app
os.chdir(os.path.join(os.getcwd(), "backend"))
sys.path.append(os.getcwd())

from database import SessionLocal
from models import Facture, InvoiceLine, JournalEntry, EntryLine

def dump_facture(num_facture):
    db = SessionLocal()
    try:
        facture = db.query(Facture).filter(Facture.numero_facture == num_facture).first()
        if not facture:
            # Try partial match if not found
            facture = db.query(Facture).filter(Facture.numero_facture.contains(num_facture.split('/')[-1])).first()
            
        if not facture:
            print(f"Facture {num_facture} not found.")
            return
        
        print(f"--- Facture {facture.numero_facture} (ID: {facture.id}) ---")
        print(f"HT: {facture.montant_ht}, TVA: {facture.montant_tva}, TTC: {facture.montant_ttc}")
        
        print("\nLines:")
        sum_ht = 0
        sum_tva = 0
        for line in facture.lines:
            print(f"  Line {line.line_number}: ID: {line.id}, Desc: {line.description[:30]}, Qty: {line.quantity}, PU: {line.unit_price_ht}, TotalHT: {line.line_amount_ht}, TVA: {line.tva_amount}")
            sum_ht += float(line.line_amount_ht or 0)
            sum_tva += float(line.tva_amount or 0)
        
        print(f"\nSum Line HT: {sum_ht:.4f}")
        print(f"Sum Line TVA: {sum_tva:.4f}")
        total_debits_calc = sum_ht + sum_tva
        print(f"Total Lines Calc: {total_debits_calc:.4f}")
        
        print("\nJournal Entries:")
        for entry in facture.journal_entries:
            print(f"  Entry ID: {entry.id}, Code: {entry.journal_code}, Total Debit: {entry.total_debit}, Total Credit: {entry.total_credit}")
            for el in entry.entry_lines:
                print(f"    - Account {el.account_code: <8} | Debit: {float(el.debit): >10.2f} | Credit: {float(el.credit): >10.2f} | {el.account_label}")
                
    finally:
        db.close()

if __name__ == "__main__":
    dump_facture("FA2026/00893")
