from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, simulation_engine
from ..database import get_db

router = APIRouter(prefix="/api/simulation", tags=["simulation"])


@router.get("/actions")
def list_actions(db: Session = Depends(get_db)):
    investments = db.query(models.Investment).all()
    return [
        {"action_key": i.action_key, "name": i.name, "description": i.description, "cost": i.cost}
        for i in investments
    ]


@router.post("", response_model=schemas.SimulationOut)
def run_simulation(req: schemas.SimulationRequest, db: Session = Depends(get_db)):
    result = simulation_engine.simulate(db, req.action_key, req.delay_days)
    if result is None:
        raise HTTPException(status_code=404, detail="Unknown action_key")
    return result
