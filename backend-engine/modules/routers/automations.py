# app/routers/automations.py
from fastapi import APIRouter, HTTPException
from modules.core.runner import run_automation
from modules.core.job_manager import job_manager, Job
from modules.crud.account import get_account_by_id
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/automations", tags=["Automations"])

class AutomationRequest(BaseModel):
    account_ids: List[str]
    automation_id: str
    parameters: dict = {}


def execute_job(job: Job):
    """
    Job execution callback - called by job_manager when a job starts.
    This runs in a background thread.
    """
    params = job.execution_params
    
    try:
        result = run_automation(
            email=params["email"],
            password=params["password"],
            isp=params["isp"],
            automation_name=params["automation_name"],
            proxy_config=params.get("proxy_config"),
            device_type=params.get("device_type", "desktop"),
            **params.get("extra_params", {})
        )
        job_manager.complete_job(job.id, success=True)
        return result
    except Exception as e:
        job_manager.complete_job(job.id, success=False, error=str(e))
        raise


# Register the job runner on module load
job_manager.set_job_runner(execute_job)


@router.post("/run")
def trigger_automation(request: AutomationRequest):
    try:
        queued_jobs = []
        skipped_accounts = []
        failed_accounts = []

        for account_id in request.account_ids:
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
