import importlib
import logging
import sys
import os

def run_automation(email, password, isp, automation_name, proxy_config=None, device_type="desktop"):
    """
    Global runner for any automation.
    Delegates platform logic to the automation's loader.py.
    """

    logger = logging.getLogger("autoisp")
    profile = email.split('@')[0]

    if getattr(sys, 'frozen', False):
        application_path = sys._MEIPASS
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))

    sys.path.insert(0, application_path)

    try:
        # Import the automation's loader.py
        loader_module_path = f"automations.{isp}.{automation_name}.loader"
        loader = importlib.import_module(loader_module_path)

        if not hasattr(loader, "run"):
            raise AttributeError(f"{loader_module_path} missing 'run(email, password, device_type, proxy_config)' function")

        logger.info(f"Running {automation_name} on {isp} for profile {profile}")
        return loader.run(email=email, password=password, device_type=device_type, proxy_config=proxy_config)

    except Exception as e:
        logger.exception(f"Failed to run automation {automation_name}: {e}")
        raise
