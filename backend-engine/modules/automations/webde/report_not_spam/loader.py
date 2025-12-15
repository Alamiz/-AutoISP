from .desktop.run import ReportNotSpam as DesktopReportNotSpam
from .mobile.run import ReportNotSpam as MobileReportNotSpam # Not implemented yet

def run(email, password, device_type="desktop", proxy_config=None, **kwargs):
    """
    Selects the right platform (desktop/mobile) and runs the automation.
    """
    # Default to desktop for now if mobile is not implemented
    automation_class = MobileReportNotSpam if device_type == "mobile" else DesktopReportNotSpam
    
    # Extract specific parameters
    search_text = kwargs.get("keyword")
    job_id = kwargs.get("job_id")
    
    automation = automation_class(
        email=email, 
        password=password, 
        proxy_config=proxy_config, 
        user_agent_type=device_type,
        search_text=search_text,
        job_id=job_id
    )

    return automation.execute()
