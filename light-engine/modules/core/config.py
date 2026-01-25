import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration for the Master API
# This can be overridden by an environment variable if needed in the future
MASTER_API_URL = os.getenv("MASTER_API_URL", "http://139.162.141.200:8000")