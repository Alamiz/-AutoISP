# automations/webde/authenticate/desktop/handlers.py
"""
State handlers for web.de Desktop Authentication using StatefulFlow.
"""
import logging
from playwright.sync_api import Page
from core.flow_engine.state_handler import StateHandler, HandlerAction
from core.humanization.actions import HumanAction
from core.utils.element_finder import deep_find_elements
from core.utils.browser_utils import navigate_to

class LoginPageHandler(StateHandler):
    """Handle web.de login page - enter credentials"""
    
    def __init__(self, human_action: HumanAction, email: str, password: str, logger=None):
        super().__init__(logger)
        self.human_action = human_action
        self.email = email
        self.password = password
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            # Check if we are already at the password step (e.g. after captcha retry)
            # Use deep_find_elements because it's in an iframe
            password_elements = deep_find_elements(page, "input#password")
            password_field_visible = any(el.is_visible() for el in password_elements)

            if password_field_visible:
                self.logger.info("LoginPageHandler: Password field visible, skipping email entry")
                
                self.human_action.human_fill(
                    page, selectors=['input#password'], text=self.password, deep_search=True
                )
                self.human_action.human_click(
                    page, selectors=['button[type="submit"][data-testid="button-submit"]'], deep_search=True
                )
                
                page.wait_for_timeout(15_000)
                self.logger.info("LoginPageHandler: Credentials submitted (password only)")
                return "continue"

            self.logger.info("LoginPageHandler: Entering credentials")
            
            self.human_action.human_fill(
                page, selectors=['input#username'], text=self.email, deep_search=True
            )
            self.human_action.human_click(
                page, selectors=['button[type="submit"][data-testid="button-continue"]'], deep_search=True
            )
            
            # Check for captcha after clicking continue
            if len(deep_find_elements(page, "div[data-testid='captcha']")) > 0:
                return "continue"

            self.human_action.human_fill(
                page, selectors=['input#password'], text=self.password, deep_search=True
            )
            self.human_action.human_click(
                page, selectors=['button[type="submit"][data-testid="button-submit"]'], deep_search=True
            )
            
            page.wait_for_timeout(15_000)
            return "continue"
            
        except Exception as e:
            self.logger.error(f"LoginPageHandler: Failed - {e}")
            return "retry"

class LoggedInPageHandler(StateHandler):
    """Handle already authenticated page - click continue"""
    
    def __init__(self, human_action: HumanAction, logger=None):
        super().__init__(logger)
        self.human_action = human_action
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            self.logger.info("LoggedInPageHandler: Clicking continue")
            
            self.human_action.human_click(
                page, selectors=["button[data-component-path='openInbox.continue-button']"], deep_search=True
            )
            page.wait_for_timeout(15_000)
            return "continue"
            
        except Exception as e:
            self.logger.error(f"LoggedInPageHandler: Failed - {e}")
            return "retry"


class AdsPreferencesPopup1Handler(StateHandler):
    """Handle ads preferences popup type 1"""
    
    def __init__(self, human_action: HumanAction, logger=None):
        super().__init__(logger)
        self.human_action = human_action
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            self.logger.info("AdsPreferencesPopup1Handler: Accepting")
            
            self.human_action.human_click(page, selectors=["button#save-all-pur"], deep_search=True)
            page.wait_for_timeout(1500)
            return "continue"
            
        except Exception as e:
            self.logger.error(f"AdsPreferencesPopup1Handler: Failed - {e}")
            return "retry"


class AdsPreferencesPopup2Handler(StateHandler):
    """Handle ads preferences popup type 2"""
    
    def __init__(self, human_action: HumanAction, logger=None):
        super().__init__(logger)
        self.human_action = human_action
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            self.logger.info("AdsPreferencesPopup2Handler: Denying")
            
            self.human_action.human_click(page, selectors=["button#deny"], deep_search=True)
            page.wait_for_timeout(1500)
            return "continue"
            
        except Exception as e:
            self.logger.error(f"AdsPreferencesPopup2Handler: Failed - {e}")
            return "retry"


class SmartFeaturesPopupHandler(StateHandler):
    """Handle smart features popup"""
    
    def __init__(self, human_action: HumanAction, logger=None):
        super().__init__(logger)
        self.human_action = human_action
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            self.logger.info("SmartFeaturesPopupHandler: Accepting")
            
            self.human_action.human_click(
                page, selectors=['button[data-component-path="acceptall-button"]'], deep_search=True
            )
            page.wait_for_timeout(1500)
            page.reload()
            return "continue"
            
        except Exception as e:
            self.logger.error(f"SmartFeaturesPopupHandler: Failed - {e}")
            return "retry"

class UnknownPageHandler(StateHandler):
    """Handle unknown pages - redirect to web.de"""
    
    def __init__(self, human_action: HumanAction, logger=None):
        super().__init__(logger)
        self.human_action = human_action
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            self.logger.warning("UnknownPageHandler: Redirecting to web.de")
            
            navigate_to(page, "https://web.de/")
            self.human_action.human_behavior.read_delay()
            return "retry"
            
        except Exception as e:
            self.logger.error(f"UnknownPageHandler: Failed - {e}")
            return "retry"
