import httpx
from fastapi.exceptions import HTTPException
import logging
from modules.core.token_storage import token_storage
from modules.core.config import MASTER_API_URL

logger = logging.getLogger(__name__)

# Configuration for the external API
EXTERNAL_BACKUP_API_BASE_URL = f"{MASTER_API_URL}/api/backups"

class BackupManager:
    @staticmethod
    async def upload_backup(filename: str, file_size: int, account_id: str, file_path: str):
        """
        Uploads a backup zip file to the Master API.
        """
        token = token_storage.get_token()
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        try:
            async with httpx.AsyncClient() as client:
                with open(file_path, "rb") as f:
                    files = {"backup_data": (filename, f, "application/zip")}
                    data = {
                        "filename": filename,
                        "file_size": file_size,
                        "account": account_id
                    }
                    
                    response = await client.post(
                        f"{EXTERNAL_BACKUP_API_BASE_URL}/upload/",
                        data=data,
                        files=files,
                        headers=headers,
                        timeout=300.0 # Large timeout for uploads
                    )
                    response.raise_for_status()
                    return response.json()
        except httpx.RequestError as exc:
            logger.error(f"An error occurred while uploading backup: {exc}")
            raise HTTPException(status_code=500, detail="Could not connect to external backup service")
        except httpx.HTTPStatusError as exc:
            logger.error(f"External backup service returned error: {exc.response.status_code} - {exc.response.text}")
            raise HTTPException(status_code=exc.response.status_code, detail=f"External backup service error: {exc.response.text}")

    @staticmethod
    async def download_backup(backup_id: str, destination_path: str):
        """
        Downloads a backup zip file from the Master API.
        """
        token = token_storage.get_token()
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        download_url = f"{EXTERNAL_BACKUP_API_BASE_URL}/{backup_id}/download/"

        try:
            async with httpx.AsyncClient() as client:
                async with client.stream("GET", download_url, headers=headers, timeout=300.0) as response:
                    response.raise_for_status()
                    with open(destination_path, "wb") as f:
                        async for chunk in response.aiter_bytes():
                            f.write(chunk)
        except httpx.RequestError as exc:
            logger.error(f"An error occurred while downloading backup: {exc}")
            raise HTTPException(status_code=500, detail="Could not connect to external backup service")
        except httpx.HTTPStatusError as exc:
            logger.error(f"External backup service returned error: {exc.response.status_code} - {exc.response.text}")
            raise HTTPException(status_code=exc.response.status_code, detail=f"External backup service error: {exc.response.text}")
