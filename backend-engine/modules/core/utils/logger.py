import logging
import requests
import json
from ..token_storage import token_storage

class MasterAPILogHandler(logging.Handler):
    """Custom logging handler that sends logs to the master API."""
    
    def __init__(self, master_url):
        super().__init__()
        self.master_url = master_url.rstrip("/") + "/api/logs/"
        self.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s'))

    def emit(self, record):
        log_entry = self.format(record)
        payload = {
            "level": record.levelname,
            "message": log_entry,
            "logger_name": record.name,
        }

        token = token_storage.get_token()
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        try:
            requests.post(self.master_url, data=json.dumps(payload), headers=headers, timeout=2)
        except Exception:
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
    master_handler = MasterAPILogHandler(master_url="http://master-api:8000")
    master_handler.setLevel(logging.INFO)
    logger.addHandler(master_handler)

    return logger
