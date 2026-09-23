"""
Security Investment Optimization -- prototype methodology.

Given a fixed budget and the organization-wide investment catalog, select
the subset of investments that maximizes total financial risk reduction
without exceeding the budget. This is modeled as a classic 0/1 knapsack
problem:

    value(investment) = total_organization_EAL * risk_reduction_factor
    weight(investment) = investment.cost
    maximize sum(value) subject to sum(weight) <= budget

Combined reduction across multiple simultaneously-selected investments is
capped at 85% of total EAL, reflecting that overlapping controls have
diminishing marginal benefit in reality (a simplification, clearly labeled
as prototype methodology).
"""
from sqlalchemy.orm import Session

from . import models, risk_engine

MAX_COMBINED_REDUCTION_FRACTION = 0.85
BUCKET = 10_000  # INR granularity for the knapsack DP


def get_total_eal(db: Session) -> float:
    total = 0.0
    for ra in db.query(models.RiskAssessment).all():
        total += ra.expected_annual_loss
    return total


def optimize(db: Session, budget: float):
    investments = db.query(models.Investment).all()
    total_eal = get_total_eal(db)
    cap = total_eal * MAX_COMBINED_REDUCTION_FRACTION

    items = []
    for inv in investments:
        value = total_eal * inv.risk_reduction_factor
        weight_buckets = max(1, round(inv.cost / BUCKET))
        items.append({"inv": inv, "value": value, "cost": inv.cost, "w": weight_buckets})

    budget_buckets = max(1, int(budget // BUCKET))
    n = len(items)

    # dp[b] = best achievable value using budget b (in buckets)
    dp = [0.0] * (budget_buckets + 1)
    choice = [[False] * (budget_buckets + 1) for _ in range(n)]

    for i, item in enumerate(items):
        w, v = item["w"], item["value"]
        for b in range(budget_buckets, -1, -1):
            if w <= b and dp[b - w] + v > dp[b]:
                dp[b] = dp[b - w] + v
                choice[i][b] = True

    # Backtrack to find selected items
    selected = []
    b = budget_buckets
    for i in range(n - 1, -1, -1):
        if choice[i][b]:
            selected.append(items[i])
            b -= items[i]["w"]

    selected.reverse()

    raw_reduction = sum(s["value"] for s in selected)
    actual_reduction = min(raw_reduction, cap)
    # If the cap binds, scale down proportionally for display consistency
    scale = (actual_reduction / raw_reduction) if raw_reduction > 0 else 0

    total_cost = sum(s["cost"] for s in selected)
    risk_after = max(0.0, total_eal - actual_reduction)

    plan = [
        {
            "action_key": s["inv"].action_key,
            "name": s["inv"].name,
            "cost": s["cost"],
            "risk_reduction": round(s["value"] * scale, 2),
        }
        for s in selected
    ]

    rosi_value = risk_engine.rosi(actual_reduction, total_cost) if total_cost > 0 else 0.0

    return {
        "budget": budget,
        "total_investment": round(total_cost, 2),
        "risk_before": round(total_eal, 2),
        "risk_after": round(risk_after, 2),
        "risk_reduction": round(actual_reduction, 2),
        "rosi_percent": rosi_value,
        "plan": plan,
        "unselected": [
            {"action_key": it["inv"].action_key, "name": it["inv"].name, "cost": it["cost"]}
            for it in items
            if it["inv"].action_key not in [p["action_key"] for p in plan]
        ],
    }
