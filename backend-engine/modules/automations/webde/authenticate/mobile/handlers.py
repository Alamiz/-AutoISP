# automations/webde/authenticate/mobile/handlers.py
"""
State handlers for web.de Mobile Authentication using StatefulFlow.
"""
from playwright.sync_api import Page
from core.flow_engine.state_handler import StateHandler, HandlerAction
from core.humanization.actions import HumanAction
from core.utils.element_finder import deep_find_elements


class RegisterPageHandler(StateHandler):
    """Handle web.de mobile register page - click login button"""
    
    def __init__(self, human_action: HumanAction, logger=None):
        super().__init__(logger)
        self.human_action = human_action
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            if self.logger:
                self.logger.info("RegisterPageHandler: Clicking login button")
            
            self.human_action.human_click(
                page, selectors=['form.login-link.login-mobile > button[type="submit"]']
            )
            page.wait_for_timeout(2000)
            return "continue"
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"RegisterPageHandler: Failed - {e}")
            return "retry"


class LoginPageHandler(StateHandler):
    """Handle web.de mobile login page - enter credentials"""
    
    def __init__(self, human_action: HumanAction, email: str, password: str, logger=None):
        super().__init__(logger)
        self.human_action = human_action
        self.email = email
        self.password = password
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            if self.logger:
                self.logger.info("LoginPageHandler: Entering credentials")
            
            self.human_action.human_fill(page, selectors=['form input#username'], text=self.email)
            self.human_action.human_click(page, selectors=['form button[type="submit"]'])
            page.wait_for_timeout(2000)

            
            # Check if captcha is present
            captcha_elements = deep_find_elements(page, 'div[data-testid="captcha-container"]')
            if captcha_elements:
                if self.logger:
                    self.logger.error("LoginPageHandler: Captcha detected")
                return "abort"

            self.human_action.human_fill(page, selectors=['form input#password'], text=self.password)
            self.human_action.human_click(page, selectors=['button[type="submit"][data-testid="button-next"]'])
            
            page.wait_for_timeout(10_000)
            return "continue"
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"LoginPageHandler: Failed - {e}")
            return "retry"

class LoginCaptchaPageHandler(StateHandler):
    """Handle web.de mobile login captcha page"""
    
    def __init__(self, human_action: HumanAction, logger=None):
        super().__init__(logger)
        self.human_action = human_action
    
    def handle(self, page: Page) -> HandlerAction:
        self.logger.error("LoginCaptchaPageHandler: Captcha detected")
        return "abort"

class LoggedInPageHandler(StateHandler):
    """Handle web.de mobile logged in page - click continue to inbox"""
    
    def __init__(self, human_action: HumanAction, logger=None):
        super().__init__(logger)
        self.human_action = human_action
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            if self.logger:
                self.logger.info("LoggedInPageHandler: Clicking profile and continue")
            
            self.human_action.human_click(page, selectors=['div.login-wrapper  > account-avatar'])
            page.wait_for_timeout(2000)
            self.human_action.human_click(
                page, 
                selectors=['div#appa-account-flyout > section.account-avatar__flyout-content > section.appa-account-avatar__buttons > button:nth-of-type(2)'],
                deep_search=True
            )
            page.wait_for_timeout(2000)
            return "continue"
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"LoggedInPageHandler: Failed - {e}")
            return "retry"


class AdsPreferencesPopup1Handler(StateHandler):
    """Handle ads preferences popup type 1"""
    
    def __init__(self, human_action: HumanAction, logger=None):
        super().__init__(logger)
        self.human_action = human_action
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            self.human_action.human_click(page, selectors=["button#save-all-pur"], deep_search=True)
            page.wait_for_timeout(1500)
            return "continue"
        except Exception as e:
            return "retry"


class AdsPreferencesPopup2Handler(StateHandler):
    """Handle ads preferences popup type 2"""
    
    def __init__(self, human_action: HumanAction, logger=None):
        super().__init__(logger)
        self.human_action = human_action
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            self.human_action.human_click(page, selectors=["button#deny"], deep_search=True)
            page.wait_for_timeout(1500)
            return "continue"
        except Exception as e:
            return "retry"

class SecuritySuspensionHandler(StateHandler):
    """Handle security suspension page"""
    
    def __init__(self, human_action: HumanAction, logger=None):
        super().__init__(logger)
        self.human_action = human_action
    
    def handle(self, page: Page) -> HandlerAction:
        return "abort"

class UnknownPageHandler(StateHandler):
    """Handle unknown pages - redirect to web.de mobile"""
    
    def __init__(self, human_action: HumanAction, logger=None):
        super().__init__(logger)
        self.human_action = human_action
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            page.goto("https://lightmailer-bs.web.de/")
            self.human_action.human_behavior.read_delay()
            return "retry"
        except Exception as e:
            return "retry"
