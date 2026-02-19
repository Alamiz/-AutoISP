from .desktop.run import ReportNotSpam as DesktopReportNotSpam
from .mobile.run import ReportNotSpam as MobileReportNotSpam

async def run(account, job_id=None, log_dir=None, logger=None, **kwargs):
    """
    Loader for Report Not Spam automation.
    Selects mobile or desktop implementation based on account type.
    """
    
    automation_class = MobileReportNotSpam if account.type == "mobile" else DesktopReportNotSpam
    
    # Pass through logging info to automation class
    automation = automation_class(
        account, 
        job_id=job_id, 
        log_dir=log_dir, 
        **kwargs
    )
    
    # If a dynamic logger was provided, override the default one
    if logger:
        automation.logger = logger
        
    return await automation.execute()