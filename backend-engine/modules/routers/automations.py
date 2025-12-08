# app/routers/automations.py
from fastapi import APIRouter, BackgroundTasks, HTTPException
from modules.core.runner import run_automation
from modules.crud.account import get_account_by_id
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/automations", tags=["Automations"])

class AutomationRequest(BaseModel):
    account_ids: List[str]
    automation_id: str
    parameters: dict = {}


@router.post("/run")
def trigger_automation(request: AutomationRequest, background_tasks: BackgroundTasks):
    try:
        failed_accounts = []

        for account_id in request.account_ids:
            # Account IDs are UUID strings; force string to ensure compatibility
            account = get_account_by_id(account_id)

            if not account:
                failed_accounts.append(
                    {account_id: f"Account with id {account_id} not found"}
                )
                continue

            # Extract correct password from credentials
            password = None
            credentials = account.get("credentials", {})
            if credentials and "password" in credentials:
                password = credentials["password"]

            if not password:
                failed_accounts.append(
                    {account_id: f"Password missing in account credentials"}
                )
                continue

            # Schedule automation with correct arguments
            background_tasks.add_task(
                run_automation,
                email=account.get("email"),
                password=password,
                isp=account.get("provider"),
                automation_name=request.automation_id,
                proxy_config=account.get("proxy_settings"),
                device_type=account.get("type", "desktop"),
                **request.parameters
            )

        return {
            "status": "queued",
            "automation_id": request.automation_id,
            "parameters": request.parameters,
            "accounts": request.account_ids,
            "failed_accounts": failed_accounts,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
