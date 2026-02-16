"""
Jobs router — create job run, list jobs, get job summary.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from API.database import get_db
from API.models import Job
from API.schemas import (
    JobOut,
    JobRunRequest,
    JobSummary,
    PaginatedResponse,
)
from API.services import create_job_run, get_job_summary
from modules.core.job_manager import job_manager

router = APIRouter(prefix="/jobs", tags=["Jobs"])


# ── Create Job Run ────────────────────────────────────────────────────────
@router.post("/run", response_model=JobOut)
def run_job(payload: JobRunRequest, db: Session = Depends(get_db)):
    job = create_job_run(
        db,
        name=payload.name,
        max_concurrent=payload.max_concurrent,
        accounts_data=[a.model_dump() for a in payload.accounts] if payload.accounts else None,
        account_ids=payload.account_ids,
        proxy_ids=payload.proxy_ids,
        automations_data=[a.model_dump() for a in payload.automations],
    )
    db.commit()
    db.refresh(job)
    
    # Submit job to background manager
    job_manager.submit_job(job.id)
    
    return job


# ── List Jobs ─────────────────────────────────────────────────────────────
@router.get("", response_model=PaginatedResponse[JobOut])
def list_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=10000),
    db: Session = Depends(get_db),
):
    query = db.query(Job)
    total = query.count()
    items = (
        query.order_by(Job.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


# ── Job Summary ───────────────────────────────────────────────────────────
@router.get("/{job_id}/summary", response_model=JobSummary)
def job_summary(job_id: int, db: Session = Depends(get_db)):
    result = get_job_summary(db, job_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return result


# ── Active Jobs (Running/Queued) ──────────────────────────────────────────
@router.get("/active", response_model=List[JobSummary])
def get_active_jobs(db: Session = Depends(get_db)):
    """Returns full summary for all running or queued jobs."""
    active_jobs = db.query(Job).filter(Job.status.in_(["running", "queued"])).all()
    results = []
    for job in active_jobs:
        summary = get_job_summary(db, job.id)
        if summary:
            results.append(summary)
    return results


# ── Delete Job ────────────────────────────────────────────────────────────
@router.delete("/{job_id}", status_code=204)
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # If job is running, we might want to stop it first or prevent deletion.
    # For now, just delete it (cascade rules in models should handle children).
    # If not using database-level cascade, we might need manual cleanup.
    # Assuming models have cascade="all, delete-orphan".
    
    db.delete(job)
    db.commit()
    return None
