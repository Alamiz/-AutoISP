import importlib
import logging
import sys
import os
import asyncio


from modules.core.models import Account

async def run_automation(account: Account, automation_name: str, job_id=None, **kwargs):
    """
    Global runner for any automation (Async).
    Delegates platform logic to the automation's loader.py.
    
    Args:
        account: Account object containing all account details
        automation_name: Name of the automation to run
        job_id: Optional job ID for browser registration with job manager
    """

    logger = logging.getLogger("autoisp")
    profile = account.email.replace("@", "_").replace(".", "_")
    isp = account.provider

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
        
        # Await the loader's run method (assuming loader is also migrated to async)
        if asyncio.iscoroutinefunction(loader.run):
             return await loader.run(account=account, job_id=job_id, **kwargs)
        else:
             # Fallback for legacy sync loaders (will block loop if not threaded)
             # Ideally efficiently migrated to async
             logger.warning(f"Loader for {automation_name} is sync! Blocking event loop.", extra={"account_id": account.id})
             return loader.run(account=account, job_id=job_id, **kwargs)

    except Exception as e:
        # Check if it's a cancellation
        if "JobCancelledException" in str(type(e)):
             logger.info(f"Automation {automation_name} cancelled for {profile}", extra={"account_id": account.id, "is_global": True})
             return {"status": "cancelled", "message": "Job cancelled by user"}
             
        logger.error(f"Failed to run automation {automation_name}: {e}", extra={"account_id": account.id, "is_global": True})
        return {"status": "failed", "message": str(e)}
