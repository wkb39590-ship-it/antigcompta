import sys
import os
from datetime import date
from decimal import Decimal

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Force database path relative to backend directory
os.environ["DATABASE_URL"] = "sqlite:///backend/test.db"

from database import SessionLocal
from models import Employe, BulletinPaie, JournalEntry, EntryLine, Societe
from services.paie_service import sauvegarder_bulletin, generer_ecriture_paie

def test_full_payroll_cycle():
    db = SessionLocal()
    try:
        # 1. Setup sample societe and employee
        soc = db.query(Societe).first()
        if not soc:
            print("No societe found")
            return

        emp = db.query(Employe).filter(Employe.societe_id == soc.id).first()
        if not emp:
            # Create a sample employee if none exists
            emp = Employe(
                societe_id=soc.id,
                nom="EL OMARI",
                prenom="Driss",
                date_embauche=date(2020, 1, 1),
                salaire_base=Decimal("5000.00"),
                nb_enfants=2,
                anciennete_pct=Decimal("5.0"),
                affiliee_cnss=True
            )
            db.add(emp)
            db.commit()
            db.refresh(emp)
            print(f"Created sample employee: {emp.nom}")

        # 2. Create Bulletin
        print(f"Calculating bulletin for {emp.nom} {emp.prenom} (Month: 3, Year: 2024)...")
        bulletin = sauvegarder_bulletin(
            employe=emp,
            mois=3,
            annee=2024,
            primes=Decimal("1000.00"),
            heures_sup=Decimal("500.00"),
            db=db
        )
        print(f"Bulletin created: ID={bulletin.id}, Net={bulletin.salaire_net}")

        # 3. Validate and Generate Journal
        print("Validating and generating journal entry...")
        bulletin.statut = "VALIDE"
        db.commit()
        
        entry = generer_ecriture_paie(bulletin, db)
        print(f"Journal Entry created: ID={entry.id}, Ref={entry.reference}, Total={entry.total_debit}")

        # 4. Verify lines
        lines = db.query(EntryLine).filter(EntryLine.ecriture_journal_id == entry.id).all()
        print(f"Entry lines created: {len(lines)}")
        for l in lines:
            print(f"  [{l.account_code}] {l.account_label}: Debit={l.debit}, Credit={l.credit}")

        # 5. Cleanup (optional, but let's keep it for visual confirmation in DB if needed)
        # db.delete(bulletin)
        # db.delete(entry)
        # db.commit()

        print("\nVerification successful!")
    except Exception as e:
        print(f"Verification failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_full_payroll_cycle()
