import os
import sys
import sqlite3
from datetime import date
from decimal import Decimal

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ["DATABASE_URL"] = "sqlite:///backend/test.db"

def reset_db():
    db_path = "backend/test.db"
    if not os.path.exists(db_path):
        print(f"DB not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    tables = ["lignes_paie", "bulletins_paie", "lignes_ecritures", "ecritures_journal"]
    for table in tables:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            print(f"Dropped {table}")
        except Exception as e:
            print(f"Error dropping {table}: {e}")
    conn.commit()
    conn.close()

def create_tables():
    from database import engine, Base
    import models
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

def run_test():
    from database import SessionLocal
    from models import Employe, BulletinPaie, JournalEntry, EntryLine, Societe, LignePaie
    from services.paie_service import sauvegarder_bulletin, generer_ecriture_paie

    db = SessionLocal()
    try:
        # 1. Setup sample societe and employee
        soc = db.query(Societe).first()
        if not soc:
            print("No societe found")
            return

        emp = db.query(Employe).filter(Employe.societe_id == soc.id).first()
        if not emp:
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
        print(f"Cout Total: {bulletin.cout_total_employeur}")

        # 3. Validate and Generate Journal
        print("Validating and generating journal entry...")
        bulletin.statut = "VALIDE"
        db.commit()
        
        entry = generer_ecriture_paie(bulletin, db)
        print(f"Journal Entry created: ID={entry.id}, Ref={entry.reference}, Total={entry.total_debit}")

        # 4. Verify lines
        # Check LignePaie
        lignes_paie = db.query(LignePaie).filter(LignePaie.bulletin_id == bulletin.id).all()
        print(f"Bulletin lines: {len(lignes_paie)}")
        
        # Check EntryLine
        lines = db.query(EntryLine).filter(EntryLine.ecriture_journal_id == entry.id).all()
        print(f"Entry lines created: {len(lines)}")
        for l in lines:
            print(f"  [{l.account_code}] {l.account_label}: Debit={l.debit}, Credit={l.credit}")

        print("\nVerification successful!")
    except Exception as e:
        print(f"Verification failed: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_db()
    create_tables()
    run_test()
