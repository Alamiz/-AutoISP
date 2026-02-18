"""
Service layer — business logic for upserts, job creation, etc.
All functions receive a SQLAlchemy Session and operate within it.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session, joinedload

from API.models import Account, Job, JobAccount, JobAutomation, Proxy


# ═══════════════════════════════════════════════════════════════════════════
# Accounts
# ═══════════════════════════════════════════════════════════════════════════

def upsert_accounts(
    db: Session,
    accounts_data: List[Dict[str, Any]],
) -> Dict[str, List[int]]:
    """
    Upsert a list of accounts by (email, provider).
    Returns {"created_ids": [...], "existing_ids": [...]}.
    """
    created_ids: List[int] = []
    existing_ids: List[int] = []

    for data in accounts_data:
        existing = (
            db.query(Account)
            .filter(Account.email == data["email"], Account.provider == data["provider"])
            .first()
        )

        if existing:
            # Update mutable fields if provided
            if data.get("password"):
                existing.password = data["password"]
            if "recovery_email" in data and data["recovery_email"] is not None:
                existing.recovery_email = data["recovery_email"]
            if "phone_number" in data and data["phone_number"] is not None:
                existing.phone_number = data["phone_number"]
            if "status" in data and data["status"] is not None:
                existing.status = data["status"]
            existing_ids.append(existing.id)
        else:
            account = Account(
                email=data["email"],
                password=data["password"],
                recovery_email=data.get("recovery_email"),
                phone_number=data.get("phone_number"),
                provider=data["provider"],
                status=data.get("status", "unknown"),
            )
            db.add(account)
            db.flush()  # get the id
            created_ids.append(account.id)

    return {"created_ids": created_ids, "existing_ids": existing_ids}


# ═══════════════════════════════════════════════════════════════════════════
# Proxies
# ═══════════════════════════════════════════════════════════════════════════

def upsert_proxies(
    db: Session,
    proxies_data: List[Dict[str, Any]],
) -> Dict[str, List[int]]:
    """
    Upsert a list of proxies by (ip, port).
    Returns {"created_ids": [...], "existing_ids": [...]}.
    """
    created_ids: List[int] = []
    existing_ids: List[int] = []

    for data in proxies_data:
        existing = (
            db.query(Proxy)
            .filter(Proxy.ip == data["ip"], Proxy.port == data["port"])
            .first()
        )

        if existing:
            if "username" in data and data["username"] is not None:
                existing.username = data["username"]
            if "password" in data and data["password"] is not None:
                existing.password = data["password"]
            existing_ids.append(existing.id)
        else:
            proxy = Proxy(
                ip=data["ip"],
                port=data["port"],
                username=data.get("username"),
                password=data.get("password"),
            )
            db.add(proxy)
            db.flush()
            created_ids.append(proxy.id)

    return {"created_ids": created_ids, "existing_ids": existing_ids}


# ═══════════════════════════════════════════════════════════════════════════
# Jobs
# ═══════════════════════════════════════════════════════════════════════════

def create_job_run(
    db: Session,
    *,
    name: Optional[str],
    provider: str,
    max_concurrent: int,
    accounts_data: Optional[List[Dict[str, Any]]] = None,
    account_ids: Optional[List[int]] = None,
    proxy_ids: List[int],
    automations_data: List[Dict[str, Any]],
) -> Job:
    """
    Full job creation:
    1. Upsert accounts
    2. Create Job
    3. Create JobAccount rows (round-robin proxy assignment)
    4. Create JobAutomation rows
    """
    # 1 — Collect all Account IDs
    all_account_ids = []
    if accounts_data:
        upsert_result = upsert_accounts(db, accounts_data)
        all_account_ids.extend(upsert_result["created_ids"] + upsert_result["existing_ids"])

    if account_ids:
        # Filter out duplicates
        for aid in account_ids:
            if aid not in all_account_ids:
                all_account_ids.append(aid)

    if not all_account_ids:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="No accounts selected for this job")

    # 2 — Create the Job
    job = Job(name=name, provider=provider, max_concurrent=max_concurrent, status="queued")
    db.add(job)
    db.flush()

    # 3 — Validate proxy IDs exist
    valid_proxy_ids: List[int] = []
    if proxy_ids:
        valid_proxies = db.query(Proxy.id).filter(Proxy.id.in_(proxy_ids)).all()
        valid_proxy_ids = [p.id for p in valid_proxies]

    # 4 — Create JobAccount rows with round-robin proxy assignment
    for idx, account_id in enumerate(all_account_ids):
        proxy_id = None
        if valid_proxy_ids:
            proxy_id = valid_proxy_ids[idx % len(valid_proxy_ids)]

        job_account = JobAccount(
            job_id=job.id,
            account_id=account_id,
            proxy_id=proxy_id,
            status="queued",
        )
        db.add(job_account)

    # 5 — Create JobAutomation rows
    for auto_data in automations_data:
        settings = auto_data.get("settings")
        job_automation = JobAutomation(
            job_id=job.id,
            automation_name=auto_data["automation_name"],
            run_order=auto_data.get("run_order", 0),
            settings_json=json.dumps(settings) if settings else None,
            enabled=auto_data.get("enabled", True),
        )
        db.add(job_automation)

    db.flush()
    return job


def get_job_summary(db: Session, job_id: int) -> Optional[Dict[str, Any]]:
    """
    Returns job + aggregated counts, or None if not found.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return None

    job_accounts = (
        db.query(JobAccount)
        .options(joinedload(JobAccount.account))
        .filter(JobAccount.job_id == job_id)
        .all()
    )

    # Populate account_email for schema serialization
    for ja in job_accounts:
        ja.account_email = ja.account.email if ja.account else None
    automations = (
        db.query(JobAutomation).filter(JobAutomation.job_id == job_id).all()
    )

    # Count distinct proxies actually assigned
    proxy_ids_used = {ja.proxy_id for ja in job_accounts if ja.proxy_id is not None}

    return {
        "job": job,
        "accounts_count": len(job_accounts),
        "proxies_count": len(proxy_ids_used),
        "automations": automations,
        "job_accounts": job_accounts,
    }
