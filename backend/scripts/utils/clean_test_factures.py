"""
clean_test_factures.py — Supprime les factures de test avec ICE=None
Lancer depuis le dossier backend/ :  python clean_test_factures.py
"""
from database import SessionLocal
from models import Facture

db = SessionLocal()
try:
    # Afficher toutes les factures existantes
    factures = db.query(Facture).all()
    print(f"\n📋 {len(factures)} facture(s) en base :\n")
    for f in factures:
        print(f"  ID:{f.id} | ICE:{f.supplier_ice} | Nom:{f.supplier_name} | "
              f"Date:{f.date_facture} | TTC:{f.montant_ttc} | Status:{f.status}")

    # Supprimer les factures sans ICE et sans nom (données de test souvent orphelines)
    none_ice = db.query(Facture).filter(
        Facture.supplier_ice == None,
        Facture.supplier_name == None
    ).all()
    
    if none_ice:
        print(f"\n🗑  Suppression de {len(none_ice)} facture(s) sans ICE ni Nom...")
        for f in none_ice:
            db.delete(f)
        db.commit()
        print("✅ Nettoyage terminé.")
    else:
        print("\nℹ️  Aucune facture orpheline (sans ICE ni Nom) trouvée.")
        print("   Pour supprimer TOUTES les factures de test :")
        print("   Modifiez ce script et supprimez par date ou par ID.")

finally:
    db.close()
