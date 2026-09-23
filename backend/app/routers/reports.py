import io
import os
import tempfile
from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from .. import models
from ..database import get_db

router = APIRouter(prefix="/api/reports", tags=["reports"])

ORG_NAME = "Demo Financial Services Ltd."


def _inr(value: float) -> str:
    if value >= 1_00_00_000:
        return f"Rs. {value / 1_00_00_000:.2f} Cr"
    if value >= 1_00_000:
        return f"Rs. {value / 1_00_000:.2f} L"
    return f"Rs. {value:,.0f}"


@router.post("")
def generate_report(db: Session = Depends(get_db)):
    assessments = db.query(models.RiskAssessment).all()
    assets = {a.id: a for a in db.query(models.Asset).all()}
    recommendations = db.query(models.Recommendation).all()
    compliance = db.query(models.ComplianceControl).all()

    total_exposure = sum(ra.financial_impact for ra in assessments)
    total_eal = sum(ra.expected_annual_loss for ra in assessments)
    enterprise_score = round(sum(ra.risk_score for ra in assessments) / max(1, len(assessments)), 1)
    potential_reduction = sum(r.estimated_risk_reduction for r in recommendations)

    top_risks = sorted(
        [(assets[ra.asset_id].name, ra) for ra in assessments], key=lambda x: -x[1].risk_score
    )[:5]

    top_recs = sorted(recommendations, key=lambda r: -r.estimated_risk_reduction)[:5]
    gaps = [c for c in compliance if c.status == "Gap"]

    tmp_path = os.path.join(tempfile.gettempdir(), f"cyber_risk_report_{int(datetime.utcnow().timestamp())}.pdf")
    doc = SimpleDocTemplate(tmp_path, pagesize=A4, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], fontSize=18)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], spaceBefore=14, spaceAfter=6)
    body = styles["BodyText"]

    story = []
    story.append(Paragraph("Cyber Risk Quantification & Investment Optimization Report", title_style))
    story.append(Paragraph(f"{ORG_NAME} &nbsp;|&nbsp; Generated: {datetime.utcnow().strftime('%d %b %Y')}", body))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Enterprise Risk Summary", h2))
    summary_data = [
        ["Enterprise Risk Score", f"{enterprise_score} / 100"],
        ["Total Financial Exposure", _inr(total_exposure)],
        ["Expected Annual Loss (EAL)", _inr(total_eal)],
        ["Potential Risk Reduction", _inr(potential_reduction)],
        ["Assets Assessed", str(len(assessments))],
    ]
    t = Table(summary_data, colWidths=[8 * cm, 8 * cm])
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(t)

    story.append(Paragraph("Top Risks", h2))
    risk_data = [["Asset", "Risk Score", "Risk Level", "Expected Annual Loss"]]
    for name, ra in top_risks:
        risk_data.append([name, str(ra.risk_score), ra.risk_level, _inr(ra.expected_annual_loss)])
    t = Table(risk_data, colWidths=[5.5 * cm, 3 * cm, 3 * cm, 4.5 * cm])
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story.append(t)

    story.append(Paragraph("Recommended Investments (Top 5 by Risk Reduction)", h2))
    rec_data = [["Asset", "Recommended Action", "Cost", "Risk Reduction", "Priority"]]
    for r in top_recs:
        rec_data.append([
            assets[r.asset_id].name, r.recommended_action, _inr(r.estimated_cost),
            _inr(r.estimated_risk_reduction), r.priority,
        ])
    t = Table(rec_data, colWidths=[3.5 * cm, 5.5 * cm, 2.5 * cm, 3 * cm, 2 * cm])
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]))
    story.append(t)

    story.append(Paragraph("Compliance Gaps", h2))
    gap_data = [["Finding", "Frameworks", "Recommended Action"]]
    for g in gaps:
        gap_data.append([g.finding, g.frameworks.replace(",", ", "), g.recommended_action])
    t = Table(gap_data, colWidths=[5.5 * cm, 5 * cm, 5.5 * cm])
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]))
    story.append(t)

    story.append(Spacer(1, 16))
    story.append(Paragraph(
        "Note: All figures are generated using the prototype's simplified, internally-consistent "
        "risk quantification methodology (see backend/app/risk_engine.py) applied to the seeded "
        "demo dataset. This is a Smart India Hackathon prototype, not an audited financial report.",
        ParagraphStyle("Note", parent=styles["BodyText"], fontSize=8, textColor=colors.grey),
    ))

    doc.build(story)

    return FileResponse(tmp_path, media_type="application/pdf", filename="cyber_risk_report.pdf")
