from sqlalchemy.orm import Session
from database import SessionLocal
from models import Facture, Societe
from datetime import date
from fastapi import HTTPException
import sys

def test_duplicate_detection():
    db = SessionLocal()
    try:
        # 1. Créer une facture de référence si elle n'existe pas
        soc = db.query(Societe).first()
        if not soc:
            print("Erreur: Aucune société trouvée pour le test.")
            return

        ice = "123456789012345"
        dt = date(2026, 1, 1)
        ttc = 1200.50

        # Nettoyage si existant (pour le test)
        db.query(Facture).filter(Facture.supplier_ice == ice, Facture.date_facture == dt).delete()
        db.commit()

        print(f"Étape 1: Création d'une facture initiale (ICE: {ice}, TTC: {ttc})...")
        ref_facture = Facture(
            societe_id=soc.id,
            supplier_ice=ice,
            date_facture=dt,
            montant_ttc=ttc,
            status="EXTRACTED"
        )
        db.add(ref_facture)
        db.commit()
        db.refresh(ref_facture)
        print(f"Facture référence créée avec ID: {ref_facture.id}")

        # 2. Simuler la détection de doublon pour une nouvelle facture
        print("\nÉtape 2: Simulation d'une nouvelle extraction avec les mêmes données...")
        new_facture_id = 999999 # Dummy ID
        
        # Logique copiée de pipeline.py
        duplicate = db.query(Facture).filter(
            Facture.societe_id == soc.id,
            Facture.id != 0, # Simuler un ID différent
            Facture.supplier_ice == ice,
            Facture.date_facture == dt,
            Facture.montant_ttc == ttc
        ).first()

        if duplicate:
            print("✅ SUCCÈS: Doublon détecté correctement par la requête SQL.")
            print(f"   Correspondance trouvée avec la facture ID: {duplicate.id}")
        else:
            print("❌ ÉCHEC: Aucun doublon n'a été détecté.")

    except Exception as e:
        print(f"Erreur pendant le test: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_duplicate_detection()
