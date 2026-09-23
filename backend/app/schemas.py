from pydantic import BaseModel
from typing import List, Optional


class VulnerabilityOut(BaseModel):
    id: int
    cve_like_id: str
    severity: str
    cvss_score: float
    description: str
    patched: bool

    class Config:
        from_attributes = True


class IncidentOut(BaseModel):
    id: int
    incident_type: str
    severity: str
    financial_loss: float

    class Config:
        from_attributes = True


class ControlOut(BaseModel):
    id: int
    control_name: str
    implemented: bool
    effectiveness: float

    class Config:
        from_attributes = True


class RiskAssessmentOut(BaseModel):
    incident_likelihood: float
    financial_impact: float
    expected_annual_loss: float
    value_at_risk_95: float
    risk_score: float
    risk_level: str

    class Config:
        from_attributes = True


class AssetSummaryOut(BaseModel):
    id: int
    name: str
    asset_type: str
    business_unit: str
    criticality: int
    vulnerability_count: int
    incident_count: int
    control_effectiveness: float
    incident_likelihood: float
    financial_impact: float
    expected_annual_loss: float
    risk_score: float
    risk_level: str


class AssetDetailOut(BaseModel):
    id: int
    name: str
    asset_type: str
    business_unit: str
    criticality: int
    control_effectiveness: float
    records_at_risk: int
    data_sensitivity: int
    vulnerabilities: List[VulnerabilityOut]
    incidents: List[IncidentOut]
    controls: List[ControlOut]
    risk: Optional[RiskAssessmentOut]
    impact_breakdown: dict


class RecommendationOut(BaseModel):
    id: int
    asset_id: int
    asset_name: str
    action_key: str
    problem: str
    recommended_action: str
    estimated_cost: float
    estimated_risk_reduction: float
    new_estimated_eal: float
    priority: str
    narrative: str


class SimulationRequest(BaseModel):
    action_key: str
    delay_days: int = 0


class SimulationOut(BaseModel):
    action_key: str
    action_name: str
    delay_days: int
    eal_before: float
    eal_after: float
    eal_after_with_delay: float
    risk_reduction: float
    risk_reduction_with_delay: float
    investment_cost: float
    delay_impact: float


class OptimizationRequest(BaseModel):
    budget: float


class ComplianceOut(BaseModel):
    id: int
    finding: str
    status: str
    frameworks: List[str]
    recommended_action: str

    class Config:
        from_attributes = True


class DashboardOut(BaseModel):
    organization: str
    enterprise_risk_score: float
    total_financial_exposure: float
    expected_annual_loss: float
    value_at_risk_95: float
    critical_risk_count: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    potential_risk_reduction: float
    security_budget: float
    risk_trend: List[dict]
    exposure_by_business_unit: List[dict]
    top_risk_contributors: List[dict]
    risk_distribution: List[dict]
    risk_reduction_opportunities: List[dict]
