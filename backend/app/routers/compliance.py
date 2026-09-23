from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/compliance", tags=["compliance"])


@router.get("", response_model=List[schemas.ComplianceOut])
def get_compliance(db: Session = Depends(get_db)):
    items = db.query(models.ComplianceControl).all()
    return [
        schemas.ComplianceOut(
            id=c.id, finding=c.finding, status=c.status,
            frameworks=[f.strip() for f in c.frameworks.split(",")],
            recommended_action=c.recommended_action,
        ) for c in items
    ]
