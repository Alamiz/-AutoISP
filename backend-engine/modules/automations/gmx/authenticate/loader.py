from .desktop.run import GMXAuthentication as DesktopAuth
from .mobile.run import GMXAuthentication as MobileAuth

def run(account_id, email, password, device_type="desktop", proxy_config=None, job_id=None, **kwargs):
    """
    Selects the right platform (desktop/mobile) and runs the automation.
    """
    automation_class = MobileAuth if device_type == "mobile" else DesktopAuth
    
    automation = automation_class(
        account_id=account_id,
        email=email, 
        password=password, 
        proxy_config=proxy_config, 
        user_agent_type=device_type,
        job_id=job_id
    )

    return automation.execute()
