from .desktop.run import ReportNotSpam as DesktopReportNotSpam
from .mobile.run import ReportNotSpam as MobileReportNotSpam # Not implemented yet

def run(account, job_id=None, **kwargs):
    """
    Selects the right platform (desktop/mobile) and runs the automation.
    """
    automation_class = MobileReportNotSpam if account.type == "mobile" else DesktopReportNotSpam
    
    search_text = kwargs.get("keyword")
    start_date = kwargs.get("start_date")
    end_date = kwargs.get("end_date")
    log_dir = kwargs.get("log_dir")
    
    automation = automation_class(
        account=account,
        user_agent_type=account.type,
        search_text=search_text,
        start_date=start_date,
        end_date=end_date,
        job_id=job_id,
        log_dir=log_dir
    )

    return automation.execute()