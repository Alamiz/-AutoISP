"""
Jobs Router - REST and WebSocket endpoints for job management.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from modules.core.job_manager import job_manager

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("")
def get_jobs():
    """Get current running, queued, and recent completed jobs."""
    return job_manager.get_snapshot()


@router.delete("/{job_id}")
def cancel_job(job_id: str):
    """Cancel a queued job."""
    if job_manager.cancel_job(job_id):
        return {"status": "cancelled", "job_id": job_id}
    raise HTTPException(status_code=404, detail="Job not found or already running")


@router.post("/{job_id}/stop")
def stop_job(job_id: str):
    """Stop a specific job (running or queued)."""
    if job_manager.stop_job(job_id):
        return {"status": "stopped", "job_id": job_id}
    raise HTTPException(status_code=404, detail="Job not found")


@router.post("/stop-all")
def stop_all_jobs():
    """Stop all running and queued jobs."""
    result = job_manager.stop_all_jobs()
    return {"status": "stopped", **result}


@router.websocket("/ws")
async def jobs_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time job updates.
    
    On connect: Sends snapshot of all current jobs.
    On changes: Broadcasts job_queued, job_started, job_completed, job_failed events.
    """
    await job_manager.register_client(websocket)
    try:
        # Keep connection alive, listen for any client messages (optional ping/pong)
        while True:
            # Wait for client messages (can be used for ping/pong or commands)
            data = await websocket.receive_text()
            # For now, just echo or ignore
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        job_manager.unregister_client(websocket)
    except Exception:
        job_manager.unregister_client(websocket)
