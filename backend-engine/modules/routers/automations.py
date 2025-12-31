# app/routers/automations.py
from datetime import datetime
from fastapi import APIRouter, HTTPException
from modules.core.runner import run_automation
from modules.core.job_manager import job_manager, Job
from modules.crud.account import get_account_by_id, get_account_ids, get_accounts_by_ids
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
    
    # Default values for completion
    is_success = False
    error_msg = None
    
    try:
        result = run_automation(
            account_id=params["account_id"],
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
        
        status = result.get("status", "success")
        is_success = status == "success"
        message = result.get("message", "")
        
        print(f"🏁 Job {job.id} execution finished. Status: {status}, Message: {message}")
        
        # Log activity
        try:
            ActivityManager.create_activity(
                action="run_automation",
                status=status,
                account_id=job.account_id,
                details=message,
                metadata={
                    "automation_id": job.automation_id, 
                    "device_type": params.get("device_type", "desktop"),
                    "status": status,
                    "message": message
                },
                executed_at=executed_at,
                completed_at=completed_at
            )
        except Exception as e:
            print(f"❌ Failed to log activity: {e}")
        
        return result
        
    except Exception as e:
        # Record completion time
        completed_at = datetime.utcnow().isoformat()
        error_msg = str(e)
        is_success = False
        
        print(f"❌ Job {job.id} execution failed: {error_msg}")
        
        # Log failure activity
        try:
            ActivityManager.create_activity(
                action="run_automation",
                status="failed",
                account_id=job.account_id,
                details=f"Automation '{job.automation_name}' failed: {error_msg}",
                metadata={"automation_id": job.automation_id, "error": error_msg, "device_type": params.get("device_type", "desktop")},
                executed_at=executed_at,
                completed_at=completed_at
            )
        except Exception as e:
            print(f"❌ Failed to log failure activity: {e}")
            
        raise
        
    finally:
        # ALWAYS complete the job
        print(f"🧹 Completing job {job.id} (Success: {is_success})")
        job_manager.complete_job(job.id, success=is_success, error=error_msg)


# Register the job runner on module load
job_manager.set_job_runner(execute_job)


@router.post("/run")
def trigger_automation(request: AutomationRequest):
    try:
        queued_jobs = []
        skipped_accounts = []
        failed_accounts = []

        # Fetch all accounts in a single batch request to the master API
        accounts = get_accounts_by_ids(
            select_all=request.select_all,
            excluded_ids=request.excluded_ids,
            account_ids=request.account_ids,
            provider=request.provider
        )

        for account in accounts:
            account_id = account.get("id")
            
            if not account_id:
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
                    "account_id": account_id,
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


@router.post("/run-sequential")
def run_sequential_automation(request: AutomationRequest):
    """
    Run automations sequentially in a simple loop.
    No queue, no multithreading - just one after another.
    Handles select_all/excluded_ids logic like /run endpoint.
    """
    try:
        results = []
        failed_accounts = []

        # Determine which account IDs to process (same logic as /run)
        if request.select_all and request.provider:
            all_ids = get_account_ids(provider=request.provider)
            excluded_set = set(request.excluded_ids or [])
            account_ids = [id for id in all_ids if id not in excluded_set]
        else:
            account_ids = request.account_ids or []

        for account_id in account_ids:
            account = get_account_by_id(account_id)

            if not account:
                failed_accounts.append(
                    {"account_id": account_id, "reason": "Account not found"}
                )
                continue

            # Extract password from credentials
            password = None
            credentials = account.get("credentials", {})
            if credentials and "password" in credentials:
                password = credentials["password"]

            if not password:
                failed_accounts.append(
                    {"account_id": account_id, "reason": "Password missing in account credentials"}
                )
                continue

            # Record start time
            executed_at = datetime.utcnow().isoformat()

            try:
                # Run automation directly (synchronously)
                result = run_automation(
                    account_id=account_id,
                    email=account.get("email"),
                    password=password,
                    isp=account.get("provider"),
                    automation_name=request.automation_id,
                    proxy_config=account.get("proxy_settings"),
                    device_type=account.get("type", "desktop"),
                    **request.parameters
                )

                completed_at = datetime.utcnow().isoformat()

                # Log success activity
                ActivityManager.create_activity(
                    action="run_automation",
                    status=result.get("status", "success"),
                    account_id=account_id,
                    details=result.get("message", ""),
                    metadata={
                        "automation_id": request.automation_id,
                        "device_type": account.get("type", "desktop"),
                        "status": result.get("status", "success"),
                        "message": result.get("message", ""),
                        "mode": "sequential"
                    },
                    executed_at=executed_at,
                    completed_at=completed_at
                )

                results.append({
                    "account_id": account_id,
                    "account_email": account.get("email"),
                    "status": result.get("status", "success"),
                    "message": result.get("message", "")
                })

            except Exception as e:
                completed_at = datetime.utcnow().isoformat()
                error_msg = str(e)

                # Log failure activity
                ActivityManager.create_activity(
                    action="run_automation",
                    status="failed",
                    account_id=account_id,
                    details=f"Automation '{request.automation_id}' failed: {error_msg}",
                    metadata={
                        "automation_id": request.automation_id,
                        "error": error_msg,
                        "device_type": account.get("type", "desktop"),
                        "mode": "sequential"
                    },
                    executed_at=executed_at,
                    completed_at=completed_at
                )

                results.append({
                    "account_id": account_id,
                    "account_email": account.get("email"),
                    "status": "failed",
                    "error": error_msg
                })

        return {
            "status": "completed",
            "automation_id": request.automation_id,
            "parameters": request.parameters,
            "results": results,
            "failed_accounts": failed_accounts,
            "total_processed": len(results),
            "total_failed": len(failed_accounts)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

