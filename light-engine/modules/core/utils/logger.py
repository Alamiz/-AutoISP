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
    logger.setLevel(logging.INFO)

    # Console logs
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)

    return logger