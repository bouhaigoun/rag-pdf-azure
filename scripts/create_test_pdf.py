from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

output_path = Path("docs/test_contrat.pdf")
output_path.parent.mkdir(exist_ok=True)

doc = SimpleDocTemplate(
    str(output_path),
    pagesize=A4,
    leftMargin=3 * cm,
    rightMargin=3 * cm,
    topMargin=3 * cm,
    bottomMargin=3 * cm,
)

styles = getSampleStyleSheet()
title_style = ParagraphStyle("title", parent=styles["Heading1"], alignment=TA_CENTER, spaceAfter=24)
heading_style = ParagraphStyle("heading", parent=styles["Heading2"], spaceBefore=16, spaceAfter=8)
body_style = ParagraphStyle("body", parent=styles["Normal"], alignment=TA_JUSTIFY, spaceAfter=6)

content = [
    Paragraph("CONTRAT DE PRESTATION DE SERVICES IT", title_style),
    Spacer(1, 0.5 * cm),
    Paragraph("Article 1 - Objet", heading_style),
    Paragraph(
        "La société CLIENT SAS confie au prestataire NABIL BOUHAIGOUN une mission de Chef de Projet IT "
        "spécialisé en automatisation IA et intégration Azure.",
        body_style,
    ),
    Paragraph("Article 2 - Durée", heading_style),
    Paragraph(
        "La mission débute le 1er juin 2026 pour une durée de 3 mois renouvelable.",
        body_style,
    ),
    Paragraph("Article 3 - Tarification", heading_style),
    Paragraph(
        "Le tarif journalier est fixé à 500 euros HT soit 7500 euros HT pour la durée totale.",
        body_style,
    ),
    Paragraph("Article 4 - Livrables", heading_style),
    Paragraph("- Agent IA connecté à Notion via n8n", body_style),
    Paragraph("- Pipeline RAG PDF sur Azure AI Search", body_style),
    Paragraph("- Documentation technique et README GitHub", body_style),
    Paragraph("- Formation utilisateur de 2 heures", body_style),
    Paragraph("Article 5 - Confidentialité", heading_style),
    Paragraph(
        "Le prestataire s'engage à respecter la confidentialité des données client conformément au RGPD.",
        body_style,
    ),
]

doc.build(content)
print(f"[OK] PDF généré : {output_path.resolve()}")
