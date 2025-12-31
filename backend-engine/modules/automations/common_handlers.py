from playwright.sync_api import Page
from core.flow_engine.state_handler import StateHandler, HandlerAction
from crud.account import update_account_state

class CommonHandler(StateHandler):
    """Base class for common handlers that need account_id"""
    def __init__(self, account_id: int, logger=None):
        super().__init__(logger)
        self.account_id = account_id

class WrongPasswordPageHandler(CommonHandler):
    """Handle wrong password page"""
    def handle(self, page: Page = None) -> HandlerAction:
        if self.logger:
            self.logger.warning("WrongPasswordPageHandler: Wrong password detected")
        update_account_state(self.account_id, "wrong_password")
        return "abort"

class WrongEmailPageHandler(CommonHandler):
    """Handle wrong email page"""
    def handle(self, page: Page = None) -> HandlerAction:
        if self.logger:
            self.logger.warning("WrongEmailPageHandler: Wrong email detected")
        update_account_state(self.account_id, "wrong_username")
        return "abort"

class LoginNotPossiblePageHandler(CommonHandler):
    """Handle login not possible page"""
    def handle(self, page: Page = None) -> HandlerAction:
        if self.logger:
            self.logger.warning("LoginNotPossiblePageHandler: Login not possible detected")
        update_account_state(self.account_id, "error")
        return "abort"

class LoginCaptchaHandler(CommonHandler):
    """Handle login captcha"""
    def handle(self, page: Page = None) -> HandlerAction:
        from core.utils.element_finder import deep_find_elements
        import time

        if self.logger:
            self.logger.warning("LoginCaptchaHandler: Captcha detected. Waiting for user to solve...")
        
        update_account_state(self.account_id, "captcha")
        
        try:
            # Wait for up to 1440 seconds for the password input to appear
            start_time = time.time()
            timeout = 1440
            
            while time.time() - start_time < timeout:
                # Use deep_find_elements to search across all frames
                elements = deep_find_elements(page, "input#password")
                
                # Check if any found element is visible
                for element in elements:
                    if element.is_visible():
                        if self.logger:
                            self.logger.info("LoginCaptchaHandler: Captcha solved, password input detected.")
                        return "retry"
                
                # Wait a bit before checking again
                page.wait_for_timeout(1000)
            
            if self.logger:
                self.logger.error("LoginCaptchaHandler: Timeout waiting for captcha solution")
            return "abort"
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"LoginCaptchaHandler: Error waiting for captcha solution: {e}")
            return "abort"

class SecuritySuspensionHandler(CommonHandler):
    """Handle security suspension page"""
    def handle(self, page: Page = None) -> HandlerAction:
        if self.logger:
            self.logger.warning("SecuritySuspensionHandler: Account suspended")
        update_account_state(self.account_id, "suspended")
        return "abort"

class PhoneVerificationHandler(CommonHandler):
    """Handle phone verification page"""
    def handle(self, page: Page = None) -> HandlerAction:
        if self.logger:
            self.logger.warning("PhoneVerificationHandler: Phone verification required")
        update_account_state(self.account_id, "phone_verification")
        return "abort"
