import threading
import time
import logging
import json
import traceback
from collections import deque
from concurrent.futures import ThreadPoolExecutor, Future, TimeoutError as FuturesTimeoutError
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session
from API.database import SessionLocal
from API.models import Job, JobAccount, JobAutomation, Account as DBAccount
from modules.core.models import Account as CoreAccount
from modules.core.runner import run_automation

logger = logging.getLogger("autoisp")

class JobManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(JobManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self.job_queue = deque()
        self.current_job_id: Optional[int] = None
        self.is_running = False
        self.worker_thread = None
        self._stop_event = threading.Event()
        
        # Callback for WebSocket updates: func(event_type: str, data: dict)
        self.on_event = None
        
        self._initialized = True


    def start_worker(self):
        if self.worker_thread and self.worker_thread.is_alive():
            return
        
        self._stop_event.clear()
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True, name="JobManagerWorker")
        self.worker_thread.start()
        logger.info("JobManager worker thread started")

    def stop_worker(self):
        self._stop_event.set()
        if self.worker_thread:
            self.worker_thread.join(timeout=5)

    def set_event_callback(self, callback):
        self.on_event = callback

    def _emit(self, event_type: str, data: Dict[str, Any]):
        if self.on_event:
            try:
                self.on_event(event_type, data)
            except Exception as e:
                logger.error(f"Error in event callback: {e}")

    def submit_job(self, job_id: int):
        """Submit a job to the queue."""
        logger.info(f"Submitting job {job_id} to queue")
        self.job_queue.append(job_id)
        self._emit("job_queued", {"job_id": job_id})

    def _worker_loop(self):
        """Main loop processing jobs from the queue."""
        while not self._stop_event.is_set():
            if not self.job_queue:
                time.sleep(1)
                continue

            try:
                job_id = self.job_queue.popleft()
                self._process_job(job_id)
            except Exception as e:
                logger.error(f"Error in worker loop: {e}")
                traceback.print_exc()

    def _process_job(self, job_id: int):
        """Execute a single job."""
        self.current_job_id = job_id
        db: Session = SessionLocal()
        
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                logger.error(f"Job {job_id} not found")
                return

            # Mark job as running
            job.status = "running"
            job.started_at = datetime.now(timezone.utc)
            db.commit()
            
            self._emit("job_started", {
                "job_id": job.id,
                "status": "running",
                "started_at": job.started_at.isoformat()
            })

            # Fetch job details
            job_automations = db.query(JobAutomation).filter(
                JobAutomation.job_id == job_id,
                JobAutomation.enabled == True
            ).order_by(JobAutomation.run_order).all()

            job_accounts = db.query(JobAccount).filter(JobAccount.job_id == job_id).all()
            
            if not job_automations:
                logger.warning(f"Job {job_id} has no enabled automations")
                self._complete_job(db, job, "completed")
                return

            # Execute automations sequentially
            for automation in job_automations:
                logger.info(f"Starting automation {automation.automation_name} for job {job_id}")
                
                # Execute accounts concurrently for this automation
                self._run_automation_for_accounts(
                    db, job, automation, job_accounts
                )

                if self._stop_event.is_set():
                    break
            
            # Check if all accounts failed or if job was successful
            # For now, if we finished all automations, we mark as completed
            # We could improve this to check if any critical failures occurred
            self._complete_job(db, job, "completed" if not self._stop_event.is_set() else "cancelled")

        except Exception as e:
            logger.error(f"Failed to process job {job_id}: {e}")
            traceback.print_exc()
            if job:
                self._complete_job(db, job, "failed")
        finally:
            db.close()
            self.current_job_id = None

    def _complete_job(self, db: Session, job: Job, status: str):
        job.status = status
        job.finished_at = datetime.now(timezone.utc)
        db.commit()
        
        self._emit("job_completed", {
            "job_id": job.id,
            "status": status,
            "finished_at": job.finished_at.isoformat()
        })
        logger.info(f"Job {job.id} finished with status: {status}")

    def _run_automation_for_accounts(
        self, 
        db: Session, 
        job: Job, 
        automation: JobAutomation, 
        job_accounts: List[JobAccount]
    ):
        """Run a specific automation for all accounts in the job concurrently."""
        
        # Prepare arguments
        settings = json.loads(automation.settings_json) if automation.settings_json else {}
        automation_name = automation.automation_name
        
        # We need to map JobAccount to CoreAccount (compatible with runner)
        # and keep track of JobAccount DB objects to update status
        
        futures_map = {}
        
        with ThreadPoolExecutor(max_workers=job.max_concurrent) as executor:
            for ja in job_accounts:
                # Refresh JobAccount status to running for this automation?
                # Actually, JobAccount status reflects the *overall* status or the *current* status.
                # Let's update it to "running"
                ja.status = "running"
                ja.error_message = None # Clear previous errors? Or keep log?
                db.commit()
                
                self._emit("account_update", {
                    "job_id": job.id,
                    "account_id": ja.account_id,
                    "job_account_id": ja.id,
                    "status": "running"
                })

                # Construct CoreAccount
                # We need to fetch the full account details including provider, password etc.
                # ja.account is lazy loaded, accessed within session is fine.
                db_account = ja.account
                proxy_settings = None
                if ja.proxy:
                    proxy_settings = {
                        "protocol": "http",
                        "host": ja.proxy.ip,
                        "port": ja.proxy.port,
                        "username": ja.proxy.username,
                        "password": ja.proxy.password
                    }
                
                core_account = CoreAccount(
                    id=str(db_account.id),
                    email=db_account.email,
                    password=db_account.password,
                    provider=db_account.provider,
                    proxy_settings=proxy_settings,
                    credentials={
                        "password": db_account.password,
                        "recovery_email": db_account.recovery_email,
                        "phone_number": db_account.phone_number
                    }
                )

                # Submit to executor
                future = executor.submit(
                    run_automation,
                    account=core_account,
                    automation_name=automation_name,
                    job_id=str(job.id),
                    **settings
                )
                futures_map[future] = ja

            # Wait for completion (with timeout to prevent indefinite hangs)
            ACCOUNT_TIMEOUT = 600  # 10 minutes per account
            for future in futures_map:
                ja = futures_map[future]
                try:
                    result = future.result(timeout=ACCOUNT_TIMEOUT)
                    # result is typically a dict {"status": "success", "message": "..."}
                    
                    status = "completed"
                    msg = ""
                    
                    if isinstance(result, dict):
                        status = result.get("status", "completed")
                        msg = result.get("message", "")
                    
                    # Map runner statuses to simple UI statuses if needed
                    # For now keep as is, but lowercase/normalize
                    ja.status = status.lower()
                    ja.error_message = msg
                    
                except FuturesTimeoutError:
                    logger.error(f"Account {ja.account.email} timed out after {ACCOUNT_TIMEOUT}s")
                    ja.status = "failed"
                    ja.error_message = f"Timed out after {ACCOUNT_TIMEOUT}s"
                    future.cancel()
                except Exception as e:
                    logger.error(f"Account {ja.account.email} failed: {e}")
                    ja.status = "failed"
                    ja.error_message = str(e)
                
                db.commit()
                self._emit("account_update", {
                    "job_id": job.id,
                    "account_id": ja.account_id,
                    "job_account_id": ja.id,
                    "status": ja.status,
                    "message": ja.error_message
                })

# Global instance
job_manager = JobManager()
