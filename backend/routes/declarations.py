# # backend/routes/declarations.py
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session

# from database import get_db
# from models import DeclarationMensuelle
# from services.declaration_service import validate_declaration

# router = APIRouter(prefix="/declarations", tags=["declarations"])


# @router.get("/{annee}/{mois}")
# def get_declaration(annee: int, mois: int, db: Session = Depends(get_db)):
#     dec = db.query(DeclarationMensuelle).filter_by(annee=annee, mois=mois).first()
#     if not dec:
#         return {
#             "annee": annee,
#             "mois": mois,
#             "statut": "brouillon",
#             "lignes": [],
#             "totaux": {"ht": 0.0, "tva": 0.0, "ttc": 0.0},
#         }

#     lignes = []
#     for l in dec.lignes:
#         lignes.append({
#             "FACT_NUM": l.fact_num,
#             "DESIGNATION": l.designation,
#             "M_HT": l.m_ht,
#             "TVA": l.tva,
#             "M_TTC": l.m_ttc,
#             "IF": l.if_frs,
#             "LIB_FRSS": l.lib_frss,
#             "ICE_FRS": l.ice_frs,
#             "TAUX": l.taux,
#             "DATE_PAI": str(l.date_pai) if l.date_pai else None,
#             "DATE_FAC": str(l.date_fac) if l.date_fac else None,
#             "facture_id": l.facture_id,
#         })

#     return {
#         "annee": dec.annee,
#         "mois": dec.mois,
#         "statut": dec.statut,
#         "lignes": lignes,
#         "totaux": {"ht": dec.total_ht, "tva": dec.total_tva, "ttc": dec.total_ttc},
#     }


# @router.post("/{annee}/{mois}/valider")
# def valider_declaration_route(annee: int, mois: int, db: Session = Depends(get_db)):
#     try:
#         dec = validate_declaration(db, annee, mois)
#         db.commit()
#         db.refresh(dec)
#         return {
#             "message": "Déclaration mensuelle validée (verrouillée)",
#             "annee": dec.annee,
#             "mois": dec.mois,
#             "statut": dec.statut,
#             "totaux": {"ht": dec.total_ht, "tva": dec.total_tva, "ttc": dec.total_ttc},
#         }
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=400, detail=str(e))








# # routes/declarations.py
# from datetime import date, datetime
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session

# from database import get_db
# from models import Facture, DeclarationMensuelle, DeclarationLigne
# from schemas import DeclarationOut


# from fastapi.responses import StreamingResponse
# from services.declaration_exports import build_excel, build_pdf

# router = APIRouter(prefix="/declarations", tags=["declarations"])


# def _month_range(annee: int, mois: int):
#     if mois < 1 or mois > 12:
#         raise HTTPException(status_code=400, detail="mois doit être entre 1 et 12")

#     if mois == 12:
#         start = date(annee, 12, 1)
#         end = date(annee + 1, 1, 1)
#     else:
#         start = date(annee, mois, 1)
#         end = date(annee, mois + 1, 1)
#     return start, end


# @router.post("/{annee}/{mois}/generer", response_model=DeclarationOut)
# def generer_declaration(annee: int, mois: int, db: Session = Depends(get_db)):
#     start, end = _month_range(annee, mois)

#     decl = db.query(DeclarationMensuelle).filter(
#         DeclarationMensuelle.annee == annee,
#         DeclarationMensuelle.mois == mois
#     ).first()

#     if not decl:
#         decl = DeclarationMensuelle(annee=annee, mois=mois)
#         db.add(decl)
#         db.commit()
#         db.refresh(decl)

#     factures = db.query(Facture).filter(
#         Facture.statut == "validee",
#         Facture.date_facture >= start,
#         Facture.date_facture < end
#     ).all()

#     total_ht = 0.0
#     total_tva = 0.0
#     total_ttc = 0.0

#     for f in factures:
#         ligne = db.query(DeclarationLigne).filter(
#             DeclarationLigne.declaration_id == decl.id,
#             DeclarationLigne.facture_id == f.id
#         ).first()

#         if not ligne:
#             ligne = DeclarationLigne(declaration_id=decl.id, facture_id=f.id)
#             db.add(ligne)

#         ligne.fact_num = f.numero_facture
#         ligne.designation = f.designation
#         ligne.m_ht = f.montant_ht
#         ligne.tva = f.montant_tva
#         ligne.m_ttc = f.montant_ttc
#         ligne.if_frs = f.if_frs
#         ligne.lib_frss = f.fournisseur
#         ligne.ice_frs = f.ice_frs
#         ligne.taux = f.taux_tva
#         ligne.date_pai = f.date_paie
#         ligne.date_fac = f.date_facture

#         total_ht += float(f.montant_ht or 0)
#         total_tva += float(f.montant_tva or 0)
#         total_ttc += float(f.montant_ttc or 0)

#     decl.total_ht = round(total_ht, 2)
#     decl.total_tva = round(total_tva, 2)
#     decl.total_ttc = round(total_ttc, 2)
#     decl.updated_at = datetime.utcnow()

#     db.commit()
#     db.refresh(decl)
#     return decl


# @router.get("/{annee}/{mois}", response_model=DeclarationOut)
# def get_declaration(annee: int, mois: int, db: Session = Depends(get_db)):
#     decl = db.query(DeclarationMensuelle).filter(
#         DeclarationMensuelle.annee == annee,
#         DeclarationMensuelle.mois == mois
#     ).first()

#     if not decl:
#         raise HTTPException(status_code=404, detail="Déclaration introuvable. Lance /generer d'abord.")

#     return decl


# @router.get("/{annee}/{mois}/excel")
# def export_declaration_excel(annee: int, mois: int, db: Session = Depends(get_db)):
#     decl = db.query(DeclarationMensuelle).filter(
#         DeclarationMensuelle.annee == annee,
#         DeclarationMensuelle.mois == mois
#     ).first()
#     if not decl:
#         raise HTTPException(status_code=404, detail="Déclaration introuvable")

#     # Convert to dict structure used by builders
#     decl_dict = {
#         "id": decl.id,
#         "annee": decl.annee,
#         "mois": decl.mois,
#         "total_ht": decl.total_ht,
#         "total_tva": decl.total_tva,
#         "total_ttc": decl.total_ttc,
#         "lignes": [
#             {
#                 "fact_num": l.fact_num,
#                 "designation": l.designation,
#                 "m_ht": l.m_ht,
#                 "tva": l.tva,
#                 "m_ttc": l.m_ttc,
#                 "if_frs": l.if_frs,
#                 "lib_frss": l.lib_frss,
#                 "ice_frs": l.ice_frs,
#                 "taux": l.taux,
#                 "date_pai": l.date_pai,
#                 "date_fac": l.date_fac,
#             }
#             for l in decl.lignes
#         ]
#     }

#     fileobj = build_excel(decl_dict)
#     filename = f"declaration_{annee}_{mois:02d}.xlsx"

#     return StreamingResponse(
#         fileobj,
#         media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         headers={"Content-Disposition": f'attachment; filename="{filename}"'}
#     )


# @router.get("/{annee}/{mois}/pdf")
# def export_declaration_pdf(annee: int, mois: int, db: Session = Depends(get_db)):
#     decl = db.query(DeclarationMensuelle).filter(
#         DeclarationMensuelle.annee == annee,
#         DeclarationMensuelle.mois == mois
#     ).first()
#     if not decl:
#         raise HTTPException(status_code=404, detail="Déclaration introuvable")

#     decl_dict = {
#         "id": decl.id,
#         "annee": decl.annee,
#         "mois": decl.mois,
#         "total_ht": decl.total_ht,
#         "total_tva": decl.total_tva,
#         "total_ttc": decl.total_ttc,
#         "lignes": [
#             {
#                 "fact_num": l.fact_num,
#                 "designation": l.designation,
#                 "m_ht": l.m_ht,
#                 "tva": l.tva,
#                 "m_ttc": l.m_ttc,
#                 "if_frs": l.if_frs,
#                 "lib_frss": l.lib_frss,
#                 "ice_frs": l.ice_frs,
#                 "taux": l.taux,
#                 "date_pai": l.date_pai,
#                 "date_fac": l.date_fac,
#             }
#             for l in decl.lignes
#         ]
#     }

#     fileobj = build_pdf(decl_dict)
#     filename = f"declaration_{annee}_{mois:02d}.pdf"

#     return StreamingResponse(
#         fileobj,
#         media_type="application/pdf",
#         headers={"Content-Disposition": f'attachment; filename="{filename}"'}
#     )














# # routes/declarations.py
# import os
# from pathlib import Path
# from datetime import date
# from typing import List, Dict, Any, Optional, Tuple

# from fastapi import APIRouter, Depends, HTTPException
# from fastapi.responses import FileResponse
# from sqlalchemy.orm import Session
# from sqlalchemy import func

# from database import get_db
# from models import Facture, DeclarationMensuelle, DeclarationLigne

# from openpyxl import Workbook
# from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

# from reportlab.lib.pagesizes import A4, landscape
# from reportlab.pdfgen import canvas
# from reportlab.lib.units import mm


# router = APIRouter(prefix="/declarations", tags=["declarations"])

# EXPORT_DIR = Path(os.getenv("EXPORT_DIR", "exports"))
# EXPORT_DIR.mkdir(parents=True, exist_ok=True)

# HEADERS = [
#     "FACT_NUM", "DESIGNATION", "M_HT", "TVA", "M_TTC",
#     "IF", "LIB_FRSS", "ICE_FRS", "TAUX", "DATE_PAI", "DATE_FAC"
# ]


# def _get_or_create_declaration(db: Session, annee: int, mois: int) -> DeclarationMensuelle:
#     decl = (
#         db.query(DeclarationMensuelle)
#         .filter(DeclarationMensuelle.annee == annee, DeclarationMensuelle.mois == mois)
#         .first()
#     )
#     if decl:
#         return decl
#     decl = DeclarationMensuelle(annee=annee, mois=mois, statut="brouillon", total_ht=0, total_tva=0, total_ttc=0)
#     db.add(decl)
#     db.commit()
#     db.refresh(decl)
#     return decl


# def _recompute_totals(db: Session, decl_id: int) -> Tuple[float, float, float]:
#     total_ht, total_tva, total_ttc = (
#         db.query(
#             func.coalesce(func.sum(DeclarationLigne.m_ht), 0.0),
#             func.coalesce(func.sum(DeclarationLigne.tva), 0.0),
#             func.coalesce(func.sum(DeclarationLigne.m_ttc), 0.0),
#         )
#         .filter(DeclarationLigne.declaration_id == decl_id)
#         .one()
#     )
#     total_ht = float(total_ht or 0)
#     total_tva = float(total_tva or 0)
#     total_ttc = float(total_ttc or 0)

#     db.query(DeclarationMensuelle).filter(DeclarationMensuelle.id == decl_id).update(
#         dict(total_ht=total_ht, total_tva=total_tva, total_ttc=total_ttc)
#     )
#     db.commit()
#     return total_ht, total_tva, total_ttc


# def _build_lines_from_factures(db: Session, decl: DeclarationMensuelle) -> List[DeclarationLigne]:
#     """
#     Reconstruit les lignes de déclaration à partir des factures du mois (statut=validee).
#     ✅ facture_id sera toujours renseigné => plus de NOT NULL violation.
#     """
#     # supprimer les lignes existantes pour éviter doublons / données obsolètes
#     db.query(DeclarationLigne).filter(DeclarationLigne.declaration_id == decl.id).delete()
#     db.commit()

#     factures = (
#         db.query(Facture)
#         .filter(Facture.statut == "validee")
#         .filter(func.extract("year", Facture.date_facture) == decl.annee)
#         .filter(func.extract("month", Facture.date_facture) == decl.mois)
#         .order_by(Facture.date_facture.asc(), Facture.id.asc())
#         .all()
#     )

#     lignes: List[DeclarationLigne] = []
#     for f in factures:
#         if not f.id:
#             continue  # sécurité
#         if not f.date_facture:
#             continue

#         ligne = DeclarationLigne(
#             declaration_id=decl.id,
#             facture_id=f.id,  # ✅ jamais NULL
#             fact_num=f.numero_facture,
#             designation=f.designation or "Achat fournisseur",
#             m_ht=float(f.montant_ht or 0),
#             tva=float(f.montant_tva or 0),
#             m_ttc=float(f.montant_ttc or 0),
#             if_frs=f.if_frs,
#             lib_frss=f.fournisseur,
#             ice_frs=f.ice_frs,
#             taux=float(f.taux_tva or 0),
#             date_pai=f.date_paie or f.date_facture,
#             date_fac=f.date_facture,
#         )
#         db.add(ligne)
#         lignes.append(ligne)

#     db.commit()
#     return lignes


# # -------------------------
# # Export Excel
# # -------------------------
# def build_declaration_excel(db: Session, annee: int, mois: int) -> str:
#     decl = _get_or_create_declaration(db, annee, mois)

#     lignes = (
#         db.query(DeclarationLigne)
#         .filter(DeclarationLigne.declaration_id == decl.id)
#         .order_by(DeclarationLigne.id.asc())
#         .all()
#     )

#     wb = Workbook()
#     ws = wb.active
#     ws.title = f"DGI-{annee}-{mois:02d}"

#     header_fill = PatternFill("solid", fgColor="4F81BD")
#     header_font = Font(color="FFFFFF", bold=True)
#     thin = Side(style="thin", color="999999")
#     border = Border(left=thin, right=thin, top=thin, bottom=thin)

#     # Header
#     ws.append(HEADERS)
#     for col in range(1, len(HEADERS) + 1):
#         c = ws.cell(row=1, column=col)
#         c.fill = header_fill
#         c.font = header_font
#         c.alignment = Alignment(horizontal="center", vertical="center")
#         c.border = border

#     # Lines
#     for l in lignes:
#         ws.append([
#             l.fact_num,
#             l.designation,
#             float(l.m_ht or 0),
#             float(l.tva or 0),
#             float(l.m_ttc or 0),
#             l.if_frs,
#             l.lib_frss,
#             l.ice_frs,
#             float(l.taux or 0),
#             str(l.date_pai) if l.date_pai else None,
#             str(l.date_fac) if l.date_fac else None,
#         ])

#     # Total row
#     total_ht, total_tva, total_ttc = _recompute_totals(db, decl.id)
#     ws.append([
#         "TOTAL", "", total_ht, total_tva, total_ttc,
#         "", "", "", "", "", ""
#     ])

#     last_row = ws.max_row
#     for col in range(1, len(HEADERS) + 1):
#         c = ws.cell(row=last_row, column=col)
#         c.font = Font(bold=True)
#         c.border = border

#     # Auto width (simple)
#     for col in ws.columns:
#         max_len = 0
#         col_letter = col[0].column_letter
#         for cell in col:
#             v = "" if cell.value is None else str(cell.value)
#             max_len = max(max_len, len(v))
#         ws.column_dimensions[col_letter].width = min(max_len + 2, 40)

#     out_path = EXPORT_DIR / f"declaration_{annee}_{mois:02d}.xlsx"
#     wb.save(out_path)

#     # Stocker le chemin dans la déclaration
#     decl.ded_xlsx_path = str(out_path)
#     db.commit()
#     db.refresh(decl)

#     return str(out_path)


# # -------------------------
# # Export PDF
# # -------------------------
# def build_declaration_pdf(db: Session, annee: int, mois: int) -> str:
#     decl = _get_or_create_declaration(db, annee, mois)

#     lignes = (
#         db.query(DeclarationLigne)
#         .filter(DeclarationLigne.declaration_id == decl.id)
#         .order_by(DeclarationLigne.id.asc())
#         .all()
#     )

#     total_ht, total_tva, total_ttc = _recompute_totals(db, decl.id)

#     out_path = EXPORT_DIR / f"declaration_{annee}_{mois:02d}.pdf"

#     c = canvas.Canvas(str(out_path), pagesize=landscape(A4))
#     W, H = landscape(A4)

#     c.setFont("Helvetica-Bold", 16)
#     c.drawString(20 * mm, (H - 15 * mm), f"Déclaration Mensuelle DGI - {annee}-{mois:02d}")

#     # Table layout
#     c.setFont("Helvetica-Bold", 9)
#     x0 = 10 * mm
#     y = H - 25 * mm
#     row_h = 8 * mm

#     col_w = [22, 35, 18, 18, 18, 18, 50, 35, 15, 25, 25]  # approx widths
#     col_w = [w * mm for w in col_w]

#     # Header
#     x = x0
#     for i, h in enumerate(HEADERS):
#         c.rect(x, y, col_w[i], row_h, stroke=1, fill=0)
#         c.drawString(x + 2, y + 2, h)
#         x += col_w[i]

#     c.setFont("Helvetica", 9)
#     y -= row_h

#     for l in lignes:
#         x = x0
#         values = [
#             l.fact_num or "",
#             l.designation or "",
#             f"{float(l.m_ht or 0):.2f}",
#             f"{float(l.tva or 0):.2f}",
#             f"{float(l.m_ttc or 0):.2f}",
#             l.if_frs or "",
#             l.lib_frss or "",
#             l.ice_frs or "",
#             f"{float(l.taux or 0):.2f}",
#             str(l.date_pai) if l.date_pai else "",
#             str(l.date_fac) if l.date_fac else "",
#         ]
#         for i, v in enumerate(values):
#             c.rect(x, y, col_w[i], row_h, stroke=1, fill=0)
#             c.drawString(x + 2, y + 2, str(v)[:45])
#             x += col_w[i]

#         y -= row_h
#         if y < 15 * mm:
#             c.showPage()
#             y = H - 20 * mm

#     # Total
#     x = x0
#     c.setFont("Helvetica-Bold", 10)
#     total_vals = ["TOTAL", "", f"{total_ht:.2f}", f"{total_tva:.2f}", f"{total_ttc:.2f}", "", "", "", "", "", ""]
#     for i, v in enumerate(total_vals):
#         c.rect(x, y, col_w[i], row_h, stroke=1, fill=0)
#         c.drawString(x + 2, y + 2, str(v))
#         x += col_w[i]

#     c.save()

#     decl.ded_pdf_path = str(out_path)
#     db.commit()
#     db.refresh(decl)

#     return str(out_path)


# # -------------------------
# # Endpoints
# # -------------------------
# @router.post("/{annee}/{mois}/generer")
# def generer_declaration(annee: int, mois: int, db: Session = Depends(get_db)):
#     if mois < 1 or mois > 12:
#         raise HTTPException(status_code=400, detail="mois doit être entre 1 et 12")
#     decl = _get_or_create_declaration(db, annee, mois)

#     _build_lines_from_factures(db, decl)
#     total_ht, total_tva, total_ttc = _recompute_totals(db, decl.id)
#     db.refresh(decl)

#     return {
#         "id": decl.id,
#         "annee": decl.annee,
#         "mois": decl.mois,
#         "total_ht": total_ht,
#         "total_tva": total_tva,
#         "total_ttc": total_ttc,
#         "lignes": [
#             {
#                 "fact_num": l.fact_num,
#                 "designation": l.designation,
#                 "m_ht": float(l.m_ht or 0),
#                 "tva": float(l.tva or 0),
#                 "m_ttc": float(l.m_ttc or 0),
#                 "if_frs": l.if_frs,
#                 "lib_frss": l.lib_frss,
#                 "ice_frs": l.ice_frs,
#                 "taux": float(l.taux or 0),
#                 "date_pai": str(l.date_pai) if l.date_pai else None,
#                 "date_fac": str(l.date_fac) if l.date_fac else None,
#             }
#             for l in db.query(DeclarationLigne).filter(DeclarationLigne.declaration_id == decl.id).all()
#         ],
#     }


# @router.get("/{annee}/{mois}")
# def get_declaration(annee: int, mois: int, db: Session = Depends(get_db)):
#     decl = (
#         db.query(DeclarationMensuelle)
#         .filter(DeclarationMensuelle.annee == annee, DeclarationMensuelle.mois == mois)
#         .first()
#     )
#     if not decl:
#         raise HTTPException(status_code=404, detail="Déclaration introuvable")

#     lignes = (
#         db.query(DeclarationLigne)
#         .filter(DeclarationLigne.declaration_id == decl.id)
#         .order_by(DeclarationLigne.id.asc())
#         .all()
#     )

#     return {
#         "id": decl.id,
#         "annee": decl.annee,
#         "mois": decl.mois,
#         "total_ht": float(decl.total_ht or 0),
#         "total_tva": float(decl.total_tva or 0),
#         "total_ttc": float(decl.total_ttc or 0),
#         "ded_pdf_path": decl.ded_pdf_path,
#         "ded_xlsx_path": decl.ded_xlsx_path,
#         "lignes": [
#             {
#                 "fact_num": l.fact_num,
#                 "designation": l.designation,
#                 "m_ht": float(l.m_ht or 0),
#                 "tva": float(l.tva or 0),
#                 "m_ttc": float(l.m_ttc or 0),
#                 "if_frs": l.if_frs,
#                 "lib_frss": l.lib_frss,
#                 "ice_frs": l.ice_frs,
#                 "taux": float(l.taux or 0),
#                 "date_pai": str(l.date_pai) if l.date_pai else None,
#                 "date_fac": str(l.date_fac) if l.date_fac else None,
#             }
#             for l in lignes
#         ],
#     }


# @router.get("/{annee}/{mois}/excel")
# def export_declaration_excel(annee: int, mois: int, db: Session = Depends(get_db)):
#     # Si la déclaration n'existe pas encore, on la génère
#     decl = _get_or_create_declaration(db, annee, mois)
#     if db.query(DeclarationLigne).filter(DeclarationLigne.declaration_id == decl.id).count() == 0:
#         _build_lines_from_factures(db, decl)
#         _recompute_totals(db, decl.id)

#     path = build_declaration_excel(db, annee, mois)
#     return FileResponse(
#         path,
#         media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         filename=f"declaration_{annee}_{mois:02d}.xlsx",
#     )


# @router.get("/{annee}/{mois}/pdf")
# def export_declaration_pdf(annee: int, mois: int, db: Session = Depends(get_db)):
#     decl = _get_or_create_declaration(db, annee, mois)
#     if db.query(DeclarationLigne).filter(DeclarationLigne.declaration_id == decl.id).count() == 0:
#         _build_lines_from_factures(db, decl)
#         _recompute_totals(db, decl.id)

#     path = build_declaration_pdf(db, annee, mois)
#     return FileResponse(
#         path,
#         media_type="application/pdf",
#         filename=f"declaration_{annee}_{mois:02d}.pdf",
#     )





















# # routes/declarations.py
# from pathlib import Path
# from fastapi import APIRouter, Depends, HTTPException
# from fastapi.responses import FileResponse
# from sqlalchemy.orm import Session

# from database import get_db
# from models import DeclarationMensuelle, DeclarationLigne
# from services.exports import export_declaration_pdf, export_declaration_excel

# router = APIRouter(prefix="/declarations", tags=["declarations"])

# EXPORT_DIR = Path("exports")
# EXPORT_DIR.mkdir(parents=True, exist_ok=True)


# @router.get("/{annee}/{mois}/pdf")
# def declaration_pdf(annee: int, mois: int, db: Session = Depends(get_db)):
#     decl = db.query(DeclarationMensuelle).filter_by(annee=annee, mois=mois).first()
#     if not decl:
#         raise HTTPException(status_code=404, detail="Déclaration introuvable")

#     lignes = db.query(DeclarationLigne).filter_by(declaration_id=decl.id).order_by(DeclarationLigne.id.asc()).all()

#     pdf_path = EXPORT_DIR / f"declaration_{annee}_{mois:02d}.pdf"
#     export_declaration_pdf(decl, lignes, str(pdf_path))

#     return FileResponse(
#         path=str(pdf_path),
#         filename=pdf_path.name,
#         media_type="application/pdf"
#     )


# @router.get("/{annee}/{mois}/excel")
# def declaration_excel(annee: int, mois: int, db: Session = Depends(get_db)):
#     decl = db.query(DeclarationMensuelle).filter_by(annee=annee, mois=mois).first()
#     if not decl:
#         raise HTTPException(status_code=404, detail="Déclaration introuvable")

#     lignes = db.query(DeclarationLigne).filter_by(declaration_id=decl.id).order_by(DeclarationLigne.id.asc()).all()

#     xlsx_path = EXPORT_DIR / f"declaration_{annee}_{mois:02d}.xlsx"
#     export_declaration_excel(decl, lignes, str(xlsx_path))

#     return FileResponse(
#         path=str(xlsx_path),
#         filename=xlsx_path.name,
#         media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#     )


















# # routes/declarations.py
# from pathlib import Path
# from fastapi import APIRouter, Depends, HTTPException
# from fastapi.responses import FileResponse
# from sqlalchemy.orm import Session

# from database import get_db
# from models import DeclarationMensuelle, DeclarationLigne
# from services.exports import export_declaration_pdf, export_declaration_excel

# router = APIRouter(prefix="/declarations", tags=["declarations"])
# EXPORT_DIR = Path("exports")
# EXPORT_DIR.mkdir(parents=True, exist_ok=True)


# def get_decl_or_404(db: Session, annee: int, mois: int) -> DeclarationMensuelle:
#     decl = (
#         db.query(DeclarationMensuelle)
#         .filter(DeclarationMensuelle.annee == annee, DeclarationMensuelle.mois == mois)
#         .first()
#     )
#     if not decl:
#         raise HTTPException(status_code=404, detail="Déclaration introuvable")
#     return decl


# @router.get("/{annee}/{mois}")
# def get_declaration(annee: int, mois: int, db: Session = Depends(get_db)):
#     decl = get_decl_or_404(db, annee, mois)
#     lignes = (
#         db.query(DeclarationLigne)
#         .filter(DeclarationLigne.declaration_id == decl.id)
#         .order_by(DeclarationLigne.id.asc())
#         .all()
#     )
#     return {
#         "id": decl.id,
#         "annee": decl.annee,
#         "mois": decl.mois,
#         "total_ht": decl.total_ht,
#         "total_tva": decl.total_tva,
#         "total_ttc": decl.total_ttc,
#         "lignes": [
#             dict(
#                 id=l.id,
#                 facture_id=l.facture_id,
#                 fact_num=l.fact_num,
#                 designation=l.designation,
#                 m_ht=l.m_ht,
#                 tva=l.tva,
#                 m_ttc=l.m_ttc,
#                 if_frs=l.if_frs,
#                 lib_frss=l.lib_frss,
#                 ice_frs=l.ice_frs,
#                 taux=l.taux,
#                 date_pai=str(l.date_pai) if l.date_pai else None,
#                 date_fac=str(l.date_fac) if l.date_fac else None,
#             )
#             for l in lignes
#         ],
#     }


# @router.get("/{annee}/{mois}/pdf")
# def export_pdf(annee: int, mois: int, db: Session = Depends(get_db)):
#     decl = get_decl_or_404(db, annee, mois)
#     lignes = (
#         db.query(DeclarationLigne)
#         .filter(DeclarationLigne.declaration_id == decl.id)
#         .order_by(DeclarationLigne.id.asc())
#         .all()
#     )

#     pdf_path = decl.ded_pdf_path or str(EXPORT_DIR / f"declaration_{annee}_{mois:02d}.pdf")
#     export_declaration_pdf(decl, lignes, pdf_path)

#     # si tu as le champ en DB
#     decl.ded_pdf_path = pdf_path
#     db.commit()

#     return FileResponse(
#         path=pdf_path,
#         media_type="application/pdf",
#         filename=f"declaration_{annee}_{mois:02d}.pdf",
#     )


# @router.get("/{annee}/{mois}/excel")
# def export_excel(annee: int, mois: int, db: Session = Depends(get_db)):
#     decl = get_decl_or_404(db, annee, mois)
#     lignes = (
#         db.query(DeclarationLigne)
#         .filter(DeclarationLigne.declaration_id == decl.id)
#         .order_by(DeclarationLigne.id.asc())
#         .all()
#     )

#     xlsx_path = decl.ded_xlsx_path or str(EXPORT_DIR / f"declaration_{annee}_{mois:02d}.xlsx")
#     export_declaration_excel(decl, lignes, xlsx_path)

#     decl.ded_xlsx_path = xlsx_path
#     db.commit()

#     return FileResponse(
#         path=xlsx_path,
#         media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         filename=f"declaration_{annee}_{mois:02d}.xlsx",
#     )
























# # routes/declarations.py
# from datetime import datetime
# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session

# from database import get_db
# from models import Facture, DeclarationMensuelle, DeclarationLigne
# from schemas import DeclarationOut

# router = APIRouter(prefix="/declarations", tags=["declarations"])


# def _month_range(annee: int, mois: int):
#     # retourne (YYYY-MM-01) à (YYYY-MM-31)
#     from datetime import date
#     if mois == 12:
#         start = date(annee, mois, 1)
#         end = date(annee + 1, 1, 1)
#     else:
#         start = date(annee, mois, 1)
#         end = date(annee, mois + 1, 1)
#     return start, end


# @router.post("/{annee}/{mois}/generer", response_model=DeclarationOut)
# def generer_declaration(annee: int, mois: int, db: Session = Depends(get_db)):
#     start, end = _month_range(annee, mois)

#     decl = db.query(DeclarationMensuelle).filter(
#         DeclarationMensuelle.annee == annee,
#         DeclarationMensuelle.mois == mois
#     ).first()

#     if not decl:
#         decl = DeclarationMensuelle(annee=annee, mois=mois)
#         db.add(decl)
#         db.commit()
#         db.refresh(decl)

#     factures = db.query(Facture).filter(
#         Facture.statut == "validee",
#         Facture.date_facture >= start,
#         Facture.date_facture < end
#     ).all()

#     total_ht = 0.0
#     total_tva = 0.0
#     total_ttc = 0.0

#     for f in factures:
#         # upsert ligne (déjà unique decl+facture)
#         ligne = db.query(DeclarationLigne).filter(
#             DeclarationLigne.declaration_id == decl.id,
#             DeclarationLigne.facture_id == f.id
#         ).first()

#         if not ligne:
#             ligne = DeclarationLigne(declaration_id=decl.id, facture_id=f.id)
#             db.add(ligne)

#         ligne.fact_num = f.numero_facture
#         ligne.designation = f.designation
#         ligne.m_ht = f.montant_ht
#         ligne.tva = f.montant_tva
#         ligne.m_ttc = f.montant_ttc
#         ligne.if_frs = f.if_frs
#         ligne.lib_frss = f.fournisseur
#         ligne.ice_frs = f.ice_frs
#         ligne.taux = f.taux_tva
#         ligne.date_pai = f.date_paie
#         ligne.date_fac = f.date_facture

#         total_ht += float(f.montant_ht or 0)
#         total_tva += float(f.montant_tva or 0)
#         total_ttc += float(f.montant_ttc or 0)

#     decl.total_ht = round(total_ht, 2)
#     decl.total_tva = round(total_tva, 2)
#     decl.total_ttc = round(total_ttc, 2)
#     decl.updated_at = datetime.utcnow()

#     db.commit()
#     db.refresh(decl)
#     return decl


# @router.get("/{annee}/{mois}", response_model=DeclarationOut)
# def get_declaration(annee: int, mois: int, db: Session = Depends(get_db)):
#     decl = db.query(DeclarationMensuelle).filter(
#         DeclarationMensuelle.annee == annee,
#         DeclarationMensuelle.mois == mois
#     ).first()

#     if not decl:
#         # retourne une déclaration vide
#         decl = DeclarationMensuelle(annee=annee, mois=mois, total_ht=0, total_tva=0, total_ttc=0)
#     return decl






















# routes/declarations.py
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Facture, DeclarationMensuelle, DeclarationLigne
from schemas import DeclarationOut

router = APIRouter(prefix="/declarations", tags=["declarations"])


def _month_range(annee: int, mois: int):
    if mois < 1 or mois > 12:
        raise HTTPException(status_code=400, detail="mois doit être entre 1 et 12")

    if mois == 12:
        start = date(annee, 12, 1)
        end = date(annee + 1, 1, 1)
    else:
        start = date(annee, mois, 1)
        end = date(annee, mois + 1, 1)
    return start, end


@router.post("/{annee}/{mois}/generer", response_model=DeclarationOut)
def generer_declaration(annee: int, mois: int, db: Session = Depends(get_db)):
    start, end = _month_range(annee, mois)

    decl = db.query(DeclarationMensuelle).filter(
        DeclarationMensuelle.annee == annee,
        DeclarationMensuelle.mois == mois
    ).first()

    if not decl:
        decl = DeclarationMensuelle(annee=annee, mois=mois)
        db.add(decl)
        db.commit()
        db.refresh(decl)

    factures = db.query(Facture).filter(
        Facture.statut == "validee",
        Facture.date_facture >= start,
        Facture.date_facture < end
    ).all()

    total_ht = 0.0
    total_tva = 0.0
    total_ttc = 0.0

    for f in factures:
        ligne = db.query(DeclarationLigne).filter(
            DeclarationLigne.declaration_id == decl.id,
            DeclarationLigne.facture_id == f.id
        ).first()

        if not ligne:
            ligne = DeclarationLigne(declaration_id=decl.id, facture_id=f.id)
            db.add(ligne)

        ligne.fact_num = f.numero_facture
        ligne.designation = f.designation
        ligne.m_ht = f.montant_ht
        ligne.tva = f.montant_tva
        ligne.m_ttc = f.montant_ttc
        ligne.if_frs = f.if_frs
        ligne.lib_frss = f.fournisseur
        ligne.ice_frs = f.ice_frs
        ligne.taux = f.taux_tva
        ligne.date_pai = f.date_paie
        ligne.date_fac = f.date_facture

        total_ht += float(f.montant_ht or 0)
        total_tva += float(f.montant_tva or 0)
        total_ttc += float(f.montant_ttc or 0)

    decl.total_ht = round(total_ht, 2)
    decl.total_tva = round(total_tva, 2)
    decl.total_ttc = round(total_ttc, 2)
    decl.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(decl)
    return decl


@router.get("/{annee}/{mois}", response_model=DeclarationOut)
def get_declaration(annee: int, mois: int, db: Session = Depends(get_db)):
    decl = db.query(DeclarationMensuelle).filter(
        DeclarationMensuelle.annee == annee,
        DeclarationMensuelle.mois == mois
    ).first()

    if not decl:
        raise HTTPException(status_code=404, detail="Déclaration introuvable. Lance /generer d'abord.")

    return decl
