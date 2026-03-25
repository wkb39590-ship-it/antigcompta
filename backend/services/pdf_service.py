"""
pdf_service.py — Génération du bulletin de paie en PDF professionnel
Utilise ReportLab pour produire un bulletin conforme aux normes marocaines.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from decimal import Decimal
from typing import Optional
import math

# ──────────────────────────────────────────────────────────────────────────
# COULEURS DU BULLETIN
# ──────────────────────────────────────────────────────────────────────────
BLEU_PRINCIPAL = colors.HexColor("#1e3a5f")   # Bleu marine foncé
BLEU_CLAIR     = colors.HexColor("#e8f0fe")   # Fond bleu clair
GRIS_CLAIR     = colors.HexColor("#f5f5f5")   # Fond gris alterné
VERT_NET       = colors.HexColor("#0d6e3f")   # Vert net à payer
ROUGE_RETENUE  = colors.HexColor("#b91c1c")   # Rouge retenues
GRIS_TEXTE     = colors.HexColor("#374151")   # Texte principal
GRIS_BORDER    = colors.HexColor("#d1d5db")   # Bordures


def fmt(value) -> str:
    """Formate un nombre en MAD avec 2 décimales."""
    try:
        v = float(value or 0)
        return f"{v:,.2f}".replace(",", " ").replace(".", ",")
    except:
        return "0,00"


def mois_label(mois: int, annee: int) -> str:
    MOIS = ["", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
            "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    return f"{MOIS[mois]} {annee}"


def last_day(mois: int, annee: int) -> int:
    import calendar
    return calendar.monthrange(annee, mois)[1]


def generer_bulletin_pdf(bulletin, employe, societe) -> bytes:
    """
    Génère le PDF du bulletin de paie.
    
    Args:
        bulletin: Objet BulletinPaie avec tous les champs calculés
        employe:  Objet Employe avec les informations personnelles
        societe:  Objet Societe avec les informations de l'entreprise
    
    Returns:
        bytes: Contenu binaire du PDF
    """
    buffer = BytesIO()
    
    # Marges
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15*mm,
        leftMargin=15*mm,
        topMargin=15*mm,
        bottomMargin=15*mm,
        title=f"Bulletin de Paie - {employe.prenom or ''} {employe.nom} - {mois_label(bulletin.mois, bulletin.annee)}"
    )

    styles = getSampleStyleSheet()
    story = []

    # ── STYLES ────────────────────────────────────────────────────────────
    titre_style = ParagraphStyle(
        'Titre', parent=styles['Normal'],
        fontSize=9, textColor=GRIS_TEXTE, leading=12
    )
    bold_style = ParagraphStyle(
        'Bold', parent=styles['Normal'],
        fontSize=9, textColor=GRIS_TEXTE, leading=12,
        fontName='Helvetica-Bold'
    )
    header_title_style = ParagraphStyle(
        'HeaderTitle', parent=styles['Normal'],
        fontSize=22, textColor=BLEU_PRINCIPAL, leading=26,
        fontName='Helvetica-Bold'
    )
    subtitle_style = ParagraphStyle(
        'Subtitle', parent=styles['Normal'],
        fontSize=10, textColor=colors.white, leading=14,
        fontName='Helvetica-Bold', alignment=TA_CENTER
    )
    net_style = ParagraphStyle(
        'Net', parent=styles['Normal'],
        fontSize=16, textColor=VERT_NET, leading=20,
        fontName='Helvetica-Bold', alignment=TA_RIGHT
    )

    # ══════════════════════════════════════════════════════════════════════
    # 1. EN-TÊTE : Société | BULLETIN DE PAIE
    # ══════════════════════════════════════════════════════════════════════
    nom_societe   = getattr(societe, 'raison_sociale', 'VOTRE SOCIÉTÉ') or 'VOTRE SOCIÉTÉ'
    adresse_soc   = getattr(societe, 'adresse', '') or ''
    ice_soc       = getattr(societe, 'ice', '') or ''
    rc_soc        = getattr(societe, 'rc', '') or ''
    cnss_soc      = getattr(societe, 'cnss', None)
    cnss_soc_str  = cnss_soc if (cnss_soc and str(cnss_soc).strip()) else 'Non renseigné'

    nom_emp       = f"{getattr(employe, 'prenom', '') or ''} {getattr(employe, 'nom', '') or ''}".strip()
    cin_emp       = getattr(employe, 'cin', 'Non renseigné') or 'Non renseigné'
    cnss_emp      = getattr(employe, 'numero_cnss', 'Non renseigné') or 'Non renseigné'
    poste_emp     = getattr(employe, 'poste', 'Employé') or 'Employé'
    date_emb      = getattr(employe, 'date_embauche', None)
    date_emb_str  = date_emb.strftime('%d/%m/%Y') if date_emb else 'Non renseignée'

    periode_str   = f"{1:02d}/{bulletin.mois:02d}/{bulletin.annee} au {last_day(bulletin.mois, bulletin.annee):02d}/{bulletin.mois:02d}/{bulletin.annee}"

    # Ligne gauche (Société)
    soc_lines = [
        [Paragraph(f"<b>{nom_societe}</b>", ParagraphStyle('socnom', parent=styles['Normal'], fontSize=13, textColor=BLEU_PRINCIPAL, fontName='Helvetica-Bold', leading=16))],
        [Paragraph(adresse_soc, titre_style)],
        [Paragraph(f"RC : {rc_soc}  |  ICE : {ice_soc}", titre_style)],
        [Paragraph(f"N° CNSS : {cnss_soc_str}", titre_style)],
    ]

    # Ligne droite (Titre + Période)
    header_right = [
        [Paragraph("BULLETIN DE PAIE", header_title_style)],
        [Paragraph(f"Période : {periode_str}", ParagraphStyle('per', parent=styles['Normal'], fontSize=10, textColor=GRIS_TEXTE, leading=14, alignment=TA_RIGHT))],
        [Paragraph(f"Mois de {mois_label(bulletin.mois, bulletin.annee)}", ParagraphStyle('mois', parent=styles['Normal'], fontSize=10, textColor=BLEU_PRINCIPAL, fontName='Helvetica-Bold', leading=14, alignment=TA_RIGHT))],
    ]

    header_table = Table(
        [[Table(soc_lines, colWidths=[85*mm]), Table(header_right, colWidths=[85*mm])]],
        colWidths=[90*mm, 90*mm]
    )
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=2, color=BLEU_PRINCIPAL, spaceAfter=8))

    # ══════════════════════════════════════════════════════════════════════
    # 2. INFORMATIONS DU SALARIÉ  
    # ══════════════════════════════════════════════════════════════════════
    emp_data = [
        [
            Paragraph("<b>Nom complet</b>", bold_style), Paragraph(nom_emp, titre_style),
            Paragraph("<b>N° CIN</b>", bold_style),       Paragraph(cin_emp, titre_style),
        ],
        [
            Paragraph("<b>Poste</b>", bold_style),        Paragraph(poste_emp, titre_style),
            Paragraph("<b>N° CNSS</b>", bold_style),      Paragraph(cnss_emp, titre_style),
        ],
        [
            Paragraph("<b>Date d'embauche</b>", bold_style), Paragraph(date_emb_str, titre_style),
            Paragraph("<b>Matricule</b>", bold_style),     Paragraph(f"#{employe.id}", titre_style),
        ],
    ]

    emp_table = Table(emp_data, colWidths=[35*mm, 55*mm, 35*mm, 55*mm])
    emp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BLEU_CLAIR),
        ('GRID', (0, 0), (-1, -1), 0.5, GRIS_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(emp_table)
    story.append(Spacer(1, 6*mm))

    # ══════════════════════════════════════════════════════════════════════
    # 3. TABLEAU DES RUBRIQUES
    # ══════════════════════════════════════════════════════════════════════
    header_row = [
        Paragraph("<b>N°</b>", ParagraphStyle('th', parent=styles['Normal'], fontSize=8, textColor=colors.white, fontName='Helvetica-Bold', leading=10, alignment=TA_CENTER)),
        Paragraph("<b>Désignation de la rubrique</b>", ParagraphStyle('th', parent=styles['Normal'], fontSize=8, textColor=colors.white, fontName='Helvetica-Bold', leading=10)),
        Paragraph("<b>Base</b>", ParagraphStyle('th', parent=styles['Normal'], fontSize=8, textColor=colors.white, fontName='Helvetica-Bold', leading=10, alignment=TA_RIGHT)),
        Paragraph("<b>Taux</b>", ParagraphStyle('th', parent=styles['Normal'], fontSize=8, textColor=colors.white, fontName='Helvetica-Bold', leading=10, alignment=TA_RIGHT)),
        Paragraph("<b>À Payer</b>", ParagraphStyle('th', parent=styles['Normal'], fontSize=8, textColor=colors.white, fontName='Helvetica-Bold', leading=10, alignment=TA_RIGHT)),
        Paragraph("<b>À Retenir</b>", ParagraphStyle('th', parent=styles['Normal'], fontSize=8, textColor=colors.white, fontName='Helvetica-Bold', leading=10, alignment=TA_RIGHT)),
    ]

    rubrique_data = [header_row]

    def rubrique_row(num, designation, base="", taux="", a_payer="", a_retenir="", bg=None):
        row_style = ParagraphStyle('td', parent=styles['Normal'], fontSize=8, textColor=GRIS_TEXTE, leading=11)
        row_style_r = ParagraphStyle('tdr', parent=styles['Normal'], fontSize=8, textColor=GRIS_TEXTE, leading=11, alignment=TA_RIGHT)
        return [
            Paragraph(str(num), ParagraphStyle('tdc', parent=styles['Normal'], fontSize=8, textColor=GRIS_TEXTE, leading=11, alignment=TA_CENTER)),
            Paragraph(designation, row_style),
            Paragraph(base, row_style_r),
            Paragraph(taux, row_style_r),
            Paragraph(a_payer, row_style_r),
            Paragraph(a_retenir, row_style_r),
        ]

    sbr = float(bulletin.salaire_base)
    sbrt = float(bulletin.salaire_brut)

    # GAINS
    gains_list = getattr(bulletin, 'rubriques_gains', [])
    if gains_list:
        # Affichage détaillé depuis les lignes du journal
        for i, gain in enumerate(gains_list):
            rubrique_data.append(rubrique_row(str(100 + i*5), gain["nom"], fmt(gain["montant"]), "", fmt(gain["montant"]), ""))
    else:
        # Mode classique (auto-généré)
        rubrique_data.append(rubrique_row("100", "Salaire de Base", fmt(sbr), "", fmt(sbr), ""))
        if float(bulletin.prime_anciennete) > 0:
            rubrique_data.append(rubrique_row("110", "Prime d'ancienneté", fmt(sbr), "", fmt(bulletin.prime_anciennete), ""))
        if float(bulletin.autres_gains) > 0:
            rubrique_data.append(rubrique_row("200", "Primes et Heures Supplémentaires", "", "", fmt(bulletin.autres_gains), ""))

    # RETENUES
    if float(bulletin.cnss_salarie) > 0:
        base_cnss = min(sbrt, 6000.0)
        rubrique_data.append(rubrique_row("700", "CNSS Salarié", fmt(base_cnss), "4,48%", "", fmt(bulletin.cnss_salarie)))
    if float(bulletin.amo_salarie) > 0:
        rubrique_data.append(rubrique_row("710", "AMO Salarié", fmt(sbrt), "2,26%", "", fmt(bulletin.amo_salarie)))
    if float(bulletin.ir_retenu) > 0:
        rubrique_data.append(rubrique_row("750", "I.G.R. / I.R. (Impôt sur le Revenu)", "", "", "", fmt(bulletin.ir_retenu)))

    # TOTAL
    rubrique_data.append([
        Paragraph("", titre_style),
        Paragraph("<b>TOTAUX</b>", ParagraphStyle('tot', parent=styles['Normal'], fontSize=9, textColor=BLEU_PRINCIPAL, fontName='Helvetica-Bold', leading=12)),
        Paragraph("", titre_style),
        Paragraph("", titre_style),
        Paragraph(f"<b>{fmt(bulletin.salaire_brut)}</b>", ParagraphStyle('totv', parent=styles['Normal'], fontSize=9, textColor=BLEU_PRINCIPAL, fontName='Helvetica-Bold', leading=12, alignment=TA_RIGHT)),
        Paragraph(f"<b>{fmt(bulletin.total_retenues)}</b>", ParagraphStyle('totr', parent=styles['Normal'], fontSize=9, textColor=ROUGE_RETENUE, fontName='Helvetica-Bold', leading=12, alignment=TA_RIGHT)),
    ])

    nb_rows = len(rubrique_data)
    rub_table = Table(rubrique_data, colWidths=[12*mm, 65*mm, 27*mm, 18*mm, 27*mm, 27*mm])

    rub_style = TableStyle([
        # En-tête
        ('BACKGROUND', (0, 0), (-1, 0), BLEU_PRINCIPAL),
        ('GRID', (0, 0), (-1, -1), 0.5, GRIS_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        # Alternance gris pour les lignes de données (hors header et total)
        *[('BACKGROUND', (0, i), (-1, i), GRIS_CLAIR) for i in range(2, nb_rows - 1, 2)],
        # Ligne de total
        ('BACKGROUND', (0, nb_rows - 1), (-1, nb_rows - 1), BLEU_CLAIR),
        ('LINEABOVE', (0, nb_rows - 1), (-1, nb_rows - 1), 1.5, BLEU_PRINCIPAL),
    ])
    rub_table.setStyle(rub_style)
    story.append(rub_table)
    story.append(Spacer(1, 6*mm))

    # ══════════════════════════════════════════════════════════════════════
    # 4. BANDE NET À PAYER + CHARGES PATRONALES
    # ══════════════════════════════════════════════════════════════════════
    net_data = [
        [
            Paragraph("NET À PAYER", ParagraphStyle('netlabel', parent=styles['Normal'], fontSize=11, textColor=colors.white, fontName='Helvetica-Bold', leading=14, alignment=TA_LEFT)),
            Paragraph(f"{fmt(bulletin.salaire_net)} MAD", ParagraphStyle('netval', parent=styles['Normal'], fontSize=18, textColor=colors.white, fontName='Helvetica-Bold', leading=22, alignment=TA_RIGHT)),
        ]
    ]
    net_table = Table(net_data, colWidths=[90*mm, 90*mm])
    net_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), VERT_NET),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(net_table)
    story.append(Spacer(1, 12*mm))

    doc.build(story)
    return buffer.getvalue()
