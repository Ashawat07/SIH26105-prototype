import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import dashboard, assets, risks, recommendations, simulation, optimization, compliance, reports
from .seed import seed

app = FastAPI(
    title="SIH26105 - Cyber Risk Quantification & Investment Optimization Platform (Prototype)",
    description=(
        "Prototype backend for Smart India Hackathon problem statement SIH26105. "
        "Demonstrates converting cybersecurity risk into quantified financial risk "
        "(EAL / VaR) and optimizing security investment under budget constraints."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router)
app.include_router(assets.router)
app.include_router(risks.router)
app.include_router(recommendations.router)
app.include_router(simulation.router)
app.include_router(optimization.router)
app.include_router(compliance.router)
app.include_router(reports.router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    # Auto-seed if the database is empty, so the demo works immediately
    from .database import SessionLocal
    from . import models
    db = SessionLocal()
    try:
        if db.query(models.Asset).count() == 0:
            seed()
    finally:
        db.close()


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "sih26105-cyber-risk-platform"}


@app.get("/")
def root():
    return {
        "message": "SIH26105 Cyber Risk Quantification & Investment Optimization Platform API",
        "docs": "/docs",
    }
