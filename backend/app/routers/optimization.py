from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import schemas, optimization_engine
from ..database import get_db

router = APIRouter(prefix="/api/optimization", tags=["optimization"])


@router.post("")
def optimize(req: schemas.OptimizationRequest, db: Session = Depends(get_db)):
    return optimization_engine.optimize(db, req.budget)
