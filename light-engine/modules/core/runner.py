import importlib
import logging
import sys
import os
import asyncio


from modules.core.models import Account

async def run_automation(account: Account, automation_name: str, job_id=None, log_dir=None, **kwargs):
    """
    Global runner for any automation (Async).
    Delegates platform logic to the automation's loader.py.
    
    Args:
        account: Account object containing all account details
        automation_name: Name of the automation to run
        job_id: Optional job ID for browser registration with job manager
        log_dir: Optional directory for per-account file logging
    """

    profile = account.email.replace("@", "_").replace(".", "_")
    isp = account.provider

    # Set up logger
    if log_dir:
        # Create a child logger for this specific account to keep file logs separate
        logger_name = f"autoisp.acc_{profile}"
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        
        # Add file handler if not already present
        if not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
            log_file = os.path.join(log_dir, "log.txt")
            fh = logging.FileHandler(log_file, encoding='utf-8')
            fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            logger.addHandler(fh)
    else:
        logger = logging.getLogger("autoisp")

    if getattr(sys, 'frozen', False):
        modules_path = os.path.join(sys._MEIPASS, 'modules')
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        modules_path = os.path.abspath(os.path.join(current_dir, ".."))

    if modules_path not in sys.path:
        sys.path.insert(0, modules_path)

    try:
        # Import the automation's loader.py
        loader_module_path = f"automations.{isp}.{automation_name}.loader"
        loader = importlib.import_module(loader_module_path)

        if not hasattr(loader, "run"):
            raise AttributeError(f"{loader_module_path} missing 'run(account, job_id, **kwargs)' function")

        logger.info(f"Running {automation_name} on {isp} for profile {profile}", extra={"account_id": account.id, "is_global": True})
        
        # Await the loader's run method
        run_args = {"account": account, "job_id": job_id, "log_dir": log_dir, "logger": logger, **kwargs}
        
        if asyncio.iscoroutinefunction(loader.run):
             return await loader.run(**run_args)
        else:
             logger.warning(f"Loader for {automation_name} is sync! Blocking event loop.", extra={"account_id": account.id})
             return loader.run(**run_args)

    except Exception as e:
        # Check if it's a cancellation
        if "JobCancelledException" in str(type(e)):
             logger.info(f"Automation {automation_name} cancelled for {profile}", extra={"account_id": account.id, "is_global": True})
             return {"status": "cancelled", "message": "Job cancelled by user"}
             
        logger.error(f"Failed to run automation {automation_name}: {e}", extra={"account_id": account.id, "is_global": True})
        return {"status": "failed", "message": str(e)}
    finally:
        # Close and remove file handlers if we created them
        if log_dir:
            for handler in logger.handlers[:]:
                if isinstance(handler, logging.FileHandler):
                    handler.close()
                    logger.removeHandler(handler)
