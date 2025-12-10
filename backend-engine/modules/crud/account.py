import httpx
from fastapi.exceptions import HTTPException
import logging
from modules.core.token_storage import token_storage
from modules.core.config import MASTER_API_URL

logger = logging.getLogger(__name__)

# Configuration for the external API
EXTERNAL_ACCOUNT_API_BASE_URL = f"{MASTER_API_URL}/api/accounts" 

def _get_headers():
    token = token_storage.get_token()
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

def _fetch_accounts_from_external_api(provider: str = None):
    """Fetches all accounts from the external API, optionally filtered by provider."""
    try:
        with httpx.Client() as client:
            url = EXTERNAL_ACCOUNT_API_BASE_URL + "/"
            if provider:
                url += f"?provider={provider}"
            response = client.get(url, headers=_get_headers())
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.json()
    except httpx.RequestError as exc:
        logger.error(f"An error occurred while requesting external accounts: {exc}")
        raise HTTPException(status_code=500, detail="Could not connect to external account service")
    except httpx.HTTPStatusError as exc:
        logger.error(f"External account service returned error: {exc.response.status_code} - {exc.response.text}")
        raise HTTPException(status_code=exc.response.status_code, detail=f"External account service error: {exc.response.text}")

def _fetch_account_by_id_from_external_api(account_id: str):
    """Fetches a single account by ID from the external API."""
    try:
        with httpx.Client() as client:
            response = client.get(f"{EXTERNAL_ACCOUNT_API_BASE_URL}/{account_id}/", headers=_get_headers())
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as exc:
        logger.error(f"An error occurred while requesting external account {account_id}: {exc}")
        raise HTTPException(status_code=500, detail="Could not connect to external account service")
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Account with ID {account_id} not found in external service")
        logger.error(f"External account service returned error for ID {account_id}: {exc.response.status_code} - {exc.response.text}")
        raise HTTPException(status_code=exc.response.status_code, detail=f"External account service error: {exc.response.text}")

def get_accounts(provider: str = None):
    """
    Retrieves accounts from an external API, optionally filtered by provider.
    """
    return _fetch_accounts_from_external_api(provider)

def get_account_by_id(account_id: str):
    """
    Retrieves a single account by ID from an external API.
    """
    return _fetch_account_by_id_from_external_api(account_id)

def get_account_ids(provider: str = None):
    """
    Retrieves all account IDs from the external API, optionally filtered by provider.
    Uses the lightweight /ids/ endpoint that returns only IDs without pagination.
    """
    try:
        with httpx.Client() as client:
            url = EXTERNAL_ACCOUNT_API_BASE_URL + "/ids/"
            if provider:
                url += f"?provider={provider}"
            response = client.get(url, headers=_get_headers())
            response.raise_for_status()
            return response.json()  # Returns list of IDs
    except httpx.RequestError as exc:
        logger.error(f"An error occurred while requesting account IDs: {exc}")
        raise HTTPException(status_code=500, detail="Could not connect to external account service")
    except httpx.HTTPStatusError as exc:
        logger.error(f"External account service returned error: {exc.response.status_code} - {exc.response.text}")
        raise HTTPException(status_code=exc.response.status_code, detail=f"External account service error: {exc.response.text}")
