import importlib
import logging
import sys
import os

def run_automation(email, password, isp, automation_name):
    """
    Dynamically import and execute a specific automation task.
    Example: category='browsing', automation_id='google_search', parameters={'query': 'test'}
    """

    logger = logging.getLogger("autoisp")

    profile = email.split('@')[0]

    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        application_path = sys._MEIPASS
    else:
        # Running as script
        application_path = os.path.dirname(os.path.abspath(__file__))

    # Ensure automations can be found
    sys.path.insert(0, application_path)

    try:
        module_path = f"automations.{isp}.{automation_name}"
        module = importlib.import_module(module_path)

        if hasattr(module, "main"):
            logger.info(
                f"Running {automation_name} on {isp} for profile {profile}."
            )
            return module.main(email, password)

        raise AttributeError(f"{module_path} missing 'main(email)' entrypoint.")

    except Exception as e:
        logger.exception(f"Failed to run automation {automation_name}: {e}")
        raise