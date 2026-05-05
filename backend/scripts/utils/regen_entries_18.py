import os
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import Facture
from services.entry_generator import generate_journal_entries

def regenerate_entries(facture_id):
    db: Session = SessionLocal()
    try:
        facture = db.query(Facture).filter(Facture.id == facture_id).first()
        if not facture:
            print("Facture not found")
            return
        
        print(f"Generating entries for Facture {facture_id}...")
        entry = generate_journal_entries(facture, db)
        print(f"Success! Entry ID: {entry.id} | Journal: {entry.journal_code}")
        for el in entry.entry_lines:
            print(f"  Line: {el.account_code} | {el.account_label} | D: {el.debit} | C: {el.credit}")
        
    finally:
        db.close()

if __name__ == "__main__":
    regenerate_entries(18)
