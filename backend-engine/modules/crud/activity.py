import httpx
from fastapi.exceptions import HTTPException
import logging
from datetime import datetime
from modules.core.token_storage import token_storage

logger = logging.getLogger(__name__)

# Configuration for the external API
EXTERNAL_ACTIVITY_API_BASE_URL = "http://localhost:8000/api/activity"

class ActivityManager:
    @staticmethod
    def create_activity(
        action: str,
        status: str,
        account_id: str,
        details: str = "",
        metadata: str = "",
        executed_at: str = None,
        completed_at: str = None
    ):
        """
        Logs an activity to the Master API.
        """
        if not executed_at:
            executed_at = datetime.utcnow().isoformat()
        if not completed_at:
            completed_at = datetime.utcnow().isoformat()

        payload = {
            "action": action,
            "details": details,
            "status": status,
            "executed_at": executed_at,
            "completed_at": completed_at,
            "metadata": metadata,
            "account": account_id,
        }

        token = token_storage.get_token()
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        try:
            with httpx.Client() as client:
                response = client.post(EXTERNAL_ACTIVITY_API_BASE_URL + "/", json=payload, headers=headers)
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as exc:
            logger.error(f"An error occurred while logging activity: {exc}")
            # We don't raise here to avoid failing the main process just because logging failed
            # But maybe we should? For now, just log the error.
        except httpx.HTTPStatusError as exc:
            logger.error(f"External activity service returned error: {exc.response.status_code} - {exc.response.text}")
