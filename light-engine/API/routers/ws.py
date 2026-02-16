import asyncio
import logging
from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from modules.core.job_manager import job_manager

logger = logging.getLogger("autoisp")

router = APIRouter(tags=["WebSocket"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WS Client connected. Active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WS Client disconnected. Active: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        if not self.active_connections:
            return
            
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"WS Send Error: {e}")
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

# ---------------------------------------------------------------------------
# Bridge logic: JobManager (Thread) -> WebSocket (Async Loop)
# ---------------------------------------------------------------------------
_main_loop = None

def set_main_event_loop(loop):
    """Called from main app startup to capture the async loop."""
    global _main_loop
    _main_loop = loop
    # Hook into JobManager
    job_manager.set_event_callback(on_job_manager_event)
    logger.info("WebSocket bridge initialized with main event loop")

def on_job_manager_event(event_type: str, data: dict):
    if _main_loop and manager.active_connections:
        message = {"type": event_type, "data": data}
        try:
            asyncio.run_coroutine_threadsafe(manager.broadcast(message), _main_loop)
        except Exception as e:
            logger.error(f"Failed to schedule WS broadcast: {e}")

# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------
@router.websocket("/ws/jobs")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # We just listen to keep connection open. 
            # In future we could handle incoming commands (e.g. cancel job).
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            manager.disconnect(websocket)
        except:
            pass
