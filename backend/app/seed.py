"""
Seeds the SQLite database with a realistic demo dataset for
"Demo Financial Services Ltd." All dashboard/risk/simulation/optimization
numbers in the prototype are derived from this same seeded data --
nothing is randomly generated at request time.
"""
from datetime import datetime, timedelta

from .database import Base, engine, SessionLocal
from . import models, risk_engine, recommendation_engine


# NOTE: these values were deliberately tuned (see backend validation notes)
# so that the resulting Expected Annual Loss / exposure figures land in a
# realistic, demo-friendly range (a few crore INR total) once run through
# risk_engine.py -- they are not arbitrary.
ASSETS = [
    dict(name="Customer Database", asset_type="Database", business_unit="Retail Banking",
         criticality=5, control_effectiveness=0.35, annual_revenue_dependency=1_50_00_000,
         base_downtime_cost_per_day=1_50_000, data_sensitivity=5, records_at_risk=8_000),
    dict(name="Payment Gateway", asset_type="Application", business_unit="Payments",
         criticality=5, control_effectiveness=0.25, annual_revenue_dependency=2_00_00_000,
         base_downtime_cost_per_day=2_00_000, data_sensitivity=5, records_at_risk=5_000),
    dict(name="Internet Banking Server", asset_type="Server", business_unit="Digital Banking",
         criticality=5, control_effectiveness=0.40, annual_revenue_dependency=1_80_00_000,
         base_downtime_cost_per_day=1_80_000, data_sensitivity=5, records_at_risk=6_000),
    dict(name="Employee Portal", asset_type="Application", business_unit="Corporate IT",
         criticality=2, control_effectiveness=0.65, annual_revenue_dependency=25_00_000,
         base_downtime_cost_per_day=15_000, data_sensitivity=2, records_at_risk=500),
    dict(name="Email Server", asset_type="Infrastructure", business_unit="Corporate IT",
         criticality=3, control_effectiveness=0.50, annual_revenue_dependency=40_00_000,
         base_downtime_cost_per_day=25_000, data_sensitivity=3, records_at_risk=2_000),
    dict(name="Cloud Storage", asset_type="Storage", business_unit="Corporate IT",
         criticality=3, control_effectiveness=0.45, annual_revenue_dependency=60_00_000,
         base_downtime_cost_per_day=35_000, data_sensitivity=4, records_at_risk=4_000),
    dict(name="HR System", asset_type="Application", business_unit="Human Resources",
         criticality=2, control_effectiveness=0.58, annual_revenue_dependency=30_00_000,
         base_downtime_cost_per_day=12_000, data_sensitivity=3, records_at_risk=1_500),
    dict(name="Backup Server", asset_type="Infrastructure", business_unit="Corporate IT",
         criticality=3, control_effectiveness=0.42, annual_revenue_dependency=50_00_000,
         base_downtime_cost_per_day=20_000, data_sensitivity=3, records_at_risk=0),
    dict(name="Production Server", asset_type="Server", business_unit="Core Banking",
         criticality=5, control_effectiveness=0.38, annual_revenue_dependency=2_20_00_000,
         base_downtime_cost_per_day=2_20_000, data_sensitivity=4, records_at_risk=3_000),
    dict(name="API Gateway", asset_type="Application", business_unit="Digital Banking",
         criticality=4, control_effectiveness=0.48, annual_revenue_dependency=1_00_00_000,
         base_downtime_cost_per_day=90_000, data_sensitivity=4, records_at_risk=3_500),
]

# vulnerabilities keyed by asset name
VULNS = {
    "Customer Database": [
        ("CVE-DEMO-1001", "Critical", 9.1, "Unpatched SQL injection vector in legacy query module", False),
        ("CVE-DEMO-1002", "Critical", 9.0, "Encryption at rest not enforced for sensitive tables", False),
        ("CVE-DEMO-1003", "High", 7.8, "Excessive database privileges granted to service account", False),
        ("CVE-DEMO-1004", "Medium", 5.4, "Outdated database engine minor version", False),
    ],
    "Payment Gateway": [
        ("CVE-DEMO-1101", "Critical", 9.4, "Weak TLS configuration on payment API endpoint", False),
        ("CVE-DEMO-1102", "Critical", 9.0, "Privileged accounts without MFA", False),
        ("CVE-DEMO-1103", "Critical", 9.2, "Hardcoded credentials found in deployment scripts", False),
        ("CVE-DEMO-1104", "High", 7.2, "Insufficient input validation on transaction API", False),
        ("CVE-DEMO-1105", "Medium", 5.0, "Verbose error messages leak stack traces", False),
    ],
    "Internet Banking Server": [
        ("CVE-DEMO-1201", "Critical", 9.2, "Outdated web server software with known RCE", False),
        ("CVE-DEMO-1202", "High", 7.6, "Session tokens do not expire promptly", False),
        ("CVE-DEMO-1203", "High", 7.1, "Missing rate limiting on login endpoint", False),
        ("CVE-DEMO-1204", "Medium", 5.3, "Weak password complexity policy for customer accounts", False),
    ],
    "Employee Portal": [
        ("CVE-DEMO-1301", "Medium", 5.2, "Outdated JavaScript dependency with known XSS", False),
        ("CVE-DEMO-1302", "Low", 3.1, "Verbose server banner disclosure", True),
    ],
    "Email Server": [
        ("CVE-DEMO-1401", "High", 7.4, "Missing SPF/DKIM/DMARC hardening enables spoofing", False),
        ("CVE-DEMO-1402", "Medium", 5.5, "Outdated mail transfer agent version", False),
    ],
    "Cloud Storage": [
        ("CVE-DEMO-1501", "Critical", 8.9, "Misconfigured storage bucket permissions", False),
        ("CVE-DEMO-1502", "Medium", 5.0, "Encryption at rest not enforced organization-wide", False),
    ],
    "HR System": [
        ("CVE-DEMO-1601", "Medium", 5.6, "Weak password policy for HR portal accounts", False),
        ("CVE-DEMO-1602", "Low", 3.4, "Outdated plugin with minor disclosure risk", True),
    ],
    "Backup Server": [
        ("CVE-DEMO-1701", "High", 7.0, "Backup repository accessible without MFA", False),
        ("CVE-DEMO-1702", "Medium", 5.3, "Backup integrity checks not automated", False),
    ],
    "Production Server": [
        ("CVE-DEMO-1801", "Critical", 9.3, "Unpatched OS kernel vulnerability", False),
        ("CVE-DEMO-1802", "Critical", 9.0, "Default credentials on management console", False),
        ("CVE-DEMO-1803", "High", 7.5, "Flat network segment shared with lower-trust systems", False),
        ("CVE-DEMO-1804", "Medium", 5.1, "Excessive open ports on management interface", False),
    ],
    "API Gateway": [
        ("CVE-DEMO-1901", "High", 7.3, "API keys not rotated regularly", False),
        ("CVE-DEMO-1902", "Medium", 5.4, "Missing schema validation on inbound requests", False),
    ],
}

# incidents in the last 12 months, keyed by asset name
INCIDENTS = {
    "Customer Database": [
        ("Data exfiltration attempt", "High", 0),
        ("Unauthorized privileged access", "Medium", 1_50_000),
    ],
    "Payment Gateway": [
        ("Credential stuffing attack", "Critical", 12_00_000),
        ("Fraudulent transaction spike", "High", 6_00_000),
        ("API abuse / scraping incident", "Medium", 1_00_000),
    ],
    "Internet Banking Server": [
        ("Account takeover attempt", "High", 4_00_000),
        ("Brute-force login campaign", "Medium", 50_000),
    ],
    "Production Server": [
        ("Ransomware attempt (contained)", "Critical", 0),
        ("Suspicious lateral movement detected", "High", 2_00_000),
    ],
    "Cloud Storage": [("Misconfigured bucket exposure", "Medium", 2_00_000)],
}

# controls keyed by asset name -> list of (control_name, implemented, effectiveness)
CONTROL_NAMES = ["MFA", "Patch Management", "EDR", "Network Segmentation", "Backup", "Monitoring"]
CONTROLS = {
    "Customer Database": [("MFA", True, 0.75), ("Patch Management", False, 0.2), ("EDR", True, 0.65),
                           ("Network Segmentation", True, 0.6), ("Backup", True, 0.7), ("Monitoring", False, 0.3)],
    "Payment Gateway": [("MFA", False, 0.1), ("Patch Management", False, 0.25), ("EDR", True, 0.6),
                         ("Network Segmentation", False, 0.2), ("Backup", True, 0.7), ("Monitoring", True, 0.55)],
    "Internet Banking Server": [("MFA", True, 0.7), ("Patch Management", False, 0.2), ("EDR", False, 0.15),
                                 ("Network Segmentation", True, 0.6), ("Backup", True, 0.65), ("Monitoring", True, 0.5)],
    "Employee Portal": [("MFA", True, 0.8), ("Patch Management", True, 0.7), ("EDR", True, 0.7),
                         ("Network Segmentation", True, 0.65), ("Backup", True, 0.7), ("Monitoring", True, 0.6)],
    "Email Server": [("MFA", True, 0.6), ("Patch Management", False, 0.25), ("EDR", False, 0.2),
                      ("Network Segmentation", True, 0.5), ("Backup", True, 0.6), ("Monitoring", False, 0.3)],
    "Cloud Storage": [("MFA", True, 0.65), ("Patch Management", False, 0.2), ("EDR", False, 0.15),
                       ("Network Segmentation", False, 0.2), ("Backup", True, 0.6), ("Monitoring", False, 0.25)],
    "HR System": [("MFA", True, 0.7), ("Patch Management", True, 0.65), ("EDR", True, 0.6),
                   ("Network Segmentation", True, 0.6), ("Backup", True, 0.65), ("Monitoring", True, 0.55)],
    "Backup Server": [("MFA", False, 0.15), ("Patch Management", False, 0.25), ("EDR", False, 0.2),
                       ("Network Segmentation", True, 0.55), ("Backup", True, 0.5), ("Monitoring", False, 0.3)],
    "Production Server": [("MFA", True, 0.65), ("Patch Management", False, 0.2), ("EDR", True, 0.6),
                            ("Network Segmentation", False, 0.15), ("Backup", True, 0.6), ("Monitoring", True, 0.5)],
    "API Gateway": [("MFA", True, 0.6), ("Patch Management", False, 0.25), ("EDR", False, 0.2),
                     ("Network Segmentation", True, 0.55), ("Backup", True, 0.6), ("Monitoring", True, 0.5)],
}

INVESTMENTS = [
    dict(action_key="mfa", name="Enable MFA", description="Multi-factor authentication for privileged & remote access accounts",
         cost=20_00_000, risk_reduction_factor=0.12),
    dict(action_key="patch_management", name="Patch Critical Vulnerabilities", description="Accelerated patch management program for critical/high CVEs",
         cost=15_00_000, risk_reduction_factor=0.10),
    dict(action_key="edr", name="Deploy EDR", description="Endpoint Detection & Response across servers and endpoints",
         cost=20_00_000, risk_reduction_factor=0.15),
    dict(action_key="network_segmentation", name="Network Segmentation", description="Segment critical systems into isolated network zones",
         cost=35_00_000, risk_reduction_factor=0.18),
    dict(action_key="backup", name="Improve Backup", description="Immutable, frequently-tested backup & recovery capability",
         cost=12_00_000, risk_reduction_factor=0.08),
    dict(action_key="monitoring", name="Increase Monitoring", description="Expanded SIEM/log coverage and alerting",
         cost=18_00_000, risk_reduction_factor=0.10),
]

COMPLIANCE = [
    dict(finding="Privileged accounts without MFA", status="Gap",
         frameworks="NIST CSF,ISO/IEC 27001,CIS Controls",
         recommended_action="Enable MFA for all privileged and remote-access accounts"),
    dict(finding="Unpatched critical vulnerabilities on internet-facing systems", status="Gap",
         frameworks="NIST CSF,ISO/IEC 27001,CIS Controls,RBI Cyber Security Framework",
         recommended_action="Implement risk-based patch management SLAs"),
    dict(finding="Flat network without segmentation between core banking and corporate IT", status="Gap",
         frameworks="NIST CSF,ISO/IEC 27001,RBI Cyber Security Framework",
         recommended_action="Segment core banking systems from general corporate network"),
    dict(finding="Insufficient security monitoring / SOC coverage", status="Partial",
         frameworks="NIST CSF,CIS Controls,SEBI Cybersecurity and Cyber Resilience Framework",
         recommended_action="Expand SIEM coverage and 24x7 monitoring"),
    dict(finding="Backup and recovery procedures not regularly tested", status="Partial",
         frameworks="ISO/IEC 27001,RBI Cyber Security Framework,SEBI Cybersecurity and Cyber Resilience Framework",
         recommended_action="Institute quarterly backup restoration drills"),
    dict(finding="Data classification and encryption at rest inconsistently applied", status="Gap",
         frameworks="ISO/IEC 27001,SEBI Cybersecurity and Cyber Resilience Framework",
         recommended_action="Enforce encryption-at-rest policy for sensitive data stores"),
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Reset all tables for a clean, deterministic demo state
        db.query(models.SimulationResult).delete()
        db.query(models.Recommendation).delete()
        db.query(models.RiskAssessment).delete()
        db.query(models.SecurityControl).delete()
        db.query(models.Incident).delete()
        db.query(models.Vulnerability).delete()
        db.query(models.Asset).delete()
        db.query(models.Investment).delete()
        db.query(models.ComplianceControl).delete()
        db.commit()

        name_to_asset = {}
        for a in ASSETS:
            asset = models.Asset(**a)
            db.add(asset)
            db.flush()
            name_to_asset[a["name"]] = asset

        for name, vulns in VULNS.items():
            asset = name_to_asset[name]
            for cve, sev, score, desc, patched in vulns:
                db.add(models.Vulnerability(
                    asset_id=asset.id, cve_like_id=cve, severity=sev,
                    cvss_score=score, description=desc, patched=int(patched),
                ))
        db.flush()

        for name, incs in INCIDENTS.items():
            asset = name_to_asset[name]
            for i, (itype, sev, loss) in enumerate(incs):
                db.add(models.Incident(
                    asset_id=asset.id, incident_type=itype,
                    occurred_at=datetime.utcnow() - timedelta(days=30 * (i + 1)),
                    severity=sev, financial_loss=loss,
                ))

        for name, controls in CONTROLS.items():
            asset = name_to_asset[name]
            for cname, implemented, eff in controls:
                db.add(models.SecurityControl(
                    asset_id=asset.id, control_name=cname,
                    implemented=int(implemented), effectiveness=eff,
                ))

        for inv in INVESTMENTS:
            db.add(models.Investment(**inv))

        for c in COMPLIANCE:
            db.add(models.ComplianceControl(**c))

        db.commit()

        risk_engine.recalculate_all(db)
        recommendation_engine.regenerate_all_recommendations(db)
        print(f"Seeded {len(ASSETS)} assets, {len(INVESTMENTS)} investments, {len(COMPLIANCE)} compliance findings.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
