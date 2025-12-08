# automations/gmx/authenticate/mobile/handlers.py
"""
State handlers for GMX Mobile Authentication using StatefulFlow.
"""
import logging
from playwright.sync_api import Page
from core.flow_engine.state_handler import StateHandler, HandlerAction
from core.humanization.actions import HumanAction


class RegisterPageHandler(StateHandler):
    """Handle GMX mobile register page - click login button"""
    
    def __init__(self, human_action: HumanAction, logger=None):
        super().__init__(logger)
        self.human_action = human_action
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            if self.logger:
                self.logger.info("RegisterPageHandler: Clicking login button")
            
            self.human_action.human_click(
                page,
                selectors=['form.login-link.login-mobile > button[type="submit"]'],
            )
            page.wait_for_timeout(2000)
            return "continue"
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"RegisterPageHandler: Failed - {e}")
            return "retry"


class LoginPageHandler(StateHandler):
    """Handle GMX mobile login page - enter credentials"""
    
    def __init__(self, human_action: HumanAction, email: str, password: str, logger=None):
        super().__init__(logger)
        self.human_action = human_action
        self.email = email
        self.password = password
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            if self.logger:
                self.logger.info("LoginPageHandler: Entering credentials")
            
            # Fill email
            self.human_action.human_fill(
                page,
                selectors=['form input#username'],
                text=self.email,
            )
            
            # Click continue
            self.human_action.human_click(
                page,
                selectors=['form button[type="submit"]'],
            )
            
            # Fill password
            self.human_action.human_fill(
                page,
                selectors=['form input#password'],
                text=self.password,
            )
            
            # Click submit
            self.human_action.human_click(
                page,
                selectors=['button[type="submit"][data-testid="button-next"]'],
            )
            
            page.wait_for_timeout(10_000)
            if self.logger:
                self.logger.info("LoginPageHandler: Credentials submitted")
            
            return "continue"
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"LoginPageHandler: Failed - {e}")
            return "retry"


class LoggedInPageHandler(StateHandler):
    """Handle GMX mobile logged in page - click continue to inbox"""
    
    def __init__(self, human_action: HumanAction, logger=None):
        super().__init__(logger)
        self.human_action = human_action
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            if self.logger:
                self.logger.info("LoggedInPageHandler: Clicking profile and continue")
            
            # Click profile avatar
            self.human_action.human_click(
                page,
                selectors=['div.login-wrapper  > account-avatar'],
            )
            page.wait_for_timeout(2000)
            
            # Click continue to inbox button
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
            if self.logger:
                self.logger.info("AdsPreferencesPopup1Handler: Accepting")
            
            self.human_action.human_click(
                page,
                selectors=["button#save-all-pur"],
                deep_search=True
            )
            page.wait_for_timeout(1500)
            return "continue"
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"AdsPreferencesPopup1Handler: Failed - {e}")
            return "retry"


class AdsPreferencesPopup2Handler(StateHandler):
    """Handle ads preferences popup type 2"""
    
    def __init__(self, human_action: HumanAction, logger=None):
        super().__init__(logger)
        self.human_action = human_action
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            if self.logger:
                self.logger.info("AdsPreferencesPopup2Handler: Denying")
            
            self.human_action.human_click(
                page,
                selectors=["button#deny"],
                deep_search=True
            )
            page.wait_for_timeout(1500)
            return "continue"
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"AdsPreferencesPopup2Handler: Failed - {e}")
            return "retry"


class UnknownPageHandler(StateHandler):
    """Handle unknown pages - redirect to GMX mobile"""
    
    def __init__(self, human_action: HumanAction, logger=None):
        super().__init__(logger)
        self.human_action = human_action
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            if self.logger:
                self.logger.warning("UnknownPageHandler: Redirecting to GMX mobile")
            
            page.goto("https://lightmailer-bs.gmx.net/")
            self.human_action.human_behavior.read_delay()
            return "retry"
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"UnknownPageHandler: Failed - {e}")
            return "retry"
