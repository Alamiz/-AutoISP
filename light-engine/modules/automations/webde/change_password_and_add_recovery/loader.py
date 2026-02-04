from .desktop.run import ChangePasswordAndAddRecovery as DesktopChangePasswordAndAddRecovery

def run(account, job_id=None, **kwargs):
    """
    Selects the right platform (desktop/mobile) and runs the automation.
    NOTE: Mobile version is deprecated, forcing desktop version.
    """
    automation_class = DesktopChangePasswordAndAddRecovery
    
    log_dir = kwargs.get("log_dir")
    
    # Always force desktop user agent
    automation = automation_class(
        account=account,
        user_agent_type="desktop",
        job_id=job_id,
        log_dir=log_dir
    )

    return automation.execute()