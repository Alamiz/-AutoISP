# app/routers/automations.py
from datetime import datetime
from fastapi import APIRouter, HTTPException
from modules.core.runner import run_automation
from modules.core.job_manager import job_manager, Job
from modules.crud.account import get_account_by_id, get_account_ids
from modules.crud.activity import ActivityManager
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/automations", tags=["Automations"])

class AutomationRequest(BaseModel):
    account_ids: Optional[List[str]] = None  # Used for manual selection
    automation_id: str
    parameters: dict = {}
    # Select-all mode fields
    select_all: Optional[bool] = False
    provider: Optional[str] = None
    excluded_ids: Optional[List[str]] = []


def execute_job(job: Job):
    """
    Job execution callback - called by job_manager when a job starts.
    This runs in a background thread.
    Logs activity on completion (success or failure).
    """
    params = job.execution_params
    
    # Record start time
    executed_at = datetime.utcnow().isoformat()
    
    try:
        result = run_automation(
            email=params["email"],
            password=params["password"],
            isp=params["isp"],
            automation_name=params["automation_name"],
            proxy_config=params.get("proxy_config"),
            device_type=params.get("device_type", "desktop"),
            job_id=job.id,  # Pass job_id for browser registration
            **params.get("extra_params", {})
        )
        
        # Record completion time
        completed_at = datetime.utcnow().isoformat()
        
        # Log success activity
        ActivityManager.create_activity(
            action="run_automation",
            status=result.get("status", "success"),
            account_id=job.account_id,
            details=result.get("message", ""),
            metadata={
                "automation_id": job.automation_id, 
                "device_type": params.get("device_type", "desktop"),
                "status": result.get("status", "success"),
                "message": result.get("message", "")
            },
            executed_at=executed_at,
            completed_at=completed_at
        )
        
        job_manager.complete_job(job.id, success=True)
        return result
        
    except Exception as e:
        # Record completion time
        completed_at = datetime.utcnow().isoformat()
        error_msg = str(e)
        
        # Log failure activity
        ActivityManager.create_activity(
            action="run_automation",
            status="failed",
            account_id=job.account_id,
            details=f"Automation '{job.automation_name}' failed: {error_msg}",
            metadata={"automation_id": job.automation_id, "error": error_msg, "device_type": params.get("device_type", "desktop")},
            executed_at=executed_at,
            completed_at=completed_at
        )
        
        job_manager.complete_job(job.id, success=False, error=error_msg)
        raise


# Register the job runner on module load
job_manager.set_job_runner(execute_job)


@router.post("/run")
def trigger_automation(request: AutomationRequest):
    try:
        queued_jobs = []
        skipped_accounts = []
        failed_accounts = []

        # Determine which account IDs to process
        if request.select_all and request.provider:
            # Select-all mode: fetch all account IDs for provider using lightweight endpoint
            all_ids = get_account_ids(provider=request.provider)
            
            # Exclude specified IDs
            excluded_set = set(request.excluded_ids or [])
            account_ids = [id for id in all_ids if id not in excluded_set]
        else:
            # Manual selection mode
            account_ids = request.account_ids or []

        for account_id in account_ids:
            # Account IDs are UUID strings; force string to ensure compatibility
            account = get_account_by_id(account_id)

            if not account:
                failed_accounts.append(
                    {"account_id": account_id, "reason": "Account not found"}
                )
                continue

            # Check if account is already busy
            if job_manager.is_account_busy(account_id):
                skipped_accounts.append(
                    {"account_id": account_id, "reason": "Account already has a running or queued job"}
                )
                continue

            # Extract correct password from credentials
            password = None
            credentials = account.get("credentials", {})
            if credentials and "password" in credentials:
                password = credentials["password"]

            if not password:
                failed_accounts.append(
                    {"account_id": account_id, "reason": "Password missing in account credentials"}
                )
                continue

            # Queue the job with execution params
            job = job_manager.queue_job(
                account_id=account_id,
                account_email=account.get("email"),
                automation_id=request.automation_id,
                automation_name=request.automation_id,
                execution_params={
                    "email": account.get("email"),
                    "password": password,
                    "isp": account.get("provider"),
                    "automation_name": request.automation_id,
                    "proxy_config": account.get("proxy_settings"),
                    "device_type": account.get("type", "desktop"),
                    "extra_params": request.parameters,
                }
            )

            if not job:
                skipped_accounts.append(
                    {"account_id": account_id, "reason": "Failed to create job"}
                )
                continue

            queued_jobs.append({"job_id": job.id, "account_email": job.account_email})

        return {
            "status": "queued",
            "automation_id": request.automation_id,
            "parameters": request.parameters,
            "queued_jobs": queued_jobs,
            "skipped_accounts": skipped_accounts,
            "failed_accounts": failed_accounts,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
