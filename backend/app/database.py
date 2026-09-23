"""
Database configuration for the SIH26105 prototype.

Uses SQLite + SQLAlchemy ORM. Kept intentionally simple for a hackathon
prototype -- a real deployment would point SQLALCHEMY_DATABASE_URL at a
managed Postgres/MySQL instance via an environment variable.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_PATH = os.environ.get("SIH_DB_PATH", os.path.join(os.path.dirname(__file__), "..", "cyber_risk.db"))
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
