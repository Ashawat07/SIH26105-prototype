"""
Deterministic "AI Security Advisor".

Design note: this module deliberately does NOT call an external LLM. It
inspects the already-computed risk data (from risk_engine.py) and maps
missing / weak controls to a fixed catalog of security investments,
producing cost and risk-reduction numbers that come straight from the
backend calculation engine -- the "AI" layer never invents financial
figures on its own.

The module is structured so that a real LLM call could later be slotted in
to turn these structured recommendations into natural-language narrative,
without changing the underlying numbers (see `narrate()` stub).
"""
from sqlalchemy.orm import Session

from . import models, risk_engine

# Maps a security-control gap to the investment catalog action_key,
# a human readable problem statement, and the recommended action text.
CONTROL_GAP_MAP = [
    {
        "control_name": "MFA",
        "action_key": "mfa",
        "problem": "Privileged / user accounts do not require multi-factor authentication",
        "action": "Enable MFA for privileged and remote-access accounts",
    },
    {
        "control_name": "Patch Management",
        "action_key": "patch_management",
        "problem": "Known critical/high vulnerabilities remain unpatched",
        "action": "Patch critical and high-severity vulnerabilities",
    },
    {
        "control_name": "EDR",
        "action_key": "edr",
        "problem": "No endpoint detection & response coverage on this asset",
        "action": "Deploy Endpoint Detection & Response (EDR)",
    },
    {
        "control_name": "Network Segmentation",
        "action_key": "network_segmentation",
        "problem": "Asset sits on a flat network with insufficient segmentation",
        "action": "Implement network segmentation / micro-perimeters",
    },
    {
        "control_name": "Backup",
        "action_key": "backup",
        "problem": "Backup and recovery capability is weak or untested",
        "action": "Improve backup frequency, immutability and recovery testing",
    },
    {
        "control_name": "Monitoring",
        "action_key": "monitoring",
        "problem": "Insufficient logging / security monitoring coverage",
        "action": "Increase security monitoring and alerting coverage",
    },
]


def _priority_for_level(level: str) -> str:
    return level  # risk levels already map 1:1 to priority labels


def generate_recommendations_for_asset(db: Session, asset: models.Asset, investments: dict):
    """
    Build recommendation rows for a single asset based on which controls in
    CONTROL_GAP_MAP are NOT implemented (or implemented with low
    effectiveness) for that asset, using the asset's current EAL.
    """
    if asset.risk_assessment is None:
        return []

    eal = asset.risk_assessment.expected_annual_loss
    existing_controls = {c.control_name: c for c in asset.controls}

    recs = []
    for gap in CONTROL_GAP_MAP:
        control = existing_controls.get(gap["control_name"])
        already_strong = control is not None and control.implemented and control.effectiveness >= 0.7
        if already_strong:
            continue

        investment = investments.get(gap["action_key"])
        if investment is None:
            continue

        # Per-asset cost: scale the org-wide catalog cost down to a
        # single-asset rollout, weighted by criticality so bigger/more
        # critical assets cost a bit more to remediate.
        per_asset_cost = round(investment.cost * (0.08 + 0.03 * asset.criticality), -3)
        risk_reduction = round(eal * investment.risk_reduction_factor, 2)
        new_eal = round(max(0.0, eal - risk_reduction), 2)

        recs.append(
            models.Recommendation(
                asset_id=asset.id,
                action_key=gap["action_key"],
                problem=gap["problem"],
                recommended_action=gap["action"],
                estimated_cost=per_asset_cost,
                estimated_risk_reduction=risk_reduction,
                new_estimated_eal=new_eal,
                priority=_priority_for_level(asset.risk_assessment.risk_level),
            )
        )
    # Highest risk reduction first
    recs.sort(key=lambda r: r.estimated_risk_reduction, reverse=True)
    return recs


def regenerate_all_recommendations(db: Session):
    investments = {inv.action_key: inv for inv in db.query(models.Investment).all()}
    db.query(models.Recommendation).delete()
    assets = db.query(models.Asset).all()
    for asset in assets:
        recs = generate_recommendations_for_asset(db, asset, investments)
        for r in recs:
            db.add(r)
    db.commit()


def narrate(recommendation: models.Recommendation) -> str:
    """
    Stub for future LLM integration: given a structured recommendation,
    return a natural-language explanation. For the prototype this returns a
    deterministic template so no external API key is required.
    """
    return (
        f"{recommendation.recommended_action} addresses '{recommendation.problem}'. "
        f"Estimated implementation cost is derived from the organization-wide "
        f"investment catalog and scaled to this asset; estimated risk reduction "
        f"is calculated directly from this asset's Expected Annual Loss."
    )
