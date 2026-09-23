"""
============================================================================
PROTOTYPE RISK QUANTIFICATION METHODOLOGY  (SIH26105 demo)
============================================================================
DISCLAIMER: The formulas below are a SIMPLIFIED, INTERNALLY-CONSISTENT
methodology built for this hackathon prototype. They are NOT official SIH
formulas, NOT an actuarial standard, and NOT a substitute for a real FAIR /
ISO 27005 / NIST risk quantification exercise. They exist so that every
number shown in the UI is derived, traceable, and reproducible from the
same seeded dataset -- nothing is randomly displayed at request time.

----------------------------------------------------------------------------
1) INCIDENT LIKELIHOOD (annualized probability, 0-1)
----------------------------------------------------------------------------
    base_rate            = 0.22   (assumed baseline annual incident probability
                                    for a mid-size financial services asset)
    vuln_factor          = 1 + 0.05 * weighted_open_vulnerabilities
                              (Critical=4, High=2, Medium=1, Low=0.5 weight)
    incident_history_factor = 1 + 0.15 * incidents_last_12_months
    control_mitigation   = (1 - control_effectiveness)   [0..1]

    incident_likelihood = base_rate * vuln_factor * incident_history_factor
                           * control_mitigation
    -> clamped to [0.01, 0.95]

----------------------------------------------------------------------------
2) FINANCIAL IMPACT (Single Loss Expectancy, INR)
----------------------------------------------------------------------------
Financial impact is the sum of five components, each scaled by asset
criticality/sensitivity:

    downtime_cost     = base_downtime_cost_per_day * avg_downtime_days(criticality)
    data_breach_cost  = records_at_risk * cost_per_record (INR 1,200/record,
                          scaled by data_sensitivity/5)
    recovery_cost     = 0.08 * annual_revenue_dependency
    regulatory_cost   = data_sensitivity >= 4 ? 0.02 * annual_revenue_dependency : 0.005 * ...
    operational_loss  = 0.05 * annual_revenue_dependency * criticality/5

    financial_impact = downtime_cost + data_breach_cost + recovery_cost
                        + regulatory_cost + operational_loss

----------------------------------------------------------------------------
3) EXPECTED ANNUAL LOSS (EAL, INR)
----------------------------------------------------------------------------
    EAL = incident_likelihood * financial_impact

----------------------------------------------------------------------------
4) VALUE AT RISK (95th percentile annual loss, INR) -- simplified
----------------------------------------------------------------------------
We model annual loss as right-skewed, so VaR95 is approximated as a
multiple of EAL that grows with likelihood volatility:

    VaR_95 = EAL * (1.8 + incident_likelihood)
    (i.e. a low-likelihood/high-impact asset gets a higher tail multiplier)

----------------------------------------------------------------------------
5) RISK SCORE (0-100)
----------------------------------------------------------------------------
Weighted composite of five normalized (0-1) sub-scores:

    criticality_score   (weight 0.25) = criticality / 5
    vuln_score          (weight 0.25) = min(1, weighted_open_vulnerabilities / 20)
    exposure_score      (weight 0.20) = min(1, incident_likelihood / 0.5)
    control_gap_score   (weight 0.20) = 1 - control_effectiveness
    history_score       (weight 0.10) = min(1, incidents_last_12_months / 5)

    risk_score = 100 * (0.25*criticality_score + 0.25*vuln_score +
                         0.20*exposure_score + 0.20*control_gap_score +
                         0.10*history_score)

----------------------------------------------------------------------------
6) RISK LEVEL
----------------------------------------------------------------------------
    0-30   Low
    31-60  Medium
    61-80  High
    81-100 Critical

----------------------------------------------------------------------------
7) ROSI (Return on Security Investment) -- prototype methodology
----------------------------------------------------------------------------
    ROSI (%) = (Financial Risk Reduction - Security Investment Cost)
               / Security Investment Cost * 100
============================================================================
"""
from dataclasses import dataclass
from sqlalchemy.orm import Session

from . import models

SEVERITY_WEIGHT = {"Critical": 4, "High": 2, "Medium": 1, "Low": 0.5}
COST_PER_RECORD = 1200  # INR, illustrative breach-cost-per-record assumption (prototype scale)
BASE_INCIDENT_RATE = 0.22  # baseline annualized incident probability assumption (prototype scale)


def _avg_downtime_days(criticality: int) -> float:
    # More critical assets are assumed to have faster incident response,
    # but the business impact per day is higher (captured elsewhere).
    return {5: 3.0, 4: 2.5, 3: 2.0, 2: 1.5, 1: 1.0}.get(criticality, 2.0)


def weighted_open_vulnerabilities(vulns) -> float:
    return sum(SEVERITY_WEIGHT.get(v.severity, 0.5) for v in vulns if not v.patched)


def compute_incident_likelihood(asset: models.Asset, vulns, incidents_last_12mo: int) -> float:
    vuln_factor = 1 + 0.05 * weighted_open_vulnerabilities(vulns)
    history_factor = 1 + 0.15 * incidents_last_12mo
    control_mitigation = max(0.05, 1 - asset.control_effectiveness)
    likelihood = BASE_INCIDENT_RATE * vuln_factor * history_factor * control_mitigation
    return max(0.01, min(0.95, likelihood))


def compute_financial_impact(asset: models.Asset) -> dict:
    downtime_cost = asset.base_downtime_cost_per_day * _avg_downtime_days(asset.criticality)
    data_breach_cost = asset.records_at_risk * COST_PER_RECORD * (asset.data_sensitivity / 5)
    recovery_cost = 0.08 * asset.annual_revenue_dependency
    regulatory_cost = (0.02 if asset.data_sensitivity >= 4 else 0.005) * asset.annual_revenue_dependency
    operational_loss = 0.05 * asset.annual_revenue_dependency * (asset.criticality / 5)

    total = downtime_cost + data_breach_cost + recovery_cost + regulatory_cost + operational_loss
    return {
        "downtime_cost": downtime_cost,
        "data_breach_cost": data_breach_cost,
        "recovery_cost": recovery_cost,
        "regulatory_cost": regulatory_cost,
        "operational_loss": operational_loss,
        "total": total,
    }


def compute_risk_score(asset: models.Asset, vulns, incident_likelihood: float, incidents_last_12mo: int) -> float:
    criticality_score = asset.criticality / 5
    vuln_score = min(1.0, weighted_open_vulnerabilities(vulns) / 20)
    exposure_score = min(1.0, incident_likelihood / 0.5)
    control_gap_score = 1 - asset.control_effectiveness
    history_score = min(1.0, incidents_last_12mo / 5)

    score = 100 * (
        0.25 * criticality_score
        + 0.25 * vuln_score
        + 0.20 * exposure_score
        + 0.20 * control_gap_score
        + 0.10 * history_score
    )
    return round(min(100.0, max(0.0, score)), 1)


def risk_level_for_score(score: float) -> str:
    if score >= 81:
        return "Critical"
    if score >= 61:
        return "High"
    if score >= 31:
        return "Medium"
    return "Low"


@dataclass
class AssetRiskResult:
    incident_likelihood: float
    financial_impact: float
    expected_annual_loss: float
    value_at_risk_95: float
    risk_score: float
    risk_level: str
    impact_breakdown: dict


def evaluate_asset(asset: models.Asset) -> AssetRiskResult:
    vulns = asset.vulnerabilities
    incidents_last_12mo = len(asset.incidents)

    likelihood = compute_incident_likelihood(asset, vulns, incidents_last_12mo)
    impact_breakdown = compute_financial_impact(asset)
    financial_impact = impact_breakdown["total"]
    eal = likelihood * financial_impact
    var95 = eal * (1.8 + likelihood)
    score = compute_risk_score(asset, vulns, likelihood, incidents_last_12mo)
    level = risk_level_for_score(score)

    return AssetRiskResult(
        incident_likelihood=round(likelihood, 4),
        financial_impact=round(financial_impact, 2),
        expected_annual_loss=round(eal, 2),
        value_at_risk_95=round(var95, 2),
        risk_score=score,
        risk_level=level,
        impact_breakdown=impact_breakdown,
    )


def recalculate_all(db: Session):
    """Recompute and persist risk assessments for every asset."""
    assets = db.query(models.Asset).all()
    for asset in assets:
        result = evaluate_asset(asset)
        ra = asset.risk_assessment
        if ra is None:
            ra = models.RiskAssessment(asset_id=asset.id)
            db.add(ra)
        ra.incident_likelihood = result.incident_likelihood
        ra.financial_impact = result.financial_impact
        ra.expected_annual_loss = result.expected_annual_loss
        ra.value_at_risk_95 = result.value_at_risk_95
        ra.risk_score = result.risk_score
        ra.risk_level = result.risk_level
    db.commit()


def rosi(risk_reduction: float, investment_cost: float) -> float:
    """Return on Security Investment, percentage. Prototype methodology."""
    if investment_cost <= 0:
        return 0.0
    return round((risk_reduction - investment_cost) / investment_cost * 100, 1)
