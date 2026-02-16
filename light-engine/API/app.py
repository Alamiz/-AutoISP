"""
FastAPI application entry point for AutoISP local backend.

Run with:
    uvicorn API.app:app --reload --port 8000
"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from API.database import create_tables
from API.routers import accounts, proxies, jobs, ws


from modules.core.job_manager import job_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables if they don't exist
    create_tables()
    # Capture loop for WebSocket bridge
    ws.set_main_event_loop(asyncio.get_running_loop())
    
    # Start JobManager worker
    job_manager.start_worker()
    
    yield
    
    # Shutdown
    job_manager.stop_worker()


app = FastAPI(
    title="AutoISP Local Backend",
    version="0.1.0",
    description="Local desktop backend for managing Accounts, Proxies, and Jobs.",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local development, allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers under /api prefix
app.include_router(accounts.router, prefix="/api")
app.include_router(proxies.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(ws.router) # WebSocket is usually at root or /ws



@app.get("/")
def root():
    return {"status": "ok", "message": "AutoISP backend is running"}
