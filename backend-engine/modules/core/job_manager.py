"""
Job Manager - In-memory job tracking with WebSocket broadcasting.

Manages running and queued automation jobs for the desktop app.
Jobs run one at a time - when one completes, the next in queue starts automatically.
"""
import asyncio
import uuid
import threading
from datetime import datetime
from typing import Optional, Literal, List, Set, Callable, Any
from pydantic import BaseModel
from fastapi import WebSocket


class Job(BaseModel):
    """Represents an automation job."""
    id: str
    account_id: str
    account_email: str
    automation_id: str
    automation_name: str
    status: Literal["queued", "running", "completed", "failed", "cancelling", "cancelled"]
    queued_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: int = 0
    error: Optional[str] = None
    
    # Store execution params for when job is picked from queue
    execution_params: dict = {}
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class JobManager:
    """
    Singleton job manager for tracking and broadcasting job states.
    
    Jobs run ONE AT A TIME. When an automation is requested with multiple accounts,
    all are queued and run sequentially.
    """
    
    _instance: Optional["JobManager"] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        # In-memory storage
        self.running_job: Optional[Job] = None  # Only ONE job runs at a time
        self.queued_jobs: List[Job] = []
        self.completed_jobs: List[Job] = []  # Keep last N completed
        self.max_completed_history = 50
        
        # WebSocket clients
        self.ws_clients: Set[WebSocket] = set()
        
        # Callback for starting jobs (set by automations router)
        self._job_runner: Optional[Callable[[Job], Any]] = None
        
        # Lock for thread safety
        self._lock = threading.Lock()
    
    def set_job_runner(self, runner: Callable[[Job], Any]):
        """Set the callback function that runs a job."""
        self._job_runner = runner
    
    def is_account_busy(self, account_id: str) -> bool:
        """Check if account is already running or queued."""
        with self._lock:
            # Check running job
            if self.running_job and self.running_job.account_id == account_id:
                return True
            # Check queued jobs
            for job in self.queued_jobs:
                if job.account_id == account_id:
                    return True
            return False
    
    def queue_job(
        self,
        account_id: str,
        account_email: str,
        automation_id: str,
        automation_name: str,
        execution_params: dict = None,
    ) -> Optional[Job]:
        """
        Queue a new job. Returns None if account is already busy.
        If no job is running, starts immediately.
        """
        if self.is_account_busy(account_id):
            return None
        
        job = Job(
            id=str(uuid.uuid4()),
            account_id=account_id,
            account_email=account_email,
            automation_id=automation_id,
            automation_name=automation_name,
            status="queued",
            queued_at=datetime.now(),
            execution_params=execution_params or {},
        )
        
        with self._lock:
            self.queued_jobs.append(job)
        
        self._broadcast_sync("job_queued", job)
        
        # Try to start if nothing is running
        self._try_start_next()
        
        return job
    
    def _try_start_next(self):
        """Start the next queued job if nothing is running."""
        with self._lock:
            if self.running_job is not None:
                return  # Already running
            
            if not self.queued_jobs:
                return  # Nothing queued
            
            # Pop the next job
            job = self.queued_jobs.pop(0)
            job.status = "running"
            job.started_at = datetime.now()
            self.running_job = job
        
        self._broadcast_sync("job_started", job)
        
        # Run the job via callback
        if self._job_runner:
            # Run in background thread to not block
            thread = threading.Thread(target=self._execute_job, args=(job,))
            thread.start()
    
    def _execute_job(self, job: Job):
        """Execute job in background thread."""
        try:
            self._job_runner(job)
        except Exception as e:
            # Job runner should handle its own errors, but catch here as fallback
            self.complete_job(job.id, success=False, error=str(e))
    
    def update_progress(self, job_id: str, progress: int):
        """Update job progress (0-100)."""
        with self._lock:
            if self.running_job and self.running_job.id == job_id:
                self.running_job.progress = progress
                self._broadcast_sync("job_progress", self.running_job)
    
    def complete_job(self, job_id: str, success: bool = True, error: str = None):
        """Mark job as completed or failed, then start next queued job."""
        with self._lock:
            if not self.running_job or self.running_job.id != job_id:
                return
            
            job = self.running_job
            
            # If it was cancelled, mark as cancelled instead of success/fail
            if job.status == "cancelling":
                job.status = "cancelled"
                success = False # Technically not a success
                error = "Job cancelled by user"
            else:
                job.status = "completed" if success else "failed"
                
            job.completed_at = datetime.now()
            job.progress = 100 if success else job.progress
            job.error = error
            
            # Add to history
            self.completed_jobs.insert(0, job)
            if len(self.completed_jobs) > self.max_completed_history:
                self.completed_jobs.pop()
            
            # Clear running job
            self.running_job = None
        
        event_type = "job_completed" if success else ("job_cancelled" if job.status == "cancelled" else "job_failed")
        self._broadcast_sync(event_type, job)
        
        # Start next job in queue
        self._try_start_next()
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a queued job. Returns True if cancelled."""
        with self._lock:
            for i, job in enumerate(self.queued_jobs):
                if job.id == job_id:
                    cancelled_job = self.queued_jobs.pop(i)
                    self._broadcast_sync("job_cancelled", cancelled_job)
                    return True
        return False

    def stop_job(self, job_id: str) -> bool:
        """
        Stop a specific job.
        If queued: removes from queue.
        If running: sets status to 'cancelling' and force closes browser.
        """
        print(f"🛑 Attempting to stop job {job_id}")
        
        # First check queue
        if self.cancel_job(job_id):
            print(f"✅ Job {job_id} cancelled from queue")
            return True
            
        # Check running job
        with self._lock:
            if self.running_job:
                print(f"ℹ️ Current running job: {self.running_job.id}, Status: {self.running_job.status}")
                if self.running_job.id == job_id:
                    print(f"⚠️ Stopping running job {job_id}")
                    self.running_job.status = "cancelling"
                    self._broadcast_sync("job_cancelling", self.running_job)
                    
                    # Force close browser
                    try:
                        from modules.core.browser.registry import browser_registry
                        browser_registry.force_close(job_id)
                    except Exception as e:
                        print(f"❌ Error force closing browser: {e}")
                    
                    return True
                else:
                    print(f"❌ Job ID mismatch: {self.running_job.id} != {job_id}")
            else:
                print("ℹ️ No running job found")
        
        return False

    def stop_all_jobs(self):
        """Clear the queue and stop the currently running job."""
        with self._lock:
            # Clear queue
            cancelled_jobs = list(self.queued_jobs)
            self.queued_jobs.clear()
            
            # Stop running job
            if self.running_job:
                self.running_job.status = "cancelling"
                self._broadcast_sync("job_cancelling", self.running_job)
                
                # Force close browser
                from modules.core.browser.registry import browser_registry
                browser_registry.force_close(self.running_job.id)
        
        # Broadcast cancellations for queued jobs
        for job in cancelled_jobs:
            self._broadcast_sync("job_cancelled", job)

    def check_cancellation(self, job_id: str):
        """
        Check if the specific job is cancelled.
        Raises JobCancelledException if it is.
        """
        from modules.core.utils.exceptions import JobCancelledException
        
        # We only care about the running job for this check
        # because queued jobs are just removed from the list
        with self._lock:
            if self.running_job and self.running_job.id == job_id:
                if self.running_job.status == "cancelling":
                    raise JobCancelledException(f"Job {job_id} was cancelled")
            
            # Also check if the job is no longer the running job (e.g. force stopped and cleared)
            # But be careful: if we are in the thread of the job, self.running_job SHOULD be us.
            # If self.running_job is None or different ID, it means we were forcefully removed/replaced?
            # For now, just checking status is enough.
            
    def get_snapshot(self) -> dict:
        """Get current state of all jobs for WS connection."""
        with self._lock:
            return {
                "type": "snapshot",
                "running": [self.running_job.model_dump(mode="json")] if self.running_job else [],
                "queued": [job.model_dump(mode="json") for job in self.queued_jobs],
                "completed": [job.model_dump(mode="json") for job in self.completed_jobs[:10]],  # Last 10
            }
    
    # WebSocket management
    async def register_client(self, websocket: WebSocket):
        """Register a new WebSocket client and send snapshot."""
        await websocket.accept()
        self.ws_clients.add(websocket)
        # Send current state
        await websocket.send_json(self.get_snapshot())
    
    def unregister_client(self, websocket: WebSocket):
        """Remove a WebSocket client."""
        self.ws_clients.discard(websocket)
    
    def _broadcast_sync(self, event_type: str, job: Job):
        """Broadcast job event (thread-safe, works from sync context)."""
        message = {
            "type": event_type,
            "job": job.model_dump(mode="json"),
        }
        
        # Try to get running event loop, create task if exists
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._async_broadcast(message))
        except RuntimeError:
            # No running loop, run directly (blocking)
            asyncio.run(self._async_broadcast(message))
    
    async def _async_broadcast(self, message: dict):
        """Async broadcast to all connected clients."""
        disconnected = set()
        for client in list(self.ws_clients):
            try:
                await client.send_json(message)
            except Exception:
                disconnected.add(client)
        
        # Clean up disconnected clients
        self.ws_clients -= disconnected


# Global singleton instance
job_manager = JobManager()
