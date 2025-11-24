import importlib
import logging
import sys
import os

def run_automation(email, password, isp, automation_name, proxy_config=None, device_type="desktop"):
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
        module_path = f"automations.{isp}.{automation_name}.run"
        module = importlib.import_module(module_path)

        if hasattr(module, "main"):
            logger.info(
                f"Running {automation_name} on {isp} for profile {profile}."
            )
            
            # Log proxy usage if configured
            if proxy_config:
                logger.info(f"Using proxy: {proxy_config['type']}://{proxy_config['host']}:{proxy_config['port']}")
            
            logger.info(f"Device type: {device_type}")

            # Pass proxy_config to the main function
            if proxy_config:
                return module.main(email, password, proxy_config=proxy_config, device_type=device_type)
            else:
                return module.main(email, password, device_type=device_type)

        raise AttributeError(f"{module_path} missing 'main(email)' entrypoint.")

    except Exception as e:
        logger.exception(f"Failed to run automation {automation_name}: {e}")
        raise
