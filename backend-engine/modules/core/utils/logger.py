import logging
import requests
import json
from ..token_storage import token_storage
from modules.core.config import MASTER_API_URL

class MasterAPILogHandler(logging.Handler):
    """Custom logging handler that sends logs to the master API."""
    
    def __init__(self, master_url):
        super().__init__()
        self.master_url = master_url.rstrip("/") + "/api/logs/"
        self.setFormatter(logging.Formatter('%(message)s'))

    def emit(self, record):
        log_entry = self.format(record)
        
        # Extract is_global from extra (default to False for global logs)
        is_global = getattr(record, 'is_global', False)
        
        # Extract account_id from extra (optional, for automation logs)
        account_id = getattr(record, 'account_id', None)
        
        payload = {
            "level": record.levelname,
            "message": log_entry,
            "is_global": is_global,
        }
        
        # Only include account_id if provided
        if account_id is not None:
            payload["account"] = account_id

        token = token_storage.get_token()
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        try:
            requests.post(self.master_url, data=json.dumps(payload), headers=headers, timeout=2)
        except Exception as e:
            # Fail silently to avoid recursive logging
            pass

def configure_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Console logs
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    # Master API logs
    master_handler = MasterAPILogHandler(master_url=MASTER_API_URL)
    master_handler.setLevel(logging.INFO)
    logger.addHandler(master_handler)

    return logger
