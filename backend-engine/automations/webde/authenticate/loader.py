# automations/webde/authenticate/loader.py
from .desktop.run import WebdeAuthentication as DesktopAuth
from .mobile.run import WebdeAuthentication as MobileAuth
from ..signatures import desktop as desktop_signatures, mobile as mobile_signatures

def run(email, password, device_type="desktop", proxy_config=None):
    """
    Selects the right platform (desktop/mobile) and runs the automation.
    """
    signatures = mobile_signatures if device_type == "mobile" else desktop_signatures
    auth_class = MobileAuth if device_type == "mobile" else DesktopAuth

    automation = auth_class(email=email, password=password, proxy_config=proxy_config, user_agent_type=device_type)

    # Inject platform-specific signatures
    automation.signatures = signatures.PAGE_SIGNATURES

    return automation.execute()
