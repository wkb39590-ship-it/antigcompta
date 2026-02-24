"""
purge_test_factures.py — Supprime toutes les factures créées par les scripts de test
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal
from models import Facture, InvoiceLine, SupplierMapping

db = SessionLocal()
try:
    # Supprimer les lignes d'abord (clé étrangère)
    lines_deleted = db.query(InvoiceLine).delete()
    print(f"🗑  {lines_deleted} ligne(s) de factures supprimée(s)")

    # Supprimer les factures créées par les scripts de test
    # ICEs utilisés dans les scripts de test :
    test_ices = ["999888777", "123456789012345"]
    deleted = 0
    for ice in test_ices:
        n = db.query(Facture).filter(Facture.supplier_ice == ice).delete()
        deleted += n

    # Supprimer aussi les factures sans ICE et sans nom (orphelines)
    n2 = db.query(Facture).filter(
        Facture.supplier_ice == None,
        Facture.supplier_name == None
    ).delete()
    deleted += n2

    db.commit()
    print(f"✅ {deleted} facture(s) de test supprimée(s)")

    # Afficher ce qui reste
    remaining = db.query(Facture).count()
    print(f"📋 Factures restantes en base : {remaining}")
    
    # Nettoyage des mappings de test
    m = db.query(SupplierMapping).filter(SupplierMapping.supplier_ice == "999888777").delete()
    db.commit()
    print(f"🔄 {m} mapping(s) de test supprimé(s)")
    
    print("\n✅ Base de données nettoyée avec succès !")

except Exception as e:
    db.rollback()
    print(f"❌ Erreur : {e}")
    import traceback; traceback.print_exc()
finally:
    db.close()
