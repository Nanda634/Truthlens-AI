"""PDF forensic report generation - spec section 41."""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from app.config import settings

DISCLAIMER = (
    "Automated digital-authenticity analysis can identify signals associated with "
    "manipulation or synthetic generation, but no automated detector can guarantee "
    "authenticity or manipulation in every case. Results should be independently "
    "verified when used for legal, financial, employment, security, journalistic, "
    "or other high-stakes decisions."
)


def generate_report(analysis_id: str, file_info: dict, result: dict, signals: list, limitations: list) -> str:
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Small", fontSize=8, textColor=colors.grey))

    out_path = os.path.join(settings.REPORT_DIR, f"{analysis_id}.pdf")
    doc = SimpleDocTemplate(out_path, pagesize=letter)
    story = []

    story.append(Paragraph("TruthLens AI — Digital Forensic Report", styles["Title"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("1. Executive Summary", styles["Heading2"]))
    story.append(Paragraph(
        f"Classification: <b>{result['label']}</b> &nbsp;|&nbsp; "
        f"Confidence: <b>{result['confidence'] * 100:.1f}%</b> &nbsp;|&nbsp; "
        f"Risk: <b>{result['risk_score']}</b>/100", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("2. File Information", styles["Heading2"]))
    file_table = [
        ["Filename", file_info.get("name", "")],
        ["Type", file_info.get("type", "")],
        ["Size (bytes)", str(file_info.get("size", ""))],
        ["SHA-256", file_info.get("sha256", "")],
        ["Analysis ID", analysis_id],
    ]
    t = Table(file_table, colWidths=[120, 380])
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                            ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke)]))
    story.append(t)
    story.append(Spacer(1, 12))

    story.append(Paragraph("3. Evidence / Forensic Signals", styles["Heading2"]))
    sig_table = [["Type", "Signal", "Score", "Severity", "Description"]]
    for s in signals:
        score_str = f"{s.score:.2f}" if s.score is not None else "N/A"
        sig_table.append([s.signal_type, s.name, score_str, s.severity or "N/A", s.description[:80]])
    st = Table(sig_table, colWidths=[55, 110, 40, 50, 245])
    st.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]))
    story.append(st)
    story.append(Spacer(1, 12))

    story.append(Paragraph("4. Limitations", styles["Heading2"]))
    for lim in limitations:
        story.append(Paragraph(f"• {lim}", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("5. Final Assessment", styles["Heading2"]))
    story.append(Paragraph(
        f"Classification: <b>{result['label']}</b><br/>"
        f"Confidence: <b>{result['confidence'] * 100:.1f}%</b><br/>"
        f"Risk: <b>{result['risk_score']}</b>/100", styles["Normal"]))
    story.append(Spacer(1, 20))

    story.append(Paragraph(DISCLAIMER, styles["Small"]))

    doc.build(story)
    return out_path
