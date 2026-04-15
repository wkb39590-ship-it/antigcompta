"""
fix_compte_amort_2355.py — Migration : corrige les écritures 2835 → 28355
                           pour les immobilisations de type matériel informatique (compte_actif_pcm = 2355)

Contexte PCM/CGNC Maroc :
  - 2355  = Matériel informatique (Actif immobilisé)
  - 28355 = Amortissements du matériel informatique (compte miroir CORRECT)
  - 2835  = Amortissements du matériel de bureau et mobilier (≠ informatique)

Usage : python fix_compte_amort_2355.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal
from sqlalchemy import text

def run_diagnostique(db):
    """Affiche l'état avant correction."""
    print("\n" + "="*60)
    print("📋 DIAGNOSTIC AVANT CORRECTION")
    print("="*60)

    # 1. Immobilisations mal configurées
    res = db.execute(text("""
        SELECT id, designation, compte_actif_pcm, compte_amort_pcm, statut
        FROM immobilisations
        WHERE compte_actif_pcm = '2355'
          AND (compte_amort_pcm = '2835' OR compte_amort_pcm IS NULL)
        ORDER BY id
    """))
    rows = res.fetchall()
    print(f"\n🔍 Immobilisations avec compte actif 2355 mais amort. 2835 (ou NULL) : {len(rows)}")
    for r in rows:
        print(f"   ID={r[0]} | {r[1][:50]:<50} | actif={r[2]} | amort={r[3]} | statut={r[4]}")

    # 2. Lignes d'écritures en compte 2835 liées à ces immobilisations
    res2 = db.execute(text("""
        SELECT COUNT(*) FROM lignes_ecritures le
        JOIN ecritures_journal ej ON le.ecriture_journal_id = ej.id
        WHERE le.account_code = '2835'
          AND ej.reference LIKE 'DOT-%'
    """))
    count_lines = res2.scalar()
    print(f"\n🔍 Lignes d'écritures DOT-* en compte 2835 : {count_lines}")

    # 3. Vérification que 28355 existe dans comptes_pcm
    res3 = db.execute(text("SELECT code, label FROM comptes_pcm WHERE code = '28355'"))
    pcm = res3.fetchone()
    if pcm:
        print(f"\n✅ Compte PCM 28355 trouvé : {pcm[1]}")
    else:
        print("\n❌ Compte PCM 28355 ABSENT — il faut lancer seed_pcm.py d'abord !")
        return False

    return True

def run_migration(db):
    """Applique les corrections en base."""
    print("\n" + "="*60)
    print("🔧 CORRECTION EN COURS")
    print("="*60)

    # ── 1. Corriger les immobilisations ──────────────────────────
    res = db.execute(text("""
        UPDATE immobilisations
        SET compte_amort_pcm = '28355'
        WHERE compte_actif_pcm = '2355'
          AND (compte_amort_pcm = '2835' OR compte_amort_pcm IS NULL)
    """))
    nb_immos = res.rowcount
    print(f"\n✏️  {nb_immos} immobilisation(s) corrigées : compte_amort_pcm 2835 → 28355")

    # ── 2. Corriger les lignes d'écritures de dotation (DOT-*) ──
    #    On cible uniquement les écritures OD de type dotation (référence DOT-)
    #    liées à des immobilisations dont l'actif est 2355
    res2 = db.execute(text("""
        UPDATE lignes_ecritures
        SET account_code  = '28355',
            account_label = 'Amortissements du matériel informatique'
        WHERE account_code = '2835'
          AND ecriture_journal_id IN (
              SELECT ej.id FROM ecritures_journal ej
              WHERE ej.reference LIKE 'DOT-%'
                AND ej.journal_code = 'OD'
          )
    """))
    nb_lines = res2.rowcount
    print(f"✏️  {nb_lines} ligne(s) d'écritures corrigées : account_code 2835 → 28355")

    # ── 3. Corriger le label dans les lignes d'acquisition (sécurité) ──
    #    Les lignes de crédit de l'écriture d'acquisition n'ont pas de 2835,
    #    mais on vérifie par sécurité
    res3 = db.execute(text("""
        UPDATE lignes_ecritures
        SET account_label = 'Amortissements du matériel informatique'
        WHERE account_code = '28355'
          AND account_label IN ('Amortissements cumulés', 'Amortissements du matériel de bureau et mobilier')
    """))
    nb_labels = res3.rowcount
    print(f"✏️  {nb_labels} libellé(s) de compte corrigé(s)")

    db.commit()
    print("\n✅ Migration commitée avec succès.")

def run_verification(db):
    """Vérifie l'état après correction."""
    print("\n" + "="*60)
    print("🔎 VÉRIFICATION POST-MIGRATION")
    print("="*60)

    # Vérifier qu'il ne reste plus de 2835 pour les immos 2355
    res = db.execute(text("""
        SELECT COUNT(*) FROM immobilisations
        WHERE compte_actif_pcm = '2355'
          AND compte_amort_pcm = '2835'
    """))
    reste = res.scalar()
    if reste == 0:
        print("\n✅ Aucune immobilisation 2355 ne pointe encore sur 2835.")
    else:
        print(f"\n⚠️  {reste} immobilisation(s) encore incorrectes !")

    # Compter les lignes 28355 pour confirmation
    res2 = db.execute(text("""
        SELECT COUNT(*) FROM lignes_ecritures WHERE account_code = '28355'
    """))
    total_28355 = res2.scalar()
    print(f"📊 Total lignes en compte 28355 après migration : {total_28355}")

    # S'assurer que 2835 n'est utilisé que pour du vrai mobilier (non-informatique)
    res3 = db.execute(text("""
        SELECT COUNT(*) FROM lignes_ecritures le
        JOIN ecritures_journal ej ON le.ecriture_journal_id = ej.id
        WHERE le.account_code = '2835'
          AND ej.reference LIKE 'DOT-%'
    """))
    reste_2835 = res3.scalar()
    if reste_2835 == 0:
        print("✅ Plus aucune écriture DOT-* ne passe par le compte 2835.")
    else:
        print(f"ℹ️  {reste_2835} écriture(s) DOT restantes en 2835 (peut être du mobilier de bureau — vérifier manuellement).")


def main():
    db = SessionLocal()
    try:
        # Diagnostic
        ok = run_diagnostique(db)
        if not ok:
            print("\n❌ Pré-conditions non remplies. Abandonnez et lancez seed_pcm.py d'abord.")
            return

        # Confirmation
        print("\n" + "="*60)
        reponse = input("Voulez-vous appliquer la migration ? (oui/non) : ").strip().lower()
        if reponse not in ("oui", "o", "yes", "y"):
            print("❌ Migration annulée.")
            return

        # Migration
        run_migration(db)

        # Vérification
        run_verification(db)

    except Exception as e:
        db.rollback()
        print(f"\n❌ Erreur — rollback effectué : {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
