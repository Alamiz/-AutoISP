# automations/gmx/report_not_spam/desktop/handlers.py
"""
State handlers for GMX Report Not Spam automation.
Each handler manages a specific unexpected page state.
"""
from playwright.sync_api import Page
from core.flow_engine.state_handler import StateHandler, HandlerAction


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
            
            page.goto("https://www.gmx.net/mail/client/inbox")
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(2000)
            
            if self.logger:
                self.logger.info("Successfully redirected to inbox")
            
            return "retry"  # Retry the current step after redirecting
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to handle unknown page: {e}")
            return "abort"


class LoginRequiredHandler(StateHandler):
    """
    Handle cases where user is logged out or session expired.
    This aborts the flow since re-authentication is required.
    """
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            if self.logger:
                self.logger.error("Login page detected - session expired or not authenticated")
                self.logger.error("Flow cannot continue without valid session")
            
            # Abort the flow - requires fresh authentication
            return "abort"
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to handle login page: {e}")
            return "abort"


class CaptchaPageHandler(StateHandler):
    """
    Handle CAPTCHA challenges.
    Currently aborts flow - can be extended to integrate CAPTCHA solving services.
    """
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            if self.logger:
                self.logger.error("CAPTCHA detected - cannot proceed automatically")
                self.logger.error("Consider implementing CAPTCHA solving service or manual intervention")
            
            # TODO: Integrate CAPTCHA solving service here if needed
            # Example: 2captcha, anti-captcha, etc.
            
            return "abort"
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to handle CAPTCHA page: {e}")
            return "abort"


class ErrorPageHandler(StateHandler):
    """
    Handle GMX error pages with smart recovery.
    Attempts to return to inbox with a maximum retry limit to prevent infinite loops.
    """
    
    def __init__(self, max_redirects=3, logger=None):
        super().__init__(logger)
        self.redirect_count = 0
        self.max_redirects = max_redirects
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            self.redirect_count += 1
            
            if self.redirect_count > self.max_redirects:
                if self.logger:
                    self.logger.error(
                        f"Max redirects ({self.max_redirects}) exceeded for error page. "
                        "Persistent error state detected."
                    )
                return "abort"
            
            if self.logger:
                self.logger.warning(
                    f"Error page detected (attempt {self.redirect_count}/{self.max_redirects})"
                )
                self.logger.info("Attempting to recover by returning to inbox...")
            
            # Try to recover by going back to inbox
            page.goto("https://www.gmx.net/mail/client/inbox")
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(2000)
            
            if self.logger:
                self.logger.info("Recovery attempt complete, retrying step")
            
            return "retry"
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to handle error page: {e}")
            return "abort"


class RateLimitHandler(StateHandler):
    """
    Handle rate limiting scenarios.
    Waits for specified time before allowing retry.
    """
    
    def __init__(self, wait_time=30000, max_attempts=3, logger=None):
        super().__init__(logger)
        self.wait_time = wait_time
        self.max_attempts = max_attempts
        self.attempt_count = 0
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            self.attempt_count += 1
            
            if self.attempt_count > self.max_attempts:
                if self.logger:
                    self.logger.error(
                        f"Max rate limit attempts ({self.max_attempts}) exceeded. "
                        "Account may be temporarily blocked."
                    )
                return "abort"
            
            if self.logger:
                self.logger.warning(
                    f"Rate limit detected (attempt {self.attempt_count}/{self.max_attempts}). "
                    f"Waiting {self.wait_time/1000}s before retry..."
                )
            
            page.wait_for_timeout(self.wait_time)
            
            if self.logger:
                self.logger.info("Wait complete. Retrying step...")
            
            return "retry"
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to handle rate limit: {e}")
            return "abort"


class MaintenancePageHandler(StateHandler):
    """
    Handle maintenance or downtime pages.
    Waits longer and has fewer retry attempts.
    """
    
    def __init__(self, wait_time=60000, max_attempts=2, logger=None):
        super().__init__(logger)
        self.wait_time = wait_time
        self.max_attempts = max_attempts
        self.attempt_count = 0
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            self.attempt_count += 1
            
            if self.attempt_count > self.max_attempts:
                if self.logger:
                    self.logger.error(
                        f"Service appears to be down after {self.max_attempts} attempts. "
                        "Try again later."
                    )
                return "abort"
            
            if self.logger:
                self.logger.warning(
                    f"Maintenance page detected (attempt {self.attempt_count}/{self.max_attempts})"
                )
                self.logger.info(f"Waiting {self.wait_time/1000}s for service to recover...")
            
            page.wait_for_timeout(self.wait_time)
            
            # Try refreshing the page
            page.reload()
            page.wait_for_load_state("domcontentloaded")
            
            return "retry"
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to handle maintenance page: {e}")
            return "abort"


class SessionTimeoutHandler(StateHandler):
    """
    Handle session timeout with automatic re-navigation.
    Different from login page - session exists but timed out.
    """
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            if self.logger:
                self.logger.warning("Session timeout detected")
                self.logger.info("Attempting to refresh session by navigating to inbox...")
            
            # Try to refresh the session
            page.goto("https://www.gmx.net/mail/client/inbox")
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(2000)
            
            # Check if we're still on a login page
            if "login" in page.url.lower():
                if self.logger:
                    self.logger.error("Session refresh failed - full re-authentication needed")
                return "abort"
            
            if self.logger:
                self.logger.info("Session refreshed successfully")
            
            return "retry"
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to handle session timeout: {e}")
            return "abort"


class NetworkErrorHandler(StateHandler):
    """
    Handle network connectivity issues.
    Waits and retries with exponential backoff.
    """
    
    def __init__(self, base_wait=5000, max_attempts=3, logger=None):
        super().__init__(logger)
        self.base_wait = base_wait
        self.max_attempts = max_attempts
        self.attempt_count = 0
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            self.attempt_count += 1
            
            if self.attempt_count > self.max_attempts:
                if self.logger:
                    self.logger.error("Network error persists after multiple attempts")
                return "abort"
            
            # Exponential backoff
            wait_time = self.base_wait * (2 ** (self.attempt_count - 1))
            
            if self.logger:
                self.logger.warning(
                    f"Network error detected (attempt {self.attempt_count}/{self.max_attempts})"
                )
                self.logger.info(f"Waiting {wait_time/1000}s before retry...")
            
            page.wait_for_timeout(wait_time)
            
            # Try reloading the page
            try:
                page.reload()
                page.wait_for_load_state("domcontentloaded", timeout=30000)
            except Exception:
                if self.logger:
                    self.logger.warning("Page reload failed, will retry step anyway")
            
            return "retry"
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to handle network error: {e}")
            return "abort"


class AccessDeniedHandler(StateHandler):
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