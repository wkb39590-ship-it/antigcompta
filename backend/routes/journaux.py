"""
routes/journaux.py — Journal comptable PCM Maroc
Consultation et export des écritures par journal (ACH / VTE / OD / BQ)
"""
import csv
import io
import re
import calendar as cal
from datetime import date
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from database import get_db
from models import JournalEntry, EntryLine, Facture, Employe, Societe, JournalComptable
from schemas import ManualEntryCreate, JournalComptableOut, JournalComptableCreate
from routes.deps import get_current_session

router = APIRouter(prefix="/journaux", tags=["journaux"])

# On garde CODES_JOURNAL uniquement comme fallback ou pour les types par défaut
TYPES_JOURNAL_DEFAUT = {
    "ACHAT": "Journal des Achats",
    "VENTE": "Journal des Ventes",
    "OD": "Opérations Diverses",
    "BANQUE": "Banque",
    "PAIE": "Journal de Paie",
}

@router.get("/config", response_model=List[JournalComptableOut])
def get_journals_config(
    db: Session = Depends(get_db),
    session: dict = Depends(get_current_session)
):
    """Retourne la liste des journaux paramétrés pour la société active."""
    societe_id = session.get("societe_id")
    return db.query(JournalComptable).filter(JournalComptable.societe_id == societe_id).all()

@router.post("/config", response_model=JournalComptableOut)
def create_journal_config(
    req: JournalComptableCreate,
    db: Session = Depends(get_db),
    session: dict = Depends(get_current_session)
):
    """Ajoute un nouveau journal (ex: une nouvelle banque)."""
    societe_id = session.get("societe_id")
    
    # Vérifier si le code existe déjà pour cette société
    existant = db.query(JournalComptable).filter(
        JournalComptable.societe_id == societe_id,
        JournalComptable.code == req.code.upper()
    ).first()
    if existant:
        raise HTTPException(400, f"Le code journal {req.code} existe déjà.")

    nouveau = JournalComptable(
        societe_id=societe_id,
        code=req.code.upper(),
        label=req.label,
        type=req.type.upper()
    )
    db.add(nouveau)
    db.commit()
    db.refresh(nouveau)
    return nouveau


def _entry_to_dict(entry: JournalEntry, journals_map: dict) -> dict:
    """Convertit une écriture journal en dict de réponse."""
    return {
        "id": entry.id,
        "journal_code": entry.journal_code,
        "journal_label": journals_map.get(entry.journal_code, entry.journal_code),
        "entry_date": str(entry.entry_date) if entry.entry_date else None,
        "reference": entry.reference,
        "description": entry.description,
        "is_validated": entry.is_validated,
        "total_debit": float(entry.total_debit) if entry.total_debit else 0.0,
        "total_credit": float(entry.total_credit) if entry.total_credit else 0.0,
        "facture_id": entry.facture_id,
        "entry_lines": [
            {
                "id": el.id,
                "line_order": el.line_order,
                "account_code": el.account_code,
                "account_label": el.account_label,
                "debit": float(el.debit),
                "credit": float(el.credit),
                "tiers_name": el.tiers_name,
                "tiers_ice": el.tiers_ice,
            }
            for el in sorted(entry.entry_lines, key=lambda x: x.line_order or 0)
        ],
    }


def _build_query(db: Session, societe_id: int, journal_code: Optional[str],
                 date_debut: Optional[date], date_fin: Optional[date],
                 valide_seulement: bool):
    """Construit la requête de récupération des écritures."""
    # On filtre par société directement sur l'écriture
    q = db.query(JournalEntry).filter(JournalEntry.societe_id == societe_id)

    if valide_seulement:
        q = q.filter(JournalEntry.is_validated == True)

    if journal_code:
        q = q.filter(JournalEntry.journal_code == journal_code.upper())

    if date_debut:
        q = q.filter(JournalEntry.entry_date >= date_debut)

    if date_fin:
        q = q.filter(JournalEntry.entry_date <= date_fin)

    return q.order_by(JournalEntry.entry_date.asc(), JournalEntry.id.asc())


# ──────────────────────────────────────────────────────────────────────────
# GET /journaux/ — Liste des écritures
# ──────────────────────────────────────────────────────────────────────────
@router.get("/", response_model=dict)
def list_journal(
    journal_code: Optional[str] = Query(None, description="Code du journal (ex: ACH, BQ1)"),
    date_debut: Optional[date] = Query(None, description="Date de début (YYYY-MM-DD)"),
    date_fin: Optional[date] = Query(None, description="Date de fin (YYYY-MM-DD)"),
    valide_seulement: bool = Query(True, description="N'afficher que les écritures validées"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    session: dict = Depends(get_current_session),
):
    """
    Liste les écritures du journal comptable.
    Filtrable par code journal, période, et statut de validation.
    """
    societe_id = session.get("societe_id")

    # Charger les journaux dynamiques de cette société
    journaux = db.query(JournalComptable).filter(JournalComptable.societe_id == societe_id).all()
    journals_map = {j.code: j.label for j in journaux}

    if journal_code and journal_code.upper() not in journals_map:
        # Fallback pour les codes standards si pas encore migrés (sécurité)
        if journal_code.upper() not in ["ACH", "VTE", "OD", "BQ", "PAYE"]:
            raise HTTPException(400, f"Code journal {journal_code} inconnu.")

    q = _build_query(db, societe_id, journal_code, date_debut, date_fin, valide_seulement)

    total = q.count()
    entries = q.offset((page - 1) * per_page).limit(per_page).all()

    # Calcul des totaux pour la page
    total_debit = sum(float(e.total_debit or 0) for e in entries)
    total_credit = sum(float(e.total_credit or 0) for e in entries)

    return {
        "journal_code": journal_code,
        "journal_label": journals_map.get(journal_code, "Tous les journaux") if journal_code else "Tous les journaux",
        "date_debut": str(date_debut) if date_debut else None,
        "date_fin": str(date_fin) if date_fin else None,
        "total_ecritures": total,
        "page": page,
        "per_page": per_page,
        "total_debit": round(total_debit, 2),
        "total_credit": round(total_credit, 2),
        "equilibre": round(abs(total_debit - total_credit), 2) <= 0.01,
        "ecritures": [_entry_to_dict(e, journals_map) for e in entries],
    }


# ──────────────────────────────────────────────────────────────────────────
# GET /journaux/totaux — Totaux par journal
# ──────────────────────────────────────────────────────────────────────────
@router.get("/totaux", response_model=dict)
def get_totaux_par_journal(
    annee: Optional[int] = Query(None, description="Année comptable"),
    mois: Optional[int] = Query(None, ge=1, le=12, description="Mois (1-12)"),
    valide_seulement: bool = Query(True, description="Inclure uniquement les écritures validées"),
    db: Session = Depends(get_db),
    session: dict = Depends(get_current_session),
):
    """Retourne les totaux débit/crédit par journal pour une période."""
    societe_id = session.get("societe_id")

    date_debut = None
    date_fin = None

    if annee and mois:
        import calendar
        last_day = calendar.monthrange(annee, mois)[1]
        date_debut = date(annee, mois, 1)
        date_fin = date(annee, mois, last_day)
    elif annee:
        date_debut = date(annee, 1, 1)
        date_fin = date(annee, 12, 31)

    totaux = {}
    journaux = db.query(JournalComptable).filter(JournalComptable.societe_id == societe_id).all()

    for jnl in journaux:
        q = _build_query(db, societe_id, jnl.code, date_debut, date_fin, valide_seulement=valide_seulement)
        entries = q.all()
        debit = sum(float(e.total_debit or 0) for e in entries)
        credit = sum(float(e.total_credit or 0) for e in entries)
        totaux[jnl.code] = {
            "journal_code": jnl.code,
            "journal_label": jnl.label,
            "nb_ecritures": len(entries),
            "total_debit": round(debit, 2),
            "total_credit": round(credit, 2),
            "equilibre": round(abs(debit - credit), 2) <= 0.01,
        }

    return {
        "periode": f"{annee or 'Toutes les années'}" + (f"/{mois:02d}" if mois else ""),
        "totaux_par_journal": totaux,
    }


# ──────────────────────────────────────────────────────────────────────────
# GET /journaux/export — Export CSV du journal
# ──────────────────────────────────────────────────────────────────────────
@router.get("/export")
def export_journal_csv(
    journal_code: Optional[str] = Query(None, description="ACH | VTE | OD | BQ"),
    date_debut: Optional[date] = Query(None),
    date_fin: Optional[date] = Query(None),
    valide_seulement: bool = Query(True),
    db: Session = Depends(get_db),
    session: dict = Depends(get_current_session),
):
    """Exporte le journal comptable au format CSV."""
    societe_id = session.get("societe_id")

    q = _build_query(db, societe_id, journal_code, date_debut, date_fin, valide_seulement=valide_seulement)
    entries = q.all()

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")

    # En-tête CSV
    writer.writerow([
        "Journal", "Date", "N° Pièce", "Libellé", "Compte", "Libellé Compte",
        "Débit", "Crédit", "Tiers", "ICE Tiers"
    ])

    for entry in entries:
        for el in sorted(entry.entry_lines, key=lambda x: x.line_order or 0):
            writer.writerow([
                entry.journal_code,
                str(entry.entry_date) if entry.entry_date else "",
                entry.reference or "",
                entry.description or "",
                el.account_code or "",
                el.account_label or "",
                str(float(el.debit)).replace(".", ",") if el.debit else "0,00",
                str(float(el.credit)).replace(".", ",") if el.credit else "0,00",
                el.tiers_name or "",
                el.tiers_ice or "",
            ])

    output.seek(0)
    jcode = journal_code or "ALL"
    filename = f"journal_{jcode}_{date.today().isoformat()}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ──────────────────────────────────────────────────────────────────────────
# POST /journaux/{entry_id}/valider — Validation manuelle
# ──────────────────────────────────────────────────────────────────────────
@router.post("/{entry_id}/valider")
def validate_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    session: dict = Depends(get_current_session),
):
    """Valide manuellement une écriture journalière."""
    societe_id = session.get("societe_id")
    entry = db.query(JournalEntry).filter(
        JournalEntry.id == entry_id,
        JournalEntry.societe_id == societe_id
    ).first()

    if not entry:
        raise HTTPException(404, "Écriture introuvable")

    if entry.is_validated:
        return {"message": "Écriture déjà validée", "id": entry.id}

    entry.is_validated = True
    entry.validated_at = func.now()
    entry.validated_by = session.get("username", "system")

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(400, f"Erreur lors de la validation : {e}")

    return {"message": "Écriture validée avec succès", "id": entry.id}


@router.post("/manual")
def create_manual_entry(
    req: ManualEntryCreate,
    db: Session = Depends(get_db),
    context: dict = Depends(get_current_session)
):
    """Crée une écriture journal saisie manuellement par l'agent."""
    societe_id = context['societe_id']
    
    # Vérification balance
    total_debit = sum(l.debit for l in req.lines)
    total_credit = sum(l.credit for l in req.lines)
    
    if abs(total_debit - total_credit) > 0.001:
         raise HTTPException(status_code=400, detail=f"L'écriture n'est pas équilibrée (Debit: {total_debit}, Credit: {total_credit})")

    entry = JournalEntry(
        societe_id=societe_id,
        journal_code=req.journal_code,
        entry_date=req.entry_date,
        reference=req.reference,
        description=req.description,
        total_debit=total_debit,
        total_credit=total_credit,
        is_validated=True
    )
    db.add(entry)
    db.flush()
    
    for i, line in enumerate(req.lines):
        # Ignorer les lignes vides (débit et crédit à 0)
        if line.debit == 0 and line.credit == 0:
            continue
            
        db.add(EntryLine(
            ecriture_journal_id=entry.id,
            line_order=i+1,
            account_code=line.account_code,
            account_label=line.account_label,
            debit=line.debit,
            credit=line.credit,
            tiers_name=line.tiers_name
        ))
    
    db.commit()
    return {"id": entry.id, "message": "Écriture enregistrée avec succès"}


@router.delete("/{entry_id}")
def delete_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    session: dict = Depends(get_current_session)
):
    """Supprime une écriture journal (si non liée à une facture auto)."""
    societe_id = session.get("societe_id")
    entry = db.query(JournalEntry).filter(
        JournalEntry.id == entry_id,
        JournalEntry.societe_id == societe_id
    ).first()

    if not entry:
        raise HTTPException(404, "Écriture introuvable")

    if entry.facture_id:
        raise HTTPException(400, "Impossible de supprimer une écriture liée à une facture (générée automatiquement).")

    # Supprimer les lignes d'abord (cascade normalement gérée par le modèle, mais faisons-le explicitement ou flash)
    db.query(EntryLine).filter(EntryLine.ecriture_journal_id == entry_id).delete()
    db.delete(entry)
    db.commit()
    return {"message": "Écriture supprimée"}


@router.put("/{entry_id}")
def update_manual_entry(
    entry_id: int,
    req: ManualEntryCreate,
    db: Session = Depends(get_db),
    session: dict = Depends(get_current_session)
):
    """Met à jour une écriture journal manuelle."""
    societe_id = session.get("societe_id")
    entry = db.query(JournalEntry).filter(
        JournalEntry.id == entry_id,
        JournalEntry.societe_id == societe_id
    ).first()

    if not entry:
        raise HTTPException(404, "Écriture introuvable")

    if entry.facture_id:
        raise HTTPException(400, "Impossible de modifier une écriture liée à une facture (générée automatiquement).")

    # Recalcul totaux
    total_debit = sum(l.debit for l in req.lines)
    total_credit = sum(l.credit for l in req.lines)

    if abs(total_debit - total_credit) > 0.001:
         raise HTTPException(status_code=400, detail="L'écriture n'est pas équilibrée.")

    # Mise à jour entête
    entry.entry_date = req.entry_date
    entry.reference = req.reference
    entry.description = req.description
    entry.total_debit = total_debit
    entry.total_credit = total_credit
    entry.journal_code = req.journal_code

    # Remplacement des lignes
    db.query(EntryLine).filter(EntryLine.ecriture_journal_id == entry_id).delete()
    
    for i, line in enumerate(req.lines):
        if line.debit == 0 and line.credit == 0:
            continue
        db.add(EntryLine(
            ecriture_journal_id=entry.id,
            line_order=i+1,
            account_code=line.account_code,
            account_label=line.account_label,
            debit=line.debit,
            credit=line.credit,
            tiers_name=line.tiers_name
        ))

    db.commit()
    return {"id": entry.id, "message": "Écriture mise à jour"}


# ──────────────────────────────────────────────────────────────────────────
# GET /journaux/{entry_id}/bulletin-pdf — Bulletin de paie depuis une écriture PAYE
# ──────────────────────────────────────────────────────────────────────────
@router.get("/{entry_id}/bulletin-pdf")
def telecharger_bulletin_depuis_ecriture(
    entry_id: int,
    db: Session = Depends(get_db),
    session: dict = Depends(get_current_session)
):
    """
    Génère un bulletin de paie PDF professionnel directement à partir des lignes
    d'une écriture du journal de paie (PAYE).
    Extrait les montants depuis les comptes PCM :
      6171 → Salaire Brut, 4441 → Net à Payer, 4443 → CNSS, 4444 → IR, 4447 → AMO
    """
    societe_id = session.get("societe_id")
    entry = db.query(JournalEntry).filter(
        JournalEntry.id == entry_id,
        JournalEntry.societe_id == societe_id
    ).first()

    if not entry:
        raise HTTPException(status_code=404, detail="Écriture introuvable.")

    if entry.journal_code != "PAYE":
        raise HTTPException(status_code=400, detail="Cette écriture n'est pas une écriture de paie.")

    # ── Extraction des montants depuis les lignes comptables ──────────────
    lines = sorted(entry.entry_lines, key=lambda x: x.line_order or 0)

    salaire_brut   = 0.0
    charges_pat    = 0.0
    net_a_payer    = 0.0
    cnss_total     = 0.0
    amo_total      = 0.0
    ir_retenu      = 0.0
    nom_salarie    = ""

    rubriques_gains = []
    for line in lines:
        code = (line.account_code or "").strip()
        label = (line.account_label or "").strip().lower()
        debit  = float(line.debit or 0)
        credit = float(line.credit or 0)

        # Matching plus souple pour les GAINS
        is_gain = (code.startswith("6171") or 
                   any(k in label for k in ["brut", "appointement", "salaire", "prime", "indemnité", "gratification"]))
        
        if is_gain and debit > 0:
            rubriques_gains.append({
                "nom": (line.account_label or "Salaire").strip(),
                "montant": debit
            })
            salaire_brut += debit
        elif code.startswith("6174") or "charge" in label or "patronal" in label:
            charges_pat = max(charges_pat, debit)
        elif code.startswith("4441") or "rémunération" in label or "due" in label or "net" in label:
            net_a_payer = max(net_a_payer, credit)
        elif "cnss" in label and "amo" in label:
            cnss_total += credit  # Ligne combinée
        elif code.startswith("4443") or "cnss" in label:
            cnss_total += credit
        elif code.startswith("4447") or "amo" in label:
            amo_total += credit
        elif code.startswith("4444") or "igr" in label or "ir " in label or "impôt" in label:
            ir_retenu = max(ir_retenu, credit)

        # Nom du salarié (présent sur la ligne de net à payer ou d'autres)
        if not nom_salarie and line.tiers_name:
            nom_salarie = line.tiers_name
        elif line.tiers_name and ("rémunération" in label or code.startswith("4441")):
            nom_salarie = line.tiers_name

    # Recalcul des retenues salariales (CNSS + AMO + IR)
    # L'écriture manuelle ne sépare pas toujours CNSS/AMO
    total_retenues = round(salaire_brut - net_a_payer, 2)
    cnss_sal = min(salaire_brut, 6000) * 0.0448
    amo_sal  = salaire_brut * 0.0226
    
    # Si on a un IGR explicite, on l'utilise, sinon on déduit
    if ir_retenu == 0 and total_retenues > 0:
        ir_retenu = max(total_retenues - cnss_sal - amo_sal, 0)
    elif ir_retenu > 0:
        # Ajustement cnss/amo si la somme dépasse les retenues totales à cause d'arrondis
        if cnss_sal + amo_sal + ir_retenu > total_retenues + 1:
            cnss_sal = max(total_retenues - ir_retenu - amo_sal, 0)

    # ── Déduction période depuis la référence ou la date ─────────────────
    mois = entry.entry_date.month if entry.entry_date else date.today().month
    annee = entry.entry_date.year if entry.entry_date else date.today().year

    if entry.reference:
        m = re.search(r'(\d{2})[/-](\d{4})', entry.reference)
        if m:
            try:
                mois = int(m.group(1))
                annee = int(m.group(2))
            except:
                pass

    # ── Récupération infos employé (par nom si possible) ─────────────────
    employe = None
    if nom_salarie:
        n_search = nom_salarie.lower().strip()
        search_words = set(n_search.split())
        tous_employes = db.query(Employe).filter(Employe.societe_id == societe_id).all()
        
        best_emp = None
        best_score = 0
        
        for emp in tous_employes:
            nom_emp = (emp.nom or "").lower()
            prenom_emp = (emp.prenom or "").lower()
            
            # Intersection des mots
            emp_words = set(f"{nom_emp} {prenom_emp}".split())
            score = len(search_words.intersection(emp_words))
            
            # Correspondance exacte (bonus)
            complet_np = f"{nom_emp} {prenom_emp}".strip()
            complet_pn = f"{prenom_emp} {nom_emp}".strip()
            if n_search == complet_np or n_search == complet_pn:
                score += 100
                
            if score > best_score:
                best_score = score
                best_emp = emp
                
        if best_score > 0:
            employe = best_emp

    # Société
    societe = db.query(Societe).filter(Societe.id == societe_id).first()

    # ── Génération PDF via un objet proxy ─────────────────────────────────
    from services.pdf_service import generer_bulletin_pdf

    class BulletinProxy:
        """Proxy pour simuler l'objet BulletinPaie attendu par pdf_service."""
        def __init__(self):
            self.mois            = mois
            self.annee           = annee
            self.rubriques_gains = rubriques_gains
            self.salaire_base    = salaire_brut
            self.prime_anciennete= 0.0
            self.autres_gains    = 0.0
            self.salaire_brut    = salaire_brut
            self.cnss_salarie    = round(cnss_sal, 2)
            self.amo_salarie     = round(amo_sal, 2)
            self.ir_retenu       = round(max(total_retenues - cnss_sal - amo_sal, 0), 2)
            self.total_retenues  = total_retenues
            self.cnss_patronal   = round(salaire_brut * 0.1064, 2)
            self.amo_patronal    = round(salaire_brut * 0.0394, 2)
            self.total_patronal  = charges_pat
            self.salaire_net     = net_a_payer

    class EmployeProxy:
        """Proxy pour simuler l'objet Employe attendu par pdf_service."""
        def __init__(self):
            if employe:
                self.id              = employe.id
                self.nom             = employe.nom
                self.prenom          = employe.prenom or ""
                self.cin             = employe.cin or ""
                self.poste           = employe.poste or "Employé"
                self.date_embauche   = employe.date_embauche
                self.numero_cnss     = employe.numero_cnss or ""
            else:
                parts = nom_salarie.strip().split() if nom_salarie else ["—"]
                self.id              = entry_id
                self.nom             = parts[-1] if len(parts) >= 2 else nom_salarie
                self.prenom          = " ".join(parts[:-1]) if len(parts) >= 2 else ""
                self.cin             = ""
                self.poste           = "Employé"
                self.date_embauche   = None
                self.numero_cnss     = ""

    bulletin_proxy = BulletinProxy()
    employe_proxy  = EmployeProxy()

    pdf_bytes = generer_bulletin_pdf(bulletin_proxy, employe_proxy, societe)

    nom_file = nom_salarie.replace(" ", "_") if nom_salarie else f"entry_{entry_id}"
    filename = f"Bulletin_Paie_{nom_file}_{mois:02d}_{annee}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
