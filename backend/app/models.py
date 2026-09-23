"""
ORM models for the SIH26105 prototype: "AI-Powered Continuous Cyber Risk
Quantification and Investment Optimization Platform".

Table set (kept minimal per prototype scope):
    assets, vulnerabilities, incidents, security_controls,
    risk_assessments, recommendations, investments,
    simulation_results, compliance_controls
"""
from sqlalchemy import (
    Column, Integer, String, Float, ForeignKey, DateTime, Text
)
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    asset_type = Column(String, nullable=False)
    business_unit = Column(String, nullable=False)
    criticality = Column(Integer, nullable=False)  # 1-5 (5 = most critical)
    control_effectiveness = Column(Float, nullable=False)  # 0-1 (fraction of risk mitigated by existing controls)
    annual_revenue_dependency = Column(Float, nullable=False)  # INR, revenue that depends on this asset being up
    base_downtime_cost_per_day = Column(Float, nullable=False)  # INR
    data_sensitivity = Column(Integer, nullable=False)  # 1-5 (5 = most sensitive, e.g. PII/PCI/financial)
    records_at_risk = Column(Integer, nullable=False, default=0)

    vulnerabilities = relationship("Vulnerability", back_populates="asset", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="asset", cascade="all, delete-orphan")
    controls = relationship("SecurityControl", back_populates="asset", cascade="all, delete-orphan")
    risk_assessment = relationship("RiskAssessment", back_populates="asset", uselist=False, cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="asset", cascade="all, delete-orphan")


class Vulnerability(Base):
    __tablename__ = "vulnerabilities"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    cve_like_id = Column(String, nullable=False)
    severity = Column(String, nullable=False)  # Low / Medium / High / Critical
    cvss_score = Column(Float, nullable=False)
    description = Column(String, nullable=False)
    patched = Column(Integer, default=0)  # 0/1

    asset = relationship("Asset", back_populates="vulnerabilities")


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    incident_type = Column(String, nullable=False)
    occurred_at = Column(DateTime, default=datetime.utcnow)
    severity = Column(String, nullable=False)
    financial_loss = Column(Float, default=0)

    asset = relationship("Asset", back_populates="incidents")


class SecurityControl(Base):
    __tablename__ = "security_controls"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    control_name = Column(String, nullable=False)  # e.g. MFA, EDR, Segmentation
    implemented = Column(Integer, default=0)  # 0/1
    effectiveness = Column(Float, default=0)  # 0-1 contribution

    asset = relationship("Asset", back_populates="controls")


class RiskAssessment(Base):
    """
    Stores the latest computed risk output for an asset so the frontend can
    read pre-calculated values without recomputation on every request.
    Recomputed by risk_engine.recalculate_all() on data changes / demand.
    """
    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), unique=True)

    incident_likelihood = Column(Float, nullable=False)  # 0-1 annualized probability
    financial_impact = Column(Float, nullable=False)  # INR, single-loss expectancy
    expected_annual_loss = Column(Float, nullable=False)  # INR
    value_at_risk_95 = Column(Float, nullable=False)  # INR, 95th percentile annual loss estimate
    risk_score = Column(Float, nullable=False)  # 0-100
    risk_level = Column(String, nullable=False)  # Low/Medium/High/Critical
    updated_at = Column(DateTime, default=datetime.utcnow)

    asset = relationship("Asset", back_populates="risk_assessment")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    action_key = Column(String, nullable=False)  # matches Investment.action_key
    problem = Column(String, nullable=False)
    recommended_action = Column(String, nullable=False)
    estimated_cost = Column(Float, nullable=False)
    estimated_risk_reduction = Column(Float, nullable=False)
    new_estimated_eal = Column(Float, nullable=False)
    priority = Column(String, nullable=False)  # Low/Medium/High/Critical

    asset = relationship("Asset", back_populates="recommendations")


class Investment(Base):
    """
    Organization-wide catalog of available security investments used by the
    What-if Simulation and Investment Optimization modules.
    """
    __tablename__ = "investments"

    id = Column(Integer, primary_key=True, index=True)
    action_key = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    cost = Column(Float, nullable=False)  # INR, org-wide rollout cost
    risk_reduction_factor = Column(Float, nullable=False)  # 0-1, fraction of EAL this action mitigates when applied org-wide


class SimulationResult(Base):
    __tablename__ = "simulation_results"

    id = Column(Integer, primary_key=True, index=True)
    action_key = Column(String, nullable=False)
    delay_days = Column(Integer, default=0)
    eal_before = Column(Float, nullable=False)
    eal_after = Column(Float, nullable=False)
    risk_reduction = Column(Float, nullable=False)
    investment_cost = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ComplianceControl(Base):
    __tablename__ = "compliance_controls"

    id = Column(Integer, primary_key=True, index=True)
    finding = Column(String, nullable=False)
    status = Column(String, nullable=False)  # Gap / Partial / Compliant
    frameworks = Column(String, nullable=False)  # comma separated
    recommended_action = Column(String, nullable=False)
