from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

ORG_NAME = "Demo Financial Services Ltd."
SECURITY_BUDGET = 1_00_00_000  # INR 1 Crore, illustrative annual budget

# Illustrative 6-month risk trend (INR Crore), demonstrating a downward
# trend as remediation is assumed to have begun -- static demo series
# consistent with current EAL, not randomly generated per request.
TREND_MONTHS = ["Apr", "May", "Jun", "Jul", "Aug", "Sep"]


@router.get("", response_model=schemas.DashboardOut)
def get_dashboard(db: Session = Depends(get_db)):
    assessments = db.query(models.RiskAssessment).all()
    assets = {a.id: a for a in db.query(models.Asset).all()}

    total_exposure = sum(ra.financial_impact for ra in assessments)
    total_eal = sum(ra.expected_annual_loss for ra in assessments)
    total_var = sum(ra.value_at_risk_95 for ra in assessments)

    critical = sum(1 for ra in assessments if ra.risk_level == "Critical")
    high = sum(1 for ra in assessments if ra.risk_level == "High")
    medium = sum(1 for ra in assessments if ra.risk_level == "Medium")
    low = sum(1 for ra in assessments if ra.risk_level == "Low")

    enterprise_score = round(sum(ra.risk_score for ra in assessments) / max(1, len(assessments)), 1)

    recommendations = db.query(models.Recommendation).all()
    potential_reduction = sum(r.estimated_risk_reduction for r in recommendations)

    # EAL by business unit
    bu_exposure = {}
    for ra in assessments:
        asset = assets[ra.asset_id]
        bu_exposure.setdefault(asset.business_unit, 0)
        bu_exposure[asset.business_unit] += ra.financial_impact
    exposure_by_bu = [{"business_unit": k, "exposure": round(v, 2)} for k, v in
                       sorted(bu_exposure.items(), key=lambda x: -x[1])]

    # Top risk contributors (by EAL)
    contributors = sorted(
        [{"asset": assets[ra.asset_id].name, "eal": ra.expected_annual_loss} for ra in assessments],
        key=lambda x: -x["eal"],
    )[:6]

    risk_distribution = [
        {"level": "Critical", "count": critical},
        {"level": "High", "count": high},
        {"level": "Medium", "count": medium},
        {"level": "Low", "count": low},
    ]

    # Risk reduction opportunities aggregated by action across all recommendations
    reduction_by_action = {}
    for r in recommendations:
        reduction_by_action.setdefault(r.recommended_action, 0)
        reduction_by_action[r.recommended_action] += r.estimated_risk_reduction
    reduction_opportunities = sorted(
        [{"action": k, "risk_reduction": round(v, 2)} for k, v in reduction_by_action.items()],
        key=lambda x: -x["risk_reduction"],
    )[:6]

    # Simple deterministic trend ending at current EAL (demo storytelling data)
    risk_trend = []
    factor_series = [1.28, 1.22, 1.15, 1.10, 1.04, 1.00]
    for month, factor in zip(TREND_MONTHS, factor_series):
        risk_trend.append({"month": month, "eal": round(total_eal * factor, 2)})

    return schemas.DashboardOut(
        organization=ORG_NAME,
        enterprise_risk_score=enterprise_score,
        total_financial_exposure=round(total_exposure, 2),
        expected_annual_loss=round(total_eal, 2),
        value_at_risk_95=round(total_var, 2),
        critical_risk_count=critical,
        high_risk_count=high,
        medium_risk_count=medium,
        low_risk_count=low,
        potential_risk_reduction=round(potential_reduction, 2),
        security_budget=SECURITY_BUDGET,
        risk_trend=risk_trend,
        exposure_by_business_unit=exposure_by_bu,
        top_risk_contributors=contributors,
        risk_distribution=risk_distribution,
        risk_reduction_opportunities=reduction_opportunities,
    )
