from .desktop.run import ReportNotSpam as DesktopReportNotSpam
from .mobile.run import ReportNotSpam as MobileReportNotSpam

async def run(account, job_id=None, **kwargs):
    """
    Loader for Report Not Spam automation.
    Selects mobile or desktop implementation based on account type.
    """
    
    # Simple factory logic
    # Assuming account object has a 'type' or similar attribute, or passed in kwargs
    # For now defaulting to desktop if not mobile
    
    automation_class = MobileReportNotSpam if account.type == "mobile" else DesktopReportNotSpam
    
    automation = automation_class(account, job_id=job_id, **kwargs)
    return await automation.execute()