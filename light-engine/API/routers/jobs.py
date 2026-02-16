"""
Jobs router — create job run, list jobs, get job summary.
"""

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

router = APIRouter(prefix="/jobs", tags=["Jobs"])


# ── Create Job Run ────────────────────────────────────────────────────────
@router.post("/run", response_model=JobOut)
def run_job(payload: JobRunRequest, db: Session = Depends(get_db)):
    job = create_job_run(
        db,
        name=payload.name,
        max_concurrent=payload.max_concurrent,
        accounts_data=[a.model_dump() for a in payload.accounts],
        proxy_ids=payload.proxy_ids,
        automations_data=[a.model_dump() for a in payload.automations],
    )
    db.commit()
    db.refresh(job)
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
