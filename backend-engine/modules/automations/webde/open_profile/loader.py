from .desktop.run import OpenProfile as DesktopOpenProfile

def run(account, job_id=None, **kwargs):
    """
    Selects the right platform (desktop/mobile) and runs the automation.
    """
    # Default to desktop for now
    automation_class = DesktopOpenProfile
    
    # Extract specific parameters
    duration = kwargs.get("duration")
    
    automation = automation_class(
        account=account,
        user_agent_type=account.type,
        duration=duration,
        job_id=job_id
    )

    return automation.execute()
