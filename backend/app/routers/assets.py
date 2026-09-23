from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, risk_engine
from ..database import get_db

router = APIRouter(prefix="/api/assets", tags=["assets"])


@router.get("", response_model=List[schemas.AssetSummaryOut])
def list_assets(db: Session = Depends(get_db)):
    assets = db.query(models.Asset).all()
    out = []
    for a in assets:
        ra = a.risk_assessment
        out.append(schemas.AssetSummaryOut(
            id=a.id, name=a.name, asset_type=a.asset_type, business_unit=a.business_unit,
            criticality=a.criticality,
            vulnerability_count=len(a.vulnerabilities),
            incident_count=len(a.incidents),
            control_effectiveness=a.control_effectiveness,
            incident_likelihood=ra.incident_likelihood if ra else 0,
            financial_impact=ra.financial_impact if ra else 0,
            expected_annual_loss=ra.expected_annual_loss if ra else 0,
            risk_score=ra.risk_score if ra else 0,
            risk_level=ra.risk_level if ra else "Low",
        ))
    return sorted(out, key=lambda x: -x.risk_score)


@router.get("/{asset_id}", response_model=schemas.AssetDetailOut)
def get_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    result = risk_engine.evaluate_asset(asset)

    return schemas.AssetDetailOut(
        id=asset.id, name=asset.name, asset_type=asset.asset_type,
        business_unit=asset.business_unit, criticality=asset.criticality,
        control_effectiveness=asset.control_effectiveness,
        records_at_risk=asset.records_at_risk, data_sensitivity=asset.data_sensitivity,
        vulnerabilities=[schemas.VulnerabilityOut(
            id=v.id, cve_like_id=v.cve_like_id, severity=v.severity,
            cvss_score=v.cvss_score, description=v.description, patched=bool(v.patched),
        ) for v in asset.vulnerabilities],
        incidents=[schemas.IncidentOut(
            id=i.id, incident_type=i.incident_type, severity=i.severity, financial_loss=i.financial_loss,
        ) for i in asset.incidents],
        controls=[schemas.ControlOut(
            id=c.id, control_name=c.control_name, implemented=bool(c.implemented), effectiveness=c.effectiveness,
        ) for c in asset.controls],
        risk=schemas.RiskAssessmentOut(
            incident_likelihood=result.incident_likelihood,
            financial_impact=result.financial_impact,
            expected_annual_loss=result.expected_annual_loss,
            value_at_risk_95=result.value_at_risk_95,
            risk_score=result.risk_score,
            risk_level=result.risk_level,
        ),
        impact_breakdown=result.impact_breakdown,
    )
