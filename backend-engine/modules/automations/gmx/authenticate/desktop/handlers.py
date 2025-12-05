# automations/gmx/authenticate/desktop/handlers.py
"""
State handlers for GMX Authentication using StatefulFlow.
Each handler manages a specific page state during authentication.
"""
import logging
from playwright.sync_api import Page
from core.flow_engine.state_handler import StateHandler, HandlerAction
from core.humanization.actions import HumanAction


class LoginPageHandler(StateHandler):
    """Handle GMX login page - enter credentials"""
    
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
                selectors=['input#username'],
                text=self.email,
                deep_search=True
            )
            
            # Click continue
            self.human_action.human_click(
                page,
                selectors=['button[type="submit"][data-testid="button-continue"]'],
                deep_search=True
            )
            
            # Fill password
            self.human_action.human_fill(
                page,
                selectors=['input#password'],
                text=self.password,
                deep_search=True
            )
            
            # Click submit
            self.human_action.human_click(
                page,
                selectors=['button[type="submit"][data-testid="button-submit"]'],
                deep_search=True
            )
            
            page.wait_for_timeout(2000)
            if self.logger:
                self.logger.info("LoginPageHandler: Credentials submitted")
            
            return "continue"
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"LoginPageHandler: Failed - {e}")
            return "abort"


class LoggedInPageHandler(StateHandler):
    """Handle already authenticated page - click continue"""
    
    def __init__(self, human_action: HumanAction, logger=None):
        super().__init__(logger)
        self.human_action = human_action
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            if self.logger:
                self.logger.info("LoggedInPageHandler: Clicking continue")
            
            self.human_action.human_click(
                page,
                selectors=["button[data-component-path='openInbox.continue-button']"],
                deep_search=True
            )
            
            page.wait_for_timeout(10_000)
            return "continue"
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"LoggedInPageHandler: Failed - {e}")
            return "abort"


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


class SmartFeaturesPopupHandler(StateHandler):
    """Handle smart features popup"""
    
    def __init__(self, human_action: HumanAction, logger=None):
        super().__init__(logger)
        self.human_action = human_action
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            if self.logger:
                self.logger.info("SmartFeaturesPopupHandler: Accepting")
            
            self.human_action.human_click(
                page,
                selectors=['button[data-component-path="acceptall-button"]'],
                deep_search=True
            )
            page.wait_for_timeout(1500)
            page.reload()
            return "continue"
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"SmartFeaturesPopupHandler: Failed - {e}")
            return "retry"


class UnknownPageHandler(StateHandler):
    """Handle unknown pages - redirect to GMX"""
    
    def __init__(self, human_action: HumanAction, logger=None):
        super().__init__(logger)
        self.human_action = human_action
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            if self.logger:
                self.logger.warning("UnknownPageHandler: Redirecting to GMX")
            
            page.goto("https://www.gmx.net/")
            self.human_action.human_behavior.read_delay()
            return "retry"
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"UnknownPageHandler: Failed - {e}")
            return "abort"
