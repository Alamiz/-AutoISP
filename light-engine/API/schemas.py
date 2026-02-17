"""
Pydantic schemas for request / response validation.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, field_validator

T = TypeVar("T")


# ═══════════════════════════════════════════════════════════════════════════
# Pagination
# ═══════════════════════════════════════════════════════════════════════════
class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int


# ═══════════════════════════════════════════════════════════════════════════
# Account
# ═══════════════════════════════════════════════════════════════════════════
VALID_PROVIDERS = {"gmx", "webde", "outlook", "libero", "cloudAI"}
VALID_ACCOUNT_STATUSES = {
    "unknown", "active", "inactive", "error", "disabled", "suspended",
    "phone_verification", "captcha", "wrong_password", "wrong_username",
}


class AccountCreate(BaseModel):
    email: str
    password: str
    recovery_email: Optional[str] = None
    phone_number: Optional[str] = None
    provider: str
    status: str = "unknown"

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        if v not in VALID_PROVIDERS:
            raise ValueError(f"provider must be one of {VALID_PROVIDERS}")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in VALID_ACCOUNT_STATUSES:
            raise ValueError(f"status must be one of {VALID_ACCOUNT_STATUSES}")
        return v


class AccountUpdate(BaseModel):
    password: Optional[str] = None
    recovery_email: Optional[str] = None
    phone_number: Optional[str] = None
    status: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_ACCOUNT_STATUSES:
            raise ValueError(f"status must be one of {VALID_ACCOUNT_STATUSES}")
        return v


class AccountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    password: str
    recovery_email: Optional[str] = None
    phone_number: Optional[str] = None
    provider: str
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BulkUpsertAccountResponse(BaseModel):
    created_ids: List[int]
    existing_ids: List[int]


# ═══════════════════════════════════════════════════════════════════════════
# Proxy
# ═══════════════════════════════════════════════════════════════════════════
class ProxyCreate(BaseModel):
    ip: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None


class ProxyUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None


class ProxyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ip: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BulkUpsertProxyResponse(BaseModel):
    created_ids: List[int]
    existing_ids: List[int]


# ═══════════════════════════════════════════════════════════════════════════
# Automation (sub-schema used inside Job)
# ═══════════════════════════════════════════════════════════════════════════
class AutomationInput(BaseModel):
    automation_name: str
    run_order: int = 0
    settings: Optional[dict[str, Any]] = None
    enabled: bool = True


class AutomationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    automation_name: str
    run_order: int
    settings_json: Optional[str] = None
    enabled: bool

    @property
    def settings(self) -> Optional[dict]:
        if self.settings_json:
            return json.loads(self.settings_json)
        return None


# ═══════════════════════════════════════════════════════════════════════════
# Job
# ═══════════════════════════════════════════════════════════════════════════
VALID_JOB_STATUSES = {"queued", "running", "completed", "failed", "stopped"}


class JobRunRequest(BaseModel):
    """Payload for POST /jobs/run — creates everything in one shot."""
    name: Optional[str] = None
    max_concurrent: int = 1
    accounts: Optional[List[AccountCreate]] = None
    account_ids: Optional[List[int]] = None
    proxy_ids: List[int] = []
    automations: List[AutomationInput] = []


class JobAccountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_id: int
    account_email: Optional[str] = None
    proxy_id: Optional[int] = None
    status: str
    error_message: Optional[str] = None


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: Optional[str] = None
    status: str
    max_concurrent: int
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None


class JobSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job: JobOut
    accounts_count: int
    proxies_count: int
    automations: List[AutomationOut]
    job_accounts: List[JobAccountOut]
