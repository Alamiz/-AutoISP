import os

# Configuration for the Master API
# This can be overridden by an environment variable if needed in the future
MASTER_API_URL = os.getenv("MASTER_API_URL", "http://localhost:8000")
