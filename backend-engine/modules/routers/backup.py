from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
import asyncio
from modules.core.backups.utils import run_backup
from modules.core.backups.progress_store import progress_queues

router = APIRouter(prefix="/backups", tags=["Backups"])

@router.post("/{account_id}/start")
async def start_backup(account_id: str):
    """Start a backup for the given account profile."""
    if not account_id:
        raise HTTPException(status_code=400, detail="Account ID is required")
    
    if account_id not in progress_queues:
        progress_queues[account_id] = asyncio.Queue()

    asyncio.create_task(run_backup(account_id))
    return {"status": "started", "account_id": account_id}

@router.websocket("/{account_id}/progress")
async def progress_ws(websocket: WebSocket, account_id: str):
    await websocket.accept()

    if account_id not in progress_queues:
        progress_queues[account_id] = asyncio.Queue()

    queue = progress_queues[account_id]

    try:
        while True:
            try:
                # Wait for new progress for max 1 second
                progress = await asyncio.wait_for(queue.get(), timeout=1.0)
                await websocket.send_json(progress)
            except asyncio.TimeoutError:
                # No progress yet, just continue to keep connection alive
                continue
    except WebSocketDisconnect:
        print(f"[WS] Client disconnected: {account_id}")