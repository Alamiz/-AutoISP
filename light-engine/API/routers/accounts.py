"""
Accounts router — CRUD + bulk upsert.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from API.database import get_db
from API.models import Account
from API.schemas import (
    AccountCreate,
    AccountOut,
    AccountUpdate,
    BulkUpsertAccountResponse,
    PaginatedResponse,
)
from API.services import upsert_accounts

router = APIRouter(prefix="/accounts", tags=["Accounts"])


# ── Bulk Upsert ───────────────────────────────────────────────────────────
@router.post("/bulk-upsert", response_model=BulkUpsertAccountResponse)
def bulk_upsert(accounts: list[AccountCreate], db: Session = Depends(get_db)):
    data = [a.model_dump() for a in accounts]
    result = upsert_accounts(db, data)
    db.commit()
    return result


# ── List (paginated + filters) ────────────────────────────────────────────
@router.get("", response_model=PaginatedResponse[AccountOut])
def list_accounts(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    provider: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Account)

    if provider:
        query = query.filter(Account.provider == provider)
    if status:
        query = query.filter(Account.status == status)
    if search:
        query = query.filter(Account.email.ilike(f"%{search}%"))

    total = query.count()
    items = (
        query.order_by(Account.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


# ── Get by ID ─────────────────────────────────────────────────────────────
@router.get("/{account_id}", response_model=AccountOut)
def get_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


# ── Patch ─────────────────────────────────────────────────────────────────
@router.patch("/{account_id}", response_model=AccountOut)
def patch_account(
    account_id: int, updates: AccountUpdate, db: Session = Depends(get_db)
):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(account, key, value)

    db.commit()
    db.refresh(account)
    return account


# ── Delete ────────────────────────────────────────────────────────────────
@router.delete("/{account_id}", status_code=204)
def delete_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    db.delete(account)
    db.commit()
