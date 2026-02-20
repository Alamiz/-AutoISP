import asyncio
import logging
import json
import traceback
from collections import deque
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session
from API.database import SessionLocal
from API.models import Job, JobAccount, JobAutomation, Account as DBAccount
from modules.core.models import Account as CoreAccount
from modules.core.runner import run_automation
from API.database import BASE_DIR
import os

logger = logging.getLogger("autoisp")

class JobManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(JobManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self.job_queue = asyncio.Queue()
        self.current_job_id: Optional[int] = None
        self.worker_task: Optional[asyncio.Task] = None
        
        # Callback for updates: async func(event_type: str, data: dict)
        self.on_event = None
        
        self._initialized = True


    def start_worker(self):
        """Start the background worker task."""
        if self.worker_task and not self.worker_task.done():
            return
        
        loop = asyncio.get_event_loop()
        self.worker_task = loop.create_task(self._worker_loop())
        logger.info("JobManager async worker started")

    def stop_worker(self):
        if self.worker_task:
            self.worker_task.cancel()
            self.worker_task = None

    def set_event_callback(self, callback):
        self.on_event = callback

    async def _emit(self, event_type: str, data: Dict[str, Any]):
        if self.on_event:
            try:
                # If callback is async, await it; else call it
                if asyncio.iscoroutinefunction(self.on_event):
                    await self.on_event(event_type, data)
                else:
                    self.on_event(event_type, data)
            except Exception as e:
                logger.error(f"Error in event callback: {e}")

    async def submit_job(self, job_id: int):
        """Submit a job to the async queue."""
        logger.info(f"Submitting job {job_id} to queue")
        await self.job_queue.put(job_id)
        await self._emit("job_queued", {"job_id": job_id})

    async def _worker_loop(self):
        """Main loop processing jobs from the queue."""
        logger.info("Worker loop running...")
        while True:
            try:
                job_id = await self.job_queue.get()
                logger.info(f"Picked up job {job_id}")
                await self._process_job(job_id)
                self.job_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in worker loop: {e}")
                traceback.print_exc()

    async def _process_job(self, job_id: int):
        """Logic to process a specific job."""
        try:
            # Create timestamped run folder inside BASE_DIR/output
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_root = os.path.join(BASE_DIR, "output")
            run_output_dir = os.path.join(output_root, f"automation_run_{timestamp}")
            os.makedirs(run_output_dir, exist_ok=True)
            logger.info(f"Created run output directory: {run_output_dir}")

            # Fetch job details to get max_concurrent
            db_job = await asyncio.to_thread(self._get_job, job_id)
            if not db_job:
                logger.error(f"Job {job_id} not found in database")
                return
            
            max_concurrent = db_job.max_concurrent or 1

            # Mark job as running
            await asyncio.to_thread(self._update_job_status, job_id, "running", start=True)
            
            await self._emit("job_started", {
                "job_id": job_id,
                "status": "running",
                "started_at": datetime.now(timezone.utc).isoformat(),
                "output_dir": run_output_dir
            })

            # Fetch automations and accounts
            automations, accounts = await asyncio.to_thread(self._get_job_details, job_id)
            
            if not automations:
                logger.warning(f"Job {job_id} has no enabled automations")
                await asyncio.to_thread(self._update_job_status, job_id, "completed", finish=True)
                await self._emit("job_completed", {"job_id": job_id, "status": "completed"})
                return

            # Execute automations sequentially
            for automation in automations:
                logger.info(f"Starting automation {automation.automation_name} for job {job_id}")
                
                 # Execute accounts concurrently for this automation
                await self._run_automation_for_accounts(
                     job_id, automation, accounts, max_concurrent, run_output_dir
                )

            await asyncio.to_thread(self._update_job_status, job_id, "completed", finish=True)
            await self._emit("job_completed", {
                "job_id": job_id,
                "status": "completed",
                "finished_at": datetime.now(timezone.utc).isoformat()
            })

        except Exception as e:
            logger.error(f"Failed to process job {job_id}: {e}")
            traceback.print_exc()
            await asyncio.to_thread(self._update_job_status, job_id, "failed", finish=True)
            await self._emit("job_completed", {"job_id": job_id, "status": "failed"})
            
        finally:
            self.current_job_id = None

    async def _run_automation_for_accounts(
        self, 
        job_id: int, 
        automation: Any, # SQLAlchemy object
        job_accounts: List[Any],
        concurrency: int,
        run_output_dir: str
    ):
        """Run a specific automation for all accounts in the job concurrently."""
        
        settings = json.loads(automation.settings_json) if automation.settings_json else {}
        automation_name = automation.automation_name
        
        semaphore = asyncio.Semaphore(concurrency)
        
        tasks = []
        for ja in job_accounts:
            # Update status to running (sync DB)
            await asyncio.to_thread(self._update_account_status, ja.id, "running")
            await self._emit("account_update", {
                "job_id": job_id,
                "account_id": ja.account_id,
                "job_account_id": ja.id,
                "status": "running"
            })

            # Construct CoreAccount (we assume ja.account is eager loaded or valid)
            # Fetch full account data in thread to avoid lazy load block
            core_account = await asyncio.to_thread(self._build_core_account, ja)

            # Create account-specific logs folder
            email_folder = core_account.email.replace("@", "_").replace(".", "_")
            account_log_dir = os.path.join(run_output_dir, "accounts", email_folder)
            os.makedirs(account_log_dir, exist_ok=True)

            # Create task
            task = asyncio.create_task(
                self._run_single_account(
                    semaphore, core_account, automation_name, job_id, ja.id, settings, account_log_dir
                )
            )
            tasks.append(task)
            
        await asyncio.gather(*tasks)

    async def _run_single_account(self, semaphore, core_account, automation_name, job_id, job_account_id, settings, log_dir):
        async with semaphore:
            try:
                # This is the key async call to the runner
                result = await run_automation(
                    account=core_account,
                    automation_name=automation_name,
                    job_id=str(job_id),
                    log_dir=log_dir,
                    **settings
                )
                
                status = result.get("status", "completed") if isinstance(result, dict) else "completed"
                msg = result.get("message", "") if isinstance(result, dict) else str(result)
                
                # Normalize status
                status = status.lower()
                
            except asyncio.CancelledError:
                 status = "cancelled"
                 msg = "Job cancelled"
            except Exception as e:
                logger.error(f"Account {core_account.email} failed: {e}")
                status = "failed"
                msg = str(e)
            
            # Update DB
            await asyncio.to_thread(self._update_account_status, job_account_id, status, msg)
            await self._emit("account_update", {
                "job_id": job_id,
                "account_id": core_account.id, # Note: check if ID mismatch (db vs core)
                 "job_account_id": job_account_id,
                "status": status,
                "message": msg
            })

    # ─────────────────────────────────────────────────────────────
    # Sync DB Helpers (run in threads)
    # ─────────────────────────────────────────────────────────────

    def _get_job(self, job_id):
        db = SessionLocal()
        try:
            return db.query(Job).filter(Job.id == job_id).first()
        finally:
            db.close()

    def _update_job_status(self, job_id, status, start=False, finish=False):
        db = SessionLocal()
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = status
                if start:
                    job.started_at = datetime.now(timezone.utc)
                if finish:
                    job.finished_at = datetime.now(timezone.utc)
                db.commit()
        finally:
            db.close()

    def _get_job_details(self, job_id):
        db = SessionLocal()
        try:
            automations = db.query(JobAutomation).filter(
                JobAutomation.job_id == job_id,
                JobAutomation.enabled == True
            ).order_by(JobAutomation.run_order).all()
            
            # Eager load account and proxy to avoid detatched instance errors
            from sqlalchemy.orm import joinedload
            accounts = db.query(JobAccount).options(
                joinedload(JobAccount.account),
                joinedload(JobAccount.proxy)
            ).filter(JobAccount.job_id == job_id).all()
            
            # Detach/Expunge to use outside session? 
            # Better to just extraction data here or keep session scope short.
            # We'll rely on the objects staying valid if simple, or we construct dicts.
            # But we pass objects to _run_automation_for_accounts... 
            # Strategy: The objects are detached when session closes. accessing lazy attrs triggers error.
            # So we enable joinedload above.
            db.expunge_all() 
            return automations, accounts
        finally:
            db.close()

    def _update_account_status(self, job_account_id, status, error_message=None):
        db = SessionLocal()
        try:
             ja = db.query(JobAccount).filter(JobAccount.id == job_account_id).first()
             if ja:
                 # Update the specific job record
                 ja.status = status
                 if error_message:
                     ja.error_message = error_message
                 
                 # Also update the Master Account status to reflect current health
                 if ja.account:
                     # Map automation success to "active" for the sidebar/list
                     if status in ["success", "completed"]:
                         ja.account.status = "active"
                     else:
                         # For errors like 'locked', 'wrong_password', 'suspended', 
                         # we propagate the specific status to the master account
                         ja.account.status = status
                 
                 db.commit()
        finally:
            db.close()

    def _build_core_account(self, ja):
        """Convert DB JobAccount (attached/detached) to CoreAccount."""
        # Note: 'ja' comes from _get_job_details where we expunged.
        # Ensure ja.account is loaded.
        
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
        
        return CoreAccount(
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

# Global instance
job_manager = JobManager()
