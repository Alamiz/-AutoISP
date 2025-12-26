from .desktop.run import ReportNotSpam as DesktopReportNotSpam
from .mobile.run import ReportNotSpam as MobileReportNotSpam # Not implemented yet

def run(account_id, email, password, device_type="desktop", proxy_config=None, job_id=None, **kwargs):
    """
    Selects the right platform (desktop/mobile) and runs the automation.
    """
    automation_class = MobileReportNotSpam if device_type == "mobile" else DesktopReportNotSpam
    
    search_text = kwargs.get("keyword")
    start_date = kwargs.get("start_date")
    end_date = kwargs.get("end_date")
    
    automation = automation_class(
        account_id=account_id,
        email=email, 
        password=password, 
        proxy_config=proxy_config, 
        user_agent_type=device_type,
        search_text=search_text,
        start_date=start_date,
        end_date=end_date,
        job_id=job_id
    )

    return automation.execute()
