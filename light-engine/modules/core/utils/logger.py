import logging
# import requests
import json
from ..token_storage import token_storage
from modules.core.config import MASTER_API_URL

"""
class MasterAPILogHandler(logging.Handler):
    ...
"""

def configure_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Console logs
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    # Master API logs
    # master_handler = MasterAPILogHandler(master_url=MASTER_API_URL)
    # master_handler.setLevel(logging.INFO)
    # logger.addHandler(master_handler)

    return logger