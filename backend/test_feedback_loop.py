import sys
import os

# Ajouter le dossier actuel au path pour les imports
sys.path.append(os.getcwd())

from database import SessionLocal
from models import Facture, Societe, SupplierMapping, PcmAccount, InvoiceLine, Cabinet
from services.classification_service import classify_all_lines
from datetime import date

def test_feedback_loop():
    db = SessionLocal()
    print("🚀 Démarrage du test Feedback Loop...")

    try:
        # 1. Configuration initiale : Trouver ou créer une société et un cabinet
        cab = db.query(Cabinet).first()
        if not cab:
            cab = Cabinet(nom="Cabinet Test")
            db.add(cab)
            db.commit()
            db.refresh(cab)

        soc = db.query(Societe).filter(Societe.cabinet_id == cab.id).first()
        if not soc:
            soc = Societe(raison_sociale="Ma Societe Test", cabinet_id=cab.id, ice="123456789012345")
            db.add(soc)
            db.commit()
            db.refresh(soc)

        # 2. S'assurer que le compte PCM de test existe
        test_account_code = "6144"
        account = db.query(PcmAccount).filter(PcmAccount.code == test_account_code).first()
        if not account:
            account = PcmAccount(code=test_account_code, label="Postes et télécommunications", pcm_class=6)
            db.add(account)
            db.commit()

        # Nettoyage d'un éventuel mapping précédent
        db.query(SupplierMapping).filter(SupplierMapping.supplier_ice == "999888777").delete()
        db.commit()

        print(f"--- Étape 1 : Simulation de la première validation ---")
        # Créer une facture pour un fournisseur spécifique (ICE: 999888777)
        f1 = Facture(
            societe_id=soc.id,
            supplier_name="Fournisseur Telecom",
            supplier_ice="999888777",
            status="DRAFT",
            montant_ttc=120.0,
            numero_facture="FAC-001",
            date_facture=date.today()
        )
        db.add(f1)
        db.flush()

        # Ajouter une ligne avec un compte corrigé
        l1 = InvoiceLine(
            facture_id=f1.id,
            description="Abonnement Internet",
            line_amount_ht=100.0,
            pcm_account_code="6111", # Code initial (IA ou autre)
            corrected_account_code="6144" # L'humain a corrigé en 6144
        )
        db.add(l1)
        db.flush()

        # Simuler la route de validation (on réplique la logique de pipeline.py)
        # Enregistrement du mapping
        new_mapping = SupplierMapping(
            cabinet_id=cab.id,
            supplier_ice="999888777",
            pcm_account_code="6144"
        )
        db.add(new_mapping)
        f1.status = "VALIDATED"
        db.commit()
        print(f"✅ Facture 1 validée. Mapping appris : ICE 999888777 -> Compte 6144")

        print(f"\n--- Étape 2 : Test de la classification automatique ---")
        # Créer une NOUVELLE facture pour le MÊME fournisseur
        f2 = Facture(
            societe_id=soc.id,
            supplier_name="Fournisseur Telecom (Bis)",
            supplier_ice="999888777",
            status="EXTRACTED"
        )
        db.add(f2)
        db.flush()
        
        l2 = InvoiceLine(
            facture_id=f2.id,
            description="Consommation Mobile",
            line_amount_ht=50.0
        )
        db.add(l2)
        db.flush()

        # Appeler le service de classification
        print("🔍 Lancement de la classification pour la nouvelle facture...")
        results = classify_all_lines(f2, db)
        
        # Vérifier le résultat
        final_line = db.query(InvoiceLine).filter(InvoiceLine.id == l2.id).first()
        print(f"📈 Résultat classification : {final_line.pcm_account_code} ({final_line.pcm_account_label})")
        print(f"ℹ️ Raison : {final_line.classification_reason}")

        if final_line.pcm_account_code == "6144":
            print("\n🏆 SUCCÈS : Le Feedback Loop a fonctionné ! L'IA a utilisé le compte appris.")
        else:
            print("\n❌ ÉCHEC : Le système n'a pas utilisé le compte appris.")

    except Exception as e:
        print(f"❌ Erreur pendant le test : {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_feedback_loop()
