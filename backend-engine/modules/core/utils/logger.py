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
        payload = {
            "level": record.levelname,
            "message": log_entry,
        }

        token = token_storage.get_token()
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        try:
            print("Inserting log: ", payload)
            requests.post(self.master_url, data=json.dumps(payload), headers=headers, timeout=2)
        except Exception as e:
            # Fail silently to avoid recursive logging
            print("Log insertion failed: ", e)

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
