# automations/gmx/report_not_spam/desktop/handlers.py
"""
State handlers for GMX Report Not Spam automation.
Each handler manages a specific unexpected page state.
"""
from playwright.sync_api import Page
from core.flow_engine.state_handler import StateHandler, HandlerAction
from core.utils.browser_utils import navigate_to


class UnknownPageHandler(StateHandler):
    """
    Handle unknown/unexpected pages by redirecting to inbox.
    Used when page identification fails or page is not recognized.
    """
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            if self.logger:
                self.logger.warning(f"Unknown page detected at: {page.url}")
                self.logger.info("Redirecting to inbox...")
            
            navigate_to(page, "https://www.gmx.net/mail/client/inbox")
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(2000)
            
            if self.logger:
                self.logger.info("Successfully redirected to inbox")
            
            return "retry"  # Retry the current step after redirecting
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to handle unknown page: {e}")
            return "abort"


    """
    Handle access denied or permission error pages.
    Usually indicates account issues.
    """
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            if self.logger:
                self.logger.error("Access denied page detected")
                self.logger.error("Account may be locked, suspended, or have insufficient permissions")
            
            # This is typically not recoverable automatically
            return "abort"
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to handle access denied page: {e}")
            return "abort"