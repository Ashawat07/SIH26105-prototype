DIGISTAT — AI-Powered Cyber Risk Quantification & Investment Optimization

SIH Problem Statement 26105 · AICTE — Cyber Security Cell · Theme: Blockchain & Cybersecurity

DIGISTAT converts technical cybersecurity findings into measurable financial risk and helps security teams decide where a limited security budget can reduce the most risk.

This is a Smart India Hackathon prototype, not a production enterprise risk platform. The current prototype uses seeded/local data and deterministic risk, recommendation, simulation and optimization logic.

What problem this solves

Organizations collect security data from many tools, but cyber risk is often communicated only as Low / Medium / High. This makes it difficult for management to understand the possible financial exposure and decide which security investments should be prioritized.

DIGISTAT connects:

Security Findings → Risk Quantification → Financial Exposure → AI Advisor → What-if Simulation → Investment Optimization

Key Features

Enterprise cyber-risk dashboard

Asset and vulnerability risk analysis

Financial impact estimation

Expected Annual Loss (EAL)

Value at Risk (VaR95)

Risk drivers and trends

AI Security Advisor with prioritized recommendations

Cost vs. risk-reduction analysis

Budget-based security investment optimization

What-if remediation simulation

Compliance/framework view

PDF report generation

Asset-level drill-down

Architecture

React + TypeScript + Vite
        │
        │ REST API
        ▼
FastAPI Backend
        │
        ├── Risk Engine
        ├── Recommendation Engine
        ├── Simulation Engine
        ├── Investment Optimization
        ├── Compliance
        └── Reports
        │
        ▼
SQLAlchemy + Local Database

The backend automatically creates the database tables and seeds demo data when the database is empty.

Tech Stack

Frontend: React 18, TypeScript, Vite, React Router, Recharts, Tailwind CSS

Backend: Python, FastAPI, Pydantic, SQLAlchemy

Reporting: ReportLab

Database: SQLAlchemy-supported local database configured by the project

API: REST

Development: Git / GitHub

Project Structure

sih26105/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── seed.py
│   │   ├── risk_engine.py
│   │   ├── recommendation_engine.py
│   │   ├── simulation_engine.py
│   │   ├── optimization_engine.py
│   │   └── routers/
│   │       ├── dashboard.py
│   │       ├── assets.py
│   │       ├── risks.py
│   │       ├── recommendations.py
│   │       ├── simulation.py
│   │       ├── optimization.py
│   │       ├── compliance.py
│   │       └── reports.py
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── pages/
    │   ├── components/
    │   └── lib/api.ts
    └── package.json

How to Run

1. Start the Backend

Open a terminal:

cd sih26105/backend

Create and activate a virtual environment:

Windows

python -m venv venv
venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Start FastAPI:

uvicorn app.main:app --reload

Backend:

http://127.0.0.1:8000

API documentation:

http://127.0.0.1:8000/docs

Health check:

http://127.0.0.1:8000/api/health

2. Start the Frontend

Open another terminal:

cd sih26105/frontend
npm install
npm run dev

Open the Vite URL shown in the terminal, normally:

http://localhost:5173

Keep the backend running while using the frontend.

Main Demo Flow

For an SIH presentation, the easiest flow is:

Open the Dashboard and show enterprise risk and financial exposure.

Open Assets and select a critical asset.

Show its vulnerabilities, risk score and financial impact.

Open AI Advisor and show recommended security actions with estimated cost and risk reduction.

Open Simulation and run a what-if remediation scenario.

Open Optimization, enter a security budget and generate an investment plan.

Show Compliance and generate a report if required.

How Risk Quantification Works

The prototype combines asset criticality, vulnerabilities and incident information to estimate:

Incident likelihood

Financial impact

Risk score

Expected Annual Loss (EAL)

Value at Risk (VaR95)

ROSI for security investments

The calculations are implemented in:

backend/app/risk_engine.py

The current formulas are a hackathon prototype methodology and should not be treated as an official actuarial or regulatory model.

AI Security Advisor

The advisor converts identified risks into actionable recommendations such as:

Patch critical vulnerabilities

Strengthen access controls

Improve monitoring

Apply security controls to high-impact assets

Recommendations include estimated investment cost and modeled risk reduction.

Implementation:

backend/app/recommendation_engine.py

What-if Simulation

The simulation module allows users to explore scenarios such as applying a security action or delaying remediation.

It compares the modeled risk/financial exposure before and after the selected scenario.

Implementation:

backend/app/simulation_engine.py

Investment Optimization

DIGISTAT accepts a security budget and selects an investment combination intended to maximize modeled risk reduction.

Implementation:

backend/app/optimization_engine.py

The current prototype uses a budget-constrained optimization approach; it is designed for demonstration and can later be replaced or extended with more advanced optimization models.

API Overview

The main API areas are:

GET   /api/health
GET   /api/dashboard
GET   /api/assets
GET   /api/assets/{asset_id}
GET   /api/risks
GET   /api/recommendations
POST  /api/recommendations/regenerate
GET   /api/simulation/actions
POST  /api/simulation
POST  /api/optimization
GET   /api/compliance
POST  /api/reports

Full interactive documentation is available at:

http://127.0.0.1:8000/docs

Why DIGISTAT?

Traditional dashboards answer:

“What security problems do we have?”

DIGISTAT aims to answer:

“How much could those risks cost us, what is driving the exposure, and where should we invest to reduce it?”

Future Scope

Live integrations with SIEM, EDR, IAM, CSPM and vulnerability scanners

ML-based incident likelihood prediction

Organization-specific financial-loss calibration

Advanced portfolio optimization

Expanded NIST / ISO / CIS / RBI / SEBI mappings

Role-based enterprise deployment

Continuous near-real-time risk updates

Production-grade authentication and security controls

Prototype Disclaimer

DIGISTAT is an SIH prototype intended to demonstrate the problem, workflow and decision-support concept. Financial risk figures and recommendations are based on the prototype's defined models and seeded data; they should be calibrated with real organizational data before operational use.

Problem Statement

PS ID: 26105
Title: AI-Powered Continuous Cyber Risk Quantification and Investment Optimization Platform
Organization: All India Council for Technical Education (Cyber Security Cell)
Category: Software
Theme: Blockchain & Cybersecurity
