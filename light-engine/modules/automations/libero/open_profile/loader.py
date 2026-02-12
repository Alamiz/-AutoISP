from .desktop.run import OpenProfile as DesktopAuth

def run(account, job_id=None, **kwargs):
    """
    Selects the right platform (desktop/mobile) and runs the automation.
    """
    # Simply use desktop implementation for now
    automation = DesktopAuth(
        account=account,
        user_agent_type=account.type,
        duration=kwargs.get("duration", 10),
        job_id=job_id
    )

    return automation.execute()
