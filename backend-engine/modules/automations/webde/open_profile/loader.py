from .desktop.run import OpenProfile as DesktopOpenProfile

def run(email, password, device_type="desktop", proxy_config=None, **kwargs):
    """
    Selects the right platform (desktop/mobile) and runs the automation.
    """
    # Default to desktop for now
    automation_class = DesktopOpenProfile
    
    # Extract specific parameters
    duration = kwargs.get("duration")
    
    automation = automation_class(
        email=email, 
        password=password, 
        proxy_config=proxy_config, 
        user_agent_type=device_type,
        duration=duration
    )

    return automation.execute()
