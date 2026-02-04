from .desktop.run import OpenProfile as DesktopOpenProfile

def run(account, job_id=None, **kwargs):
    """
    Selects the right platform (desktop/mobile) and runs the automation.
    """
    # Default to desktop for now
    automation_class = DesktopOpenProfile
    
    # Extract specific parameters
    duration = kwargs.get("duration")
    
    automation_args = {
        "account": account,
        "user_agent_type": account.type,
        "job_id": job_id
    }
    if duration is not None:
        automation_args["duration"] = duration
    
    automation = automation_class(**automation_args)

    return automation.execute()