from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, risk_engine
from ..database import get_db

router = APIRouter(prefix="/api/risks", tags=["risks"])


@router.get("")
def get_risk_drivers(db: Session = Depends(get_db)):
    """
    Aggregates organization-wide risk driver weights based on the same
    weighted-vulnerability / control-gap logic used in risk_engine, so the
    percentages shown are derived from the seeded dataset, not arbitrary.
    """
    assets = db.query(models.Asset).all()

    driver_totals = {
        "Critical vulnerabilities": 0.0,
        "Weak privileged access (no MFA)": 0.0,
        "Missing / weak endpoint detection": 0.0,
        "Poor network segmentation": 0.0,
        "Insufficient monitoring": 0.0,
        "Weak backup & recovery": 0.0,
    }

    for a in assets:
        crit_vulns = sum(1 for v in a.vulnerabilities if v.severity == "Critical" and not v.patched)
        driver_totals["Critical vulnerabilities"] += crit_vulns * 4

        controls = {c.control_name: c for c in a.controls}
        mfa = controls.get("MFA")
        if not mfa or not mfa.implemented or mfa.effectiveness < 0.5:
            driver_totals["Weak privileged access (no MFA)"] += a.criticality * 2

        edr = controls.get("EDR")
        if not edr or not edr.implemented or edr.effectiveness < 0.5:
            driver_totals["Missing / weak endpoint detection"] += a.criticality * 1.5

        seg = controls.get("Network Segmentation")
        if not seg or not seg.implemented or seg.effectiveness < 0.5:
            driver_totals["Poor network segmentation"] += a.criticality * 1.5

        mon = controls.get("Monitoring")
        if not mon or not mon.implemented or mon.effectiveness < 0.5:
            driver_totals["Insufficient monitoring"] += a.criticality * 1.2

        bkp = controls.get("Backup")
        if not bkp or not bkp.implemented or bkp.effectiveness < 0.5:
            driver_totals["Weak backup & recovery"] += a.criticality * 1.0

    total = sum(driver_totals.values()) or 1
    drivers = sorted(
        [{"driver": k, "weight_percent": round(v / total * 100, 1)} for k, v in driver_totals.items() if v > 0],
        key=lambda x: -x["weight_percent"],
    )

    # Per-asset risk score ranking for the "why is risk high" view
    asset_scores = []
    for a in assets:
        if a.risk_assessment:
            asset_scores.append({
                "asset": a.name,
                "risk_score": a.risk_assessment.risk_score,
                "risk_level": a.risk_assessment.risk_level,
                "expected_annual_loss": a.risk_assessment.expected_annual_loss,
            })
    asset_scores.sort(key=lambda x: -x["risk_score"])

    return {
        "top_risk_drivers": drivers,
        "asset_risk_ranking": asset_scores,
        "methodology_note": (
            "Driver weights are derived from unpatched critical vulnerabilities and "
            "control-effectiveness gaps (MFA, EDR, segmentation, monitoring, backup) "
            "across the seeded asset dataset, weighted by asset criticality. "
            "This is the prototype's simplified methodology, not an official SIH formula."
        ),
    }
