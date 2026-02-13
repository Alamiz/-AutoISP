"""
FastAPI application entry point for AutoISP local backend.

Run with:
    uvicorn API.app:app --reload --port 8000
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI

from API.database import create_tables
from API.routers import accounts, proxies, jobs


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables if they don't exist
    create_tables()
    yield
    # Shutdown: nothing to clean up for now


app = FastAPI(
    title="AutoISP Local Backend",
    version="0.1.0",
    description="Local desktop backend for managing Accounts, Proxies, and Jobs.",
    lifespan=lifespan,
)

# Register routers under /api prefix
app.include_router(accounts.router, prefix="/api")
app.include_router(proxies.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")


@app.get("/")
def root():
    return {"status": "ok", "message": "AutoISP backend is running"}
