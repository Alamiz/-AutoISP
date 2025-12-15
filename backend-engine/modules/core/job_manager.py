"""
Job Manager - In-memory job tracking with WebSocket broadcasting.

Manages running and queued automation jobs for the desktop app.
Jobs run one at a time - when one completes, the next in queue starts automatically.
"""
import asyncio
import uuid
import threading
import logging
from datetime import datetime
from typing import Optional, Literal, List, Set, Callable, Any, Dict
from pydantic import BaseModel
from fastapi import WebSocket


class Job(BaseModel):
    """Represents an automation job."""
    id: str
    account_id: str
    account_email: str
    automation_id: str
    automation_name: str
    status: Literal["queued", "running", "completed", "failed"]
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
        
        self.logger = logging.getLogger("autoisp")
        
        # In-memory storage
        self.running_jobs: Dict[str, Job] = {}  # Map job_id -> Job
        self.max_concurrent_jobs = 5
        
        self.queued_jobs: List[Job] = []
        self.completed_jobs: List[Job] = []  # Keep last N completed
        self.max_completed_history = 50
        
        # WebSocket clients
        self.ws_clients: Set[WebSocket] = set()
        
        # Callback for starting jobs (set by automations router)
        self._job_runner: Optional[Callable[[Job], Any]] = None
        
        # Stop signals for running jobs (job_id -> Event)
        self._stop_signals: Dict[str, threading.Event] = {}
        
        # Active browser references for force-close (job_id -> browser)
        self._active_browsers: Dict[str, Any] = {}
        
        # Lock for thread safety
        self._lock = threading.Lock()
    
    def set_job_runner(self, runner: Callable[[Job], Any]):
        """Set the callback function that runs a job."""
        self._job_runner = runner
    
    def is_account_busy(self, account_id: str) -> bool:
        """Check if account is already running or queued."""
        with self._lock:
            # Check running jobs
            for job in self.running_jobs.values():
                if job.account_id == account_id:
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
        """Start queued jobs if below concurrency limit."""
        with self._lock:
            # Loop while we have capacity and jobs
            while len(self.running_jobs) < self.max_concurrent_jobs and self.queued_jobs:
                # Pop the next job
                job = self.queued_jobs.pop(0)
                job.status = "running"
                job.started_at = datetime.now()
                self.running_jobs[job.id] = job
                
                # Create stop signal for this job
                self._stop_signals[job.id] = threading.Event()
            
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
            job = self.running_jobs.get(job_id)
            if job:
                job.progress = progress
                self._broadcast_sync("job_progress", job)
    
    def complete_job(self, job_id: str, success: bool = True, error: str = None):
        """Mark job as completed or failed, then start next queued job."""
        with self._lock:
            job = self.running_jobs.get(job_id)
            if not job:
                return
            
            job.status = "completed" if success else "failed"
            job.completed_at = datetime.now()
            job.progress = 100 if success else job.progress
            job.error = error
            
            # Add to history
            self.completed_jobs.insert(0, job)
            if len(self.completed_jobs) > self.max_completed_history:
                self.completed_jobs.pop()
            
            # Clear running job
            self.running_jobs.pop(job_id, None)
        
        event_type = "job_completed" if success else "job_failed"
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
    
    # ==================== STOP FUNCTIONALITY ====================
    
    def register_browser(self, job_id: str, browser: Any):
        """Register a browser instance for a running job (for force-close)."""
        with self._lock:
            self._active_browsers[job_id] = browser
    
    def unregister_browser(self, job_id: str):
        """Unregister browser when job completes normally."""
        with self._lock:
            self._active_browsers.pop(job_id, None)
    
    def is_stopping(self, job_id: str) -> bool:
        """Check if a job has been signaled to stop."""
        with self._lock:
            event = self._stop_signals.get(job_id)
            return event.is_set() if event else False
    
    def _create_stop_signal(self, job_id: str) -> threading.Event:
        """Create a stop signal for a new job."""
        event = threading.Event()
        with self._lock:
            self._stop_signals[job_id] = event
        return event
    
    def _clear_stop_signal(self, job_id: str):
        """Clear stop signal when job completes."""
        with self._lock:
            self._stop_signals.pop(job_id, None)
    
    def stop_job(self, job_id: str) -> bool:
        """
        Stop a specific job (running or queued).
        Returns True if job was found and stopped/cancelled.
        """
        # First try to cancel if queued
        if self.cancel_job(job_id):
            return True
        
        # Check if it's a running job
        with self._lock:
            job = self.running_jobs.get(job_id)
            if not job:
                return False
            
            # Set stop signal
            stop_event = self._stop_signals.get(job_id)
            if stop_event:
                stop_event.set()
            
            # Force-close browser if registered
            browser = self._active_browsers.pop(job_id, None)
            if browser:
                self.logger.info(f"Found active browser for job {job_id}, attempting to close...")
            else:
                self.logger.warning(f"No active browser found for job {job_id} during stop")
        
        # Close browser outside of lock to avoid deadlock
        if browser:
            try:
                # Use force_close to interrupt running operations
                if hasattr(browser, 'force_close'):
                    self.logger.info(f"Calling force_close() on browser for job {job_id}")
                    browser.force_close()
                else:
                    self.logger.info(f"Calling close() on browser for job {job_id}")
                    browser.close()
                self.logger.info(f"Browser closed successfully for job {job_id}")
            except Exception as e:
                self.logger.error(f"Error closing browser for job {job_id}: {e}")
        
        # Mark job as cancelled
        with self._lock:
            job = self.running_jobs.get(job_id)
            if job:
                job.status = "failed"
                job.completed_at = datetime.now()
                job.error = "Job stopped by user"
                
                # Add to history
                self.completed_jobs.insert(0, job)
                if len(self.completed_jobs) > self.max_completed_history:
                    self.completed_jobs.pop()
                
                # Clear running job
                self.running_jobs.pop(job_id, None)
                
                # Cleanup
                self._stop_signals.pop(job_id, None)
        
        if job:
            self._broadcast_sync("job_stopped", job)
            
            # Start next job in queue
            self._try_start_next()
        else:
            self.logger.info(f"Job {job_id} completed while stopping")
        
        return True
    
    def stop_all_jobs(self) -> dict:
        """
        Stop all running jobs and clear all queued jobs.
        Returns summary of what was stopped.
        """
        stopped_running = []
        cancelled_queued = []
        
        with self._lock:
            # Get queued jobs to cancel
            cancelled_queued = [job.id for job in self.queued_jobs]
            
            # Clear queue
            for job in self.queued_jobs:
                self._broadcast_sync("job_cancelled", job)
            self.queued_jobs.clear()
            
            # Get running job info
            stopped_running = list(self.running_jobs.keys())
        
        # Stop running jobs (outside lock)
        for job_id in stopped_running:
            self.stop_job(job_id)
        
        return {
            "stopped_running": stopped_running,
            "cancelled_queued": cancelled_queued,
            "total_stopped": len(stopped_running) + len(cancelled_queued)
        }

    
    def get_snapshot(self) -> dict:
        """Get current state of all jobs for WS connection."""
        with self._lock:
            return {
                "type": "snapshot",
                "running": [job.model_dump(mode="json") for job in self.running_jobs.values()],
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
