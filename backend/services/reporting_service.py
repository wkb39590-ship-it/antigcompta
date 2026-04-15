from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from io import BytesIO
from datetime import datetime

class ReportingService:
    @staticmethod
    def generate_bilan_pdf(bilan_data: dict, societe_info: dict) -> BytesIO:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        elements = []
        styles = getSampleStyleSheet()

        # En-tête de la société
        h1_style = ParagraphStyle('Heading1', parent=styles['Heading1'], fontSize=16, spaceAfter=4)
        sub_style = ParagraphStyle('Sub', parent=styles['Normal'], fontSize=9, textColor=colors.grey)
        
        elements.append(Paragraph(societe_info.get('raison_sociale', 'SOCIETE'), h1_style))
        elements.append(Paragraph(f"ICE : {societe_info.get('ice', '-')}", sub_style))
        elements.append(Paragraph(f"Adresse : {societe_info.get('adresse', '-')}", sub_style))
        elements.append(Spacer(1, 20))

        # Titre du document
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=20, alignment=1, spaceAfter=20)
        elements.append(Paragraph(f"BILAN COMPTABLE - EXERCICE {bilan_data['annee']}", title_style))
        
        # Données Actif et Passif (Côté à côte)
        # On va créer une table principale avec 2 colonnes : Actif | Passif
        
        def format_currency(val):
            return "{:,.2f}".format(float(val)).replace(",", " ").replace(".", ",")

        # Préparation du contenu Actif
        actif_rows = [["ACTIF", "BRUT", "AMORT.", "NET"]]
        for rub in bilan_data['actif']:
            actif_rows.append([
                Paragraph(f"<b>{rub['libelle']}</b>", styles['Normal']), 
                format_currency(rub.get('total_brut', 0)), 
                format_currency(rub.get('total_amortissement', 0)), 
                format_currency(rub['total'])
            ])
            for l in rub['lignes']:
                safelabel = str(l.get('account_label') or '')[:30]
                actif_rows.append([f"  {l['account_code']} - {safelabel}", format_currency(l['brut']), format_currency(l['amortissement']), format_currency(l['net'])])
        
        # Préparation du contenu Passif
        passif_rows = [["PASSIF", "MONTANT"]]
        for rub in bilan_data['passif']:
            passif_rows.append([Paragraph(f"<b>{rub['libelle']}</b>", styles['Normal']), format_currency(rub['total'])])
            for l in rub['lignes']:
                safelabel = str(l.get('account_label') or '')[:30]
                passif_rows.append([f"  {l['account_code']} - {safelabel}", format_currency(l['net'])])
        
        # Résultat
        passif_rows.append([Paragraph("<b>RESULTAT NET</b>", styles['Normal']), format_currency(bilan_data['resultat'])])

        # Création de la table de comparaison
        # Puisque les listes sont de longueurs différentes, on les unifie
        max_len = max(len(actif_rows), len(passif_rows))
        unified_rows = []
        for i in range(max_len):
            a = actif_rows[i] if i < len(actif_rows) else ["", "", "", ""]
            p = passif_rows[i] if i < len(passif_rows) else ["", ""]
            unified_rows.append(a + p)

        # Totaux Généraux
        unified_rows.append([
            Paragraph("<b>TOTAL GENERAL ACTIF</b>", styles['Normal']), "", "", format_currency(bilan_data['total_actif']),
            Paragraph("<b>TOTAL GENERAL PASSIF</b>", styles['Normal']), format_currency(bilan_data['total_passif'])
        ])

        t = Table(unified_rows, colWidths=[200, 60, 60, 80, 200, 80])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (3, 0), colors.HexColor("#059669")),
            ('TEXTCOLOR', (0, 0), (3, 0), colors.whitesmoke),
            ('BACKGROUND', (4, 0), (5, 0), colors.HexColor("#4f46e5")),
            ('TEXTCOLOR', (4, 0), (5, 0), colors.whitesmoke),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.black),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))

        elements.append(t)
        
        # Footer
        elements.append(Spacer(1, 30))
        footer_text = f"Généré le {datetime.now().strftime('%d/%m/%Y %H:%M')} par COMPTAFACILE"
        elements.append(Paragraph(footer_text, sub_style))

        doc.build(elements)
        buffer.seek(0)
        return buffer
