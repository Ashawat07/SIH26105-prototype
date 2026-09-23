"""
What-if Simulation engine -- prototype methodology.

Applies a single security investment's org-wide risk_reduction_factor
against the current total Expected Annual Loss (EAL), and separately
models the effect of delaying that remediation.

Delay model (prototype methodology):
    Every 30 days of delay increases the applicable EAL base by 4%,
    representing continued exposure accumulation (unpatched vulnerabilities
    age, more incidents may occur, compounding risk). This is a simplified,
    clearly-labeled assumption -- not an actuarial model.
"""
from sqlalchemy.orm import Session

from . import models

DELAY_GROWTH_PER_30_DAYS = 0.04


def get_total_eal(db: Session) -> float:
    return sum(ra.expected_annual_loss for ra in db.query(models.RiskAssessment).all())


def simulate(db: Session, action_key: str, delay_days: int = 0):
    investment = db.query(models.Investment).filter(models.Investment.action_key == action_key).first()
    if investment is None:
        return None

    eal_before = get_total_eal(db)
    risk_reduction = eal_before * investment.risk_reduction_factor
    eal_after = max(0.0, eal_before - risk_reduction)

    # Delay impact: exposure compounds while remediation is postponed
    delay_periods = delay_days / 30.0
    delayed_base = eal_before * ((1 + DELAY_GROWTH_PER_30_DAYS) ** delay_periods)
    delay_impact = delayed_base - eal_before
    risk_reduction_with_delay = delayed_base * investment.risk_reduction_factor
    eal_after_with_delay = max(0.0, delayed_base - risk_reduction_with_delay)

    result = {
        "action_key": action_key,
        "action_name": investment.name,
        "delay_days": delay_days,
        "eal_before": round(eal_before, 2),
        "eal_after": round(eal_after, 2),
        "eal_after_with_delay": round(eal_after_with_delay, 2),
        "risk_reduction": round(risk_reduction, 2),
        "risk_reduction_with_delay": round(risk_reduction_with_delay, 2),
        "investment_cost": investment.cost,
        "delay_impact": round(delay_impact, 2),
    }

    db.add(models.SimulationResult(
        action_key=action_key, delay_days=delay_days,
        eal_before=eal_before, eal_after=eal_after,
        risk_reduction=risk_reduction, investment_cost=investment.cost,
    ))
    db.commit()

    return result
