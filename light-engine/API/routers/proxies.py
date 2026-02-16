"""
Proxies router — CRUD + bulk upsert.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from API.database import get_db
from API.models import Proxy
from API.schemas import (
    BulkUpsertProxyResponse,
    PaginatedResponse,
    ProxyCreate,
    ProxyOut,
    ProxyUpdate,
)
from API.services import upsert_proxies

router = APIRouter(prefix="/proxies", tags=["Proxies"])


# ── Bulk Upsert ───────────────────────────────────────────────────────────
@router.post("/bulk-upsert", response_model=BulkUpsertProxyResponse)
def bulk_upsert(proxies: list[ProxyCreate], db: Session = Depends(get_db)):
    data = [p.model_dump() for p in proxies]
    result = upsert_proxies(db, data)
    db.commit()
    return result


# ── List (paginated) ──────────────────────────────────────────────────────
@router.get("", response_model=PaginatedResponse[ProxyOut])
def list_proxies(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(Proxy)
    total = query.count()
    items = (
        query.order_by(Proxy.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


# ── Get by ID ─────────────────────────────────────────────────────────────
@router.get("/{proxy_id}", response_model=ProxyOut)
def get_proxy(proxy_id: int, db: Session = Depends(get_db)):
    proxy = db.query(Proxy).filter(Proxy.id == proxy_id).first()
    if not proxy:
        raise HTTPException(status_code=404, detail="Proxy not found")
    return proxy


# ── Patch ─────────────────────────────────────────────────────────────────
@router.patch("/{proxy_id}", response_model=ProxyOut)
def patch_proxy(proxy_id: int, updates: ProxyUpdate, db: Session = Depends(get_db)):
    proxy = db.query(Proxy).filter(Proxy.id == proxy_id).first()
    if not proxy:
        raise HTTPException(status_code=404, detail="Proxy not found")

    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(proxy, key, value)

    db.commit()
    db.refresh(proxy)
    return proxy


# ── Bulk Delete ─────────────────────────────────────────────────────────────
@router.delete("/bulk", status_code=204)
def bulk_delete_proxies(ids: list[int], db: Session = Depends(get_db)):
    db.query(Proxy).filter(Proxy.id.in_(ids)).delete(synchronize_session=False)
    db.commit()


# ── Delete ────────────────────────────────────────────────────────────────
@router.delete("/{proxy_id}", status_code=204)
def delete_proxy(proxy_id: int, db: Session = Depends(get_db)):
    proxy = db.query(Proxy).filter(Proxy.id == proxy_id).first()
    if not proxy:
        raise HTTPException(status_code=404, detail="Proxy not found")
    db.delete(proxy)
    db.commit()
