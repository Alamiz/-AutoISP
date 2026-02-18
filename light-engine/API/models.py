"""
SQLAlchemy ORM models for AutoISP.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Boolean, Text, DateTime,
    ForeignKey, UniqueConstraint,
)
from sqlalchemy.orm import relationship
from API.database import Base


def _utcnow():
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Account
# ---------------------------------------------------------------------------
class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    recovery_email = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    provider = Column(String, nullable=False)  # gmx, webde, outlook, libero, cloudAI
    status = Column(String, nullable=False, default="unknown")
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    __table_args__ = (
        UniqueConstraint("email", "provider", name="uq_account_email_provider"),
    )

    # Reverse relationship
    job_accounts = relationship("JobAccount", back_populates="account")


# ---------------------------------------------------------------------------
# Proxy
# ---------------------------------------------------------------------------
class Proxy(Base):
    __tablename__ = "proxies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ip = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    username = Column(String, nullable=True)
    password = Column(String, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    __table_args__ = (
        UniqueConstraint("ip", "port", name="uq_proxy_ip_port"),
    )

    job_accounts = relationship("JobAccount", back_populates="proxy")


# ---------------------------------------------------------------------------
# Job
# ---------------------------------------------------------------------------
class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    provider = Column(String, nullable=False, default="unknown")
    status = Column(String, nullable=False, default="queued")
    max_concurrent = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, default=_utcnow)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)

    # Relationships
    job_accounts = relationship(
        "JobAccount", back_populates="job", cascade="all, delete-orphan"
    )
    job_automations = relationship(
        "JobAutomation", back_populates="job", cascade="all, delete-orphan"
    )


# ---------------------------------------------------------------------------
# JobAccount  (per-account run record inside a Job)
# ---------------------------------------------------------------------------
class JobAccount(Base):
    __tablename__ = "job_accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    account_id = Column(
        Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False
    )
    proxy_id = Column(
        Integer, ForeignKey("proxies.id", ondelete="SET NULL"), nullable=True
    )
    status = Column(String, nullable=False, default="queued")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    # Relationships
    job = relationship("Job", back_populates="job_accounts")
    account = relationship("Account", back_populates="job_accounts")
    proxy = relationship("Proxy", back_populates="job_accounts")


# ---------------------------------------------------------------------------
# JobAutomation
# ---------------------------------------------------------------------------
class JobAutomation(Base):
    __tablename__ = "job_automations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    automation_name = Column(String, nullable=False)
    run_order = Column(Integer, nullable=False, default=0)
    settings_json = Column(Text, nullable=True)  # JSON-serialized config
    enabled = Column(Boolean, nullable=False, default=True)

    # Relationships
    job = relationship("Job", back_populates="job_automations")
