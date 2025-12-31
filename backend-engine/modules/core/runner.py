import importlib
import logging
import sys
import os


def run_automation(account_id, email, password, isp, automation_name, proxy_config=None, device_type="desktop", job_id=None, **kwargs):
    """
    Global runner for any automation.
    Delegates platform logic to the automation's loader.py.
    
    Args:
        job_id: Optional job ID for browser registration with job manager
    """

    logger = logging.getLogger("autoisp")
    profile = email.replace("@", "_").replace(".", "_")

    if getattr(sys, 'frozen', False):
        modules_path = os.path.join(sys._MEIPASS, 'modules')
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        modules_path = os.path.abspath(os.path.join(current_dir, ".."))

    print("modules_path: ", modules_path)
    sys.path.insert(0, modules_path)

    try:
        # Import the automation's loader.py
        loader_module_path = f"automations.{isp}.{automation_name}.loader"
        loader = importlib.import_module(loader_module_path)

        if not hasattr(loader, "run"):
            raise AttributeError(f"{loader_module_path} missing 'run(account_id, email, password, device_type, proxy_config)' function")

        logger.info(f"Running {automation_name} on {isp} for profile {profile}")
        return loader.run(account_id=account_id, email=email, password=password, device_type=device_type, proxy_config=proxy_config, job_id=job_id, **kwargs)

    except Exception as e:
        # Check if it's a cancellation
        if "JobCancelledException" in str(type(e)):
             logger.info(f"Automation {automation_name} cancelled for {profile}")
             return {"status": "cancelled", "message": "Job cancelled by user"}
             
        logger.error(f"Failed to run automation {automation_name}: {e}")
        return {"status": "failed", "message": str(e)}
