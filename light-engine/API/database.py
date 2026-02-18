"""
Database configuration for AutoISP local backend.
SQLAlchemy 2.0 + SQLite.
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Determine the base directory for data (persistent in AppData for frozen apps)
if getattr(sys, 'frozen', False):
    # Running in a bundle (PyInstaller)
    APPDATA = os.getenv('APPDATA')
    BASE_DIR = os.path.join(APPDATA, 'AutoISP')
    os.makedirs(BASE_DIR, exist_ok=True)
else:
    # Running in development
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'autoisp.db')}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Required for SQLite
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def create_tables():
    """Create all tables defined in models."""
    from API import models  # noqa: F401 — ensure models are imported
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency that yields a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
