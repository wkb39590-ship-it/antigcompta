"""
seed_pcm.py — Seed du référentiel Plan Comptable Marocain (PCM/CGNC)
Usage: python seed_pcm.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal, engine, Base
from models import PcmAccount

# Créer les tables si elles n'existent pas
Base.metadata.create_all(bind=engine)

PCM_ACCOUNTS = [
    # ── Classe 1 — Comptes de financement permanent ──────────────
    ("1111", "Capital social", 1, "11", "PASSIF", False, None),
    ("1181", "Résultats nets en instance d'affectation", 1, "11", "PASSIF", False, None),
    ("1411", "Emprunts obligataires", 1, "14", "PASSIF", False, None),
    ("1481", "Autres dettes de financement", 1, "14", "PASSIF", False, None),

    # ── Classe 2 — Comptes d'actif immobilisé ───────────────────
    ("2210", "Terrains", 2, "22", "ACTIF", False, None),
    ("2321", "Bâtiments", 2, "23", "ACTIF", False, None),
    ("2340", "Matériel de transport", 2, "23", "ACTIF", False, None),
    ("2350", "Matériel de bureau et mobilier", 2, "23", "ACTIF", False, None),
    ("2351", "Mobilier de bureau", 2, "23", "ACTIF", False, None),
    ("2352", "Matériel de bureau", 2, "23", "ACTIF", False, None),
    ("2355", "Matériel informatique", 2, "23", "ACTIF", False, None),
    ("2360", "Agencements et installations", 2, "23", "ACTIF", False, None),
    ("2400", "Immobilisations incorporelles", 2, "24", "ACTIF", False, None),
    
    # ── Classe 2 — Amortissements (28xx) ────────────────────────
    ("2823", "Amortissements des bâtiments", 2, "28", "ACTIF", False, None),
    ("2834", "Amortissements du matériel de transport", 2, "28", "ACTIF", False, None),
    ("2835", "Amortissements du matériel de bureau et mobilier", 2, "28", "ACTIF", False, None),
    ("28351", "Amortissements du mobilier de bureau", 2, "28", "ACTIF", False, None),
    ("28352", "Amortissements du matériel de bureau", 2, "28", "ACTIF", False, None),
    ("28355", "Amortissements du matériel informatique", 2, "28", "ACTIF", False, None),

    # ── Classe 3 — Comptes d'actif circulant ────────────────────
    ("3111", "Marchandises", 3, "31", "ACTIF", False, None),
    ("3121", "Matières premières", 3, "31", "ACTIF", False, None),
    ("3421", "Clients", 3, "34", "TIERS", False, None),
    ("3441", "Personnel — débiteur", 3, "34", "TIERS", False, None),
    ("3451", "État — débiteur", 3, "34", "TIERS", False, None),
    ("34551", "TVA récupérable sur charges", 3, "345", "TIERS", True, "RECUPERABLE"),
    ("34552", "TVA récupérable sur immobilisations", 3, "345", "TIERS", True, "IMMOBILISATION"),
    ("3456", "Créances sur cessions d'immobilisations", 3, "34", "TIERS", False, None),

    # ── Classe 4 — Comptes de passif circulant ──────────────────
    ("4411", "Fournisseurs", 4, "44", "TIERS", False, None),
    ("4417", "Fournisseurs — retenues de garantie", 4, "44", "TIERS", False, None),
    ("4441", "Associés — dividendes à payer", 4, "44", "TIERS", False, None),
    ("4451", "État — TVA facturée", 4, "44", "TIERS", True, "COLLECTEE"),
    ("4455", "TVA facturée", 4, "44", "TIERS", True, "COLLECTEE"),
    ("4456", "État — autres impôts et taxes", 4, "44", "TIERS", False, None),
    ("4481", "Dettes sociales", 4, "44", "TIERS", False, None),

    # ── Classe 5 — Comptes de trésorerie ────────────────────────
    ("5141", "Banques — soldes débiteurs", 5, "51", "ACTIF", False, None),
    ("5161", "Caisse", 5, "51", "ACTIF", False, None),

    # ── Classe 6 — Comptes de charges ───────────────────────────
    ("6111", "Achats de marchandises revendues", 6, "61", "CHARGE", False, None),
    ("6121", "Achats de matières premières", 6, "61", "CHARGE", False, None),
    ("6123", "Achats de fournitures de bureau", 6, "61", "CHARGE", False, None),
    ("6124", "Achats de fournitures d'atelier", 6, "61", "CHARGE", False, None),
    ("6125", "Achats de fournitures informatiques", 6, "61", "CHARGE", False, None),
    ("6131", "Locations et charges locatives", 6, "61", "CHARGE", False, None),
    ("6132", "Redevances de crédit-bail", 6, "61", "CHARGE", False, None),
    ("6133", "Entretien et réparations", 6, "61", "CHARGE", False, None),
    ("6135", "Primes d'assurance", 6, "61", "CHARGE", False, None),
    ("6141", "Études et recherches", 6, "61", "CHARGE", False, None),
    ("6142", "Transports", 6, "61", "CHARGE", False, None),
    ("6143", "Déplacements, missions et réceptions", 6, "61", "CHARGE", False, None),
    ("6144", "Publicité, publications et relations publiques", 6, "61", "CHARGE", False, None),
    ("6145", "Frais postaux et frais de télécommunications", 6, "61", "CHARGE", False, None),
    ("6146", "Cotisations et dons", 6, "61", "CHARGE", False, None),
    ("6147", "Services bancaires", 6, "61", "CHARGE", False, None),
    ("6148", "Autres charges externes", 6, "61", "CHARGE", False, None),
    ("6152", "Honoraires", 6, "61", "CHARGE", False, None),
    ("6161", "Impôts et taxes directs", 6, "61", "CHARGE", False, None),
    ("6171", "Rémunérations du personnel", 6, "61", "CHARGE", False, None),
    ("6174", "Charges sociales", 6, "61", "CHARGE", False, None),
    ("6181", "Dotations d'exploitation aux amortissements des immobilisations incorporelles", 6, "61", "CHARGE", False, None),
    ("6193", "Dotations d'exploitation aux amortissements des immobilisations corporelles", 6, "61", "CHARGE", False, None),
    ("6300", "Impôts sur les résultats", 6, "63", "CHARGE", False, None),

    # ── Classe 7 — Comptes de produits ──────────────────────────
    ("7111", "Ventes de marchandises", 7, "71", "PRODUIT", False, None),
    ("7121", "Ventes de produits finis", 7, "71", "PRODUIT", False, None),
    ("7122", "Ventes de produits intermédiaires", 7, "71", "PRODUIT", False, None),
    ("7124", "Ventes de déchets", 7, "71", "PRODUIT", False, None),
    ("7161", "Ventes de services", 7, "71", "PRODUIT", False, None),
    ("7181", "Produits accessoires", 7, "71", "PRODUIT", False, None),
    ("7300", "Produits financiers", 7, "73", "PRODUIT", False, None),
    ("7500", "Produits non courants", 7, "75", "PRODUIT", False, None),

    # ── Classe 8 — Comptes de résultats ─────────────────────────
    ("8100", "Résultat d'exploitation", 8, "81", "PRODUIT", False, None),
    ("8200", "Résultat financier", 8, "82", "PRODUIT", False, None),
    ("8800", "Résultat net de l'exercice", 8, "88", "PRODUIT", False, None),
]


def seed():
    db = SessionLocal()
    try:
        count = 0
        for code, label, pcm_class, group_code, account_type, is_tva, tva_type in PCM_ACCOUNTS:
            existing = db.query(PcmAccount).filter(PcmAccount.code == code).first()
            if not existing:
                db.add(PcmAccount(
                    code=code,
                    label=label,
                    pcm_class=pcm_class,
                    group_code=group_code,
                    account_type=account_type,
                    is_tva_account=is_tva,
                    tva_type=tva_type,
                ))
                count += 1
            else:
                # Mise à jour des libellés et types si déjà présent
                existing.label = label
                existing.pcm_class = pcm_class
                existing.group_code = group_code
                existing.account_type = account_type
                existing.is_tva_account = is_tva
                existing.tva_type = tva_type
                count += 1
        db.commit()
        print(f"✅ Seed PCM terminé: {count} comptes insérés ({len(PCM_ACCOUNTS)} total)")
    except Exception as e:
        db.rollback()
        print(f"❌ Erreur seed: {e}")
        raise
    finally:
        db.close()


def create_tables():
    """Crée toutes les tables en base."""
    Base.metadata.create_all(bind=engine)
    print("✅ Tables créées")


if __name__ == "__main__":
    print("🔧 Création des tables...")
    create_tables()
    print("🌱 Seed des comptes PCM...")
    seed()
