from .desktop.run import LiberoAuthentication as DesktopAuth
# from .mobile.run import LiberoAuthentication as MobileAuth

def run(account, job_id=None, **kwargs):
    """
    Selects the right platform (desktop/mobile) and runs the automation.
    """
    # automation_class = MobileAuth if account.type == "mobile" else DesktopAuth
    automation_class = DesktopAuth
    
    automation = automation_class(
        account=account,
        user_agent_type=account.type,
        job_id=job_id
    )

    return automation.execute()
