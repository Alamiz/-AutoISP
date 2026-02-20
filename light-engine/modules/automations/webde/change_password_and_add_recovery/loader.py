import asyncio

from .desktop.run import ChangePasswordAndAddRecovery as DesktopChangePasswordAndAddRecovery

async def run(account, job_id=None, log_dir=None, logger=None, **kwargs):
    """
    Selects the right platform (desktop/mobile) and runs the automation.
    NOTE: Mobile version is deprecated, forcing desktop version.
    """
    automation_class = DesktopChangePasswordAndAddRecovery
    
    # Always force desktop user agent
    automation = automation_class(
        account=account,
        user_agent_type="desktop",
        job_id=job_id,
        log_dir=log_dir
    )

    # If a dynamic logger was provided, override the default one
    if logger:
        automation.logger = logger

    # Run sync execution in a thread to avoid blocking the event loop
    return await automation.execute()