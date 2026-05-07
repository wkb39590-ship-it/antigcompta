from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from io import BytesIO
import calendar

def last_day(mois: int, annee: int) -> int:
    return calendar.monthrange(annee, mois)[1]

# ──────────────────────────────────────────────────────────────────────────
# COULEURS ET STYLES PROFESSIONNELS
# ──────────────────────────────────────────────────────────────────────────
VERT_ENTETE    = colors.HexColor("#e2e8f0")   # Gris bleu très clair pour les entêtes
GRIS_BORDURE   = colors.HexColor("#94a3b8")   # Bordures fines
NOIR_TEXTE     = colors.HexColor("#000000")   # Noir pur pour impression
GRIS_TEXTE_SEC = colors.HexColor("#475569")   # Gris pour labels secondaires

def fmt(value, decimals=2) -> str:
    try:
        v = float(value or 0)
        if decimals == 3: return f"{v:,.3f}".replace(",", " ").replace(".", ",")
        return f"{v:,.2f}".replace(",", " ").replace(".", ",")
    except:
        return "0,00"

def generer_bulletin_pdf(bulletin, employe, societe) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=10*mm, leftMargin=10*mm, topMargin=10*mm, bottomMargin=10*mm,
        title=f"Bulletin - {employe.nom}"
    )

    styles = getSampleStyleSheet()
    story = []

    # ── STYLES PERSO ──────────────────────────────────────────────────────
    s_label = ParagraphStyle('Label', fontSize=8, fontName='Helvetica-Bold', textColor=NOIR_TEXTE, leading=10)
    s_value = ParagraphStyle('Value', fontSize=8, fontName='Helvetica', textColor=NOIR_TEXTE, leading=10, alignment=TA_CENTER)
    s_title = ParagraphStyle('MainTitle', fontSize=16, fontName='Helvetica-Bold', alignment=TA_CENTER, leading=20)
    s_th    = ParagraphStyle('TH', fontSize=8, fontName='Helvetica-Bold', alignment=TA_CENTER, leading=10)
    s_td    = ParagraphStyle('TD', fontSize=8, fontName='Helvetica', leading=10)
    s_tdr   = ParagraphStyle('TDR', fontSize=8, fontName='Helvetica', alignment=TA_RIGHT, leading=10)
    s_tdc   = ParagraphStyle('TDC', fontSize=8, fontName='Helvetica', alignment=TA_CENTER, leading=10)

    # 1. EN-TETE SOCIÉTÉ & TITRE
    data_top = [
        [
            Paragraph(f"<b>{societe.raison_sociale.upper()}</b><br/><font size='8'>{societe.adresse or ''}</font>", s_td),
            Paragraph("<b>BULLETIN DE PAIE</b>", s_title),
            Paragraph(f"<font size='8'>CNSS : {societe.cnss or ''}<br/>IF : {societe.if_fiscal or ''}<br/>PATENTE : {getattr(societe, 'patente', '') or ''}</font>", s_tdr)
        ]
    ]
    t_top = Table(data_top, colWidths=[65*mm, 60*mm, 65*mm])
    t_top.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(t_top)
    story.append(Spacer(1, 4*mm))

    # 2. GRILLE INFOS EMPLOYÉ (IDENTIQUE À L'IMAGE)
    # Ligne 1
    row1 = [
        Paragraph("Matricule", s_label), Paragraph("Ancienneté", s_label), 
        Paragraph("N° de Sécurité Sociale", s_label), Paragraph("N° Retraite", s_label), Paragraph("N° CIN", s_label)
    ]
    val1 = [
        Paragraph(employe.matricule or str(employe.id).zfill(4), s_value),
        Paragraph(f"{getattr(bulletin, 'anciennete_annees', 0)} an(s)", s_value),
        Paragraph(employe.numero_cnss or "—", s_value),
        Paragraph(employe.numero_retraite or "0", s_value),
        Paragraph(employe.cin or "—", s_value)
    ]
    
    # Ligne 2 (Emploi / Département)
    row2 = [[Paragraph("Emploi occupé", s_label), "", Paragraph("Département", s_label), "", ""]]
    val2 = [[Paragraph(employe.poste or "—", s_value), "", Paragraph(employe.departement or "—", s_value), "", ""]]
    
    # Ligne 3
    row3 = [
        Paragraph("N° Mutuelle", s_label), Paragraph("Date Entrée", s_label), 
        Paragraph("Date Naiss.", s_label), Paragraph("Situation Familiale", s_label), Paragraph("Nbre Enf.", s_label)
    ]
    val3 = [
        Paragraph(employe.numero_mutuelle or "0", s_value),
        Paragraph(employe.date_embauche.strftime('%d/%m/%y'), s_value),
        Paragraph(employe.date_naissance.strftime('%d/%m/%y') if employe.date_naissance else "—", s_value),
        Paragraph(employe.situation_familiale or "Célibataire", s_value),
        Paragraph(str(employe.nb_enfants), s_value)
    ]

    emp_grid_data = [row1, val1]
    t_emp = Table(emp_grid_data, colWidths=[38*mm]*5)
    t_emp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), VERT_ENTETE),
        ('GRID', (0,0), (-1,-1), 0.5, GRIS_BORDURE),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_emp)

    t_emp2 = Table([row2[0], val2[0]], colWidths=[95*mm, 0, 95*mm, 0, 0])
    t_emp2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), VERT_ENTETE),
        ('GRID', (0,0), (-1,-1), 0.5, GRIS_BORDURE),
        ('SPAN', (0,0), (1,0)), ('SPAN', (0,1), (1,1)),
        ('SPAN', (2,0), (4,0)), ('SPAN', (2,1), (4,1)),
    ]))
    story.append(t_emp2)

    t_emp3 = Table([row3, val3], colWidths=[38*mm]*5)
    t_emp3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), VERT_ENTETE),
        ('GRID', (0,0), (-1,-1), 0.5, GRIS_BORDURE),
    ]))
    story.append(t_emp3)
    story.append(Spacer(1, 4*mm))

    # 3. DATE DE PAIE ET NOM
    date_data = [
        [
            Paragraph(f"Date de Paie Du : 01/{bulletin.mois:02d}/{bulletin.annee % 100} Au : {last_day(bulletin.mois, bulletin.annee):02d}/{bulletin.mois:02d}/{bulletin.annee % 100}", s_td),
            Paragraph(f"<b>M &nbsp;&nbsp; {employe.nom.upper()} {employe.prenom or ''}</b><br/>{employe.adresse or ''}", s_td)
        ]
    ]
    t_date = Table(date_data, colWidths=[95*mm, 95*mm])
    t_date.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, GRIS_BORDURE), ('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(t_date)
    story.append(Spacer(1, 4*mm))

    # 4. TABLEAU DES RUBRIQUES (6 COLONNES)
    rub_header = [
        Paragraph("N°", s_th), Paragraph("Désignation", s_th), Paragraph("Nombre", s_th),
        Paragraph("Base", s_th), Paragraph("Taux", s_th), Paragraph("Gain", s_th), Paragraph("Retenue", s_th)
    ]
    rub_data = [rub_header]

    # Données dynamiques
    sbr = float(bulletin.salaire_base)
    # Lignes standards
    rub_data.append([Paragraph("1", s_tdc), Paragraph("Salaire de Base", s_td), Paragraph("26,00", s_tdc), Paragraph(fmt(sbr), s_tdr), "", Paragraph(fmt(sbr), s_tdr), ""])
    
    # Cotisations (Calculées dynamiquement pour l'exemple)
    if float(bulletin.cnss_salarie) > 0:
        base_cnss = min(float(bulletin.salaire_brut), 6000.0)
        rub_data.append([Paragraph("701", s_tdc), Paragraph("Cotisation CNSS", s_td), "", Paragraph(fmt(base_cnss), s_tdr), Paragraph("4,480", s_tdc), "", Paragraph(fmt(bulletin.cnss_salarie), s_tdr)])
    if float(bulletin.amo_salarie) > 0:
        rub_data.append([Paragraph("710", s_tdc), Paragraph("Cotisation AMO", s_td), "", Paragraph(fmt(bulletin.salaire_brut), s_tdr), Paragraph("2,260", s_tdc), "", Paragraph(fmt(bulletin.amo_salarie), s_tdr)])
    if float(bulletin.ir_retenu) > 0:
        rub_data.append([Paragraph("991", s_tdc), Paragraph("Retenue Impôts (IR)", s_td), "", "", "", "", Paragraph(fmt(bulletin.ir_retenu), s_tdr)])

    # Remplissage pour garder une hauteur constante
    while len(rub_data) < 15:
        rub_data.append(["", "", "", "", "", "", ""])

    t_rub = Table(rub_data, colWidths=[15*mm, 60*mm, 20*mm, 25*mm, 20*mm, 25*mm, 25*mm], rowHeights=6*mm)
    t_rub.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), VERT_ENTETE),
        ('GRID', (0,0), (-1,-1), 0.5, GRIS_BORDURE),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_rub)
    story.append(Spacer(1, 4*mm))

    # 5. PIED DE PAGE (CUMULS ET NET A PAYER)
    footer_head = [
        Paragraph("Cumuls", s_th), Paragraph("Brut imposable", s_th), Paragraph("Net imposable", s_th), 
        Paragraph("Retenue CNSS", s_th), Paragraph("Ret. AMO", s_th), Paragraph("Retenue Impôts", s_th),
        Paragraph("NET A PAYER", s_th)
    ]
    footer_vals = [
        Paragraph("Période", s_tdc), Paragraph(fmt(bulletin.salaire_brut), s_tdc), Paragraph(fmt(getattr(bulletin, 'net_imposable', 0)), s_tdc),
        Paragraph(fmt(bulletin.cnss_salarie), s_tdc), Paragraph(fmt(bulletin.amo_salarie), s_tdc), Paragraph(fmt(bulletin.ir_retenu), s_tdc),
        Paragraph(f"<b>{fmt(bulletin.salaire_net)}</b>", ParagraphStyle('Net', fontSize=12, fontName='Helvetica-Bold', alignment=TA_CENTER))
    ]
    t_foot = Table([footer_head, footer_vals], colWidths=[25*mm, 25*mm, 25*mm, 25*mm, 25*mm, 25*mm, 40*mm])
    t_foot.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), VERT_ENTETE),
        ('BACKGROUND', (-1,0), (-1,-1), VERT_ENTETE), # Net à payer en gris aussi
        ('GRID', (0,0), (-1,-1), 0.5, GRIS_BORDURE),
        ('SPAN', (-1,1), (-1,1)),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_foot)

    doc.build(story)
    return buffer.getvalue()
