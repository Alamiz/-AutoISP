import sys
import io

# Force UTF-8 encoding for stdout/stderr to fix Windows unicode issues
if sys.stdout and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'buffer'):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from modules.routers import automations, auth, backup, jobs
from modules.core.utils.logger import configure_logger

logger = configure_logger()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Replace with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(automations.router)
app.include_router(auth.router)
app.include_router(backup.router)
app.include_router(jobs.router)

@app.get("/")
def root():
    return {"message": "AutoISP API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
