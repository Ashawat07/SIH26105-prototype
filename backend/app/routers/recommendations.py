from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, recommendation_engine
from ..database import get_db

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.get("", response_model=List[schemas.RecommendationOut])
def get_recommendations(db: Session = Depends(get_db)):
    recs = db.query(models.Recommendation).all()
    assets = {a.id: a for a in db.query(models.Asset).all()}
    out = []
    for r in recs:
        out.append(schemas.RecommendationOut(
            id=r.id, asset_id=r.asset_id, asset_name=assets[r.asset_id].name,
            action_key=r.action_key, problem=r.problem,
            recommended_action=r.recommended_action,
            estimated_cost=r.estimated_cost,
            estimated_risk_reduction=r.estimated_risk_reduction,
            new_estimated_eal=r.new_estimated_eal,
            priority=r.priority,
            narrative=recommendation_engine.narrate(r),
        ))
    out.sort(key=lambda x: -x.estimated_risk_reduction)
    return out


@router.post("/regenerate")
def regenerate(db: Session = Depends(get_db)):
    recommendation_engine.regenerate_all_recommendations(db)
    return {"status": "ok"}
