"""
State handlers for GMX Authentication using StatefulFlow.
Each handler manages a specific page state during authentication.
"""
from playwright.sync_api import Page
from core.flow_engine.state_handler import StateHandler, HandlerAction
from core.utils.element_finder import deep_find_elements
from core.utils.browser_utils import navigate_to

class LoginPageHandler(StateHandler):
    """Handle GMX login page - enter credentials"""
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            # Check if we are already at the password step (e.g. after captcha retry)
            # Use deep_find_elements because it's in an iframe
            password_elements = deep_find_elements(page, "input#password")
            password_field_visible = any(el.is_visible() for el in password_elements)

            if password_field_visible:
                self.logger.info("LoginPageHandler: Password field visible, skipping email entry", extra={"account_id": self.account.id})
                
                self.automation.human_fill(
                    page,
                    selectors=['input#password'],
                    text=self.account.password,
                    deep_search=True
                )
                
                self.automation.human_click(
                    page,
                    selectors=['button[type="submit"][data-testid="button-submit"]'],
                    deep_search=True
                )
                
                self.logger.info("LoginPageHandler: Credentials submitted (password only)", extra={"account_id": self.account.id})
                return "continue"

            self.logger.info("LoginPageHandler: Entering credentials", extra={"account_id": self.account.id})
            
            # Fill email
            self.automation.human_fill(
                page,
                selectors=['input#username'],
                text=self.account.email,
                deep_search=True
            )
            
            # Click continue
            self.automation.human_click(
                page,
                selectors=['button[type="submit"][data-testid="button-continue"]'],
                deep_search=True
            )

            # Check for captcha after clicking continue
            if len(deep_find_elements(page, "div[data-testid='captcha']")) > 0:
                return "continue"

            
            # Fill password
            self.automation.human_fill(
                page,
                selectors=['input#password'],
                text=self.account.password,
                deep_search=True
            )
            
            # Click submit
            self.automation.human_click(
                page,
                selectors=['button[type="submit"][data-testid="button-submit"]'],
                deep_search=True
            )
            
            self.logger.info("LoginPageHandler: Credentials submitted", extra={"account_id": self.account.id})
            
            return "continue"
            
        except Exception as e:
            self.logger.error(f"LoginPageHandler: Failed - {e}", extra={"account_id": self.account.id})
            return "retry"

class LoggedInPageHandler(StateHandler):
    """Handle already authenticated page - click continue"""
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            self.logger.info("LoggedInPageHandler: Clicking continue", extra={"account_id": self.account.id})
            
            self.automation.human_click(
                page,
                selectors=["button[data-component-path='openInbox.continue-button']"],
                deep_search=True
            )
            
            page.wait_for_timeout(10_000)
            return "continue"
            
        except Exception as e:
            self.logger.error(f"LoggedInPageHandler: Failed - {e}", extra={"account_id": self.account.id})
            return "retry"

class AdsPreferencesPopup1Handler(StateHandler):
    """Handle ads preferences popup type 1"""
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            self.logger.info("AdsPreferencesPopup1Handler: Accepting", extra={"account_id": self.account.id})
            
            self.automation.human_click(
                page,
                selectors=["button#save-all-pur"],
                deep_search=True
            )
            
            page.wait_for_timeout(1500)
            return "continue"
            
        except Exception as e:
            self.logger.error(f"AdsPreferencesPopup1Handler: Failed - {e}", extra={"account_id": self.account.id})
            return "retry"

class AdsPreferencesPopup2Handler(StateHandler):
    """Handle ads preferences popup type 2"""
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            self.logger.info("AdsPreferencesPopup2Handler: Denying", extra={"account_id": self.account.id})
            
            self.automation.human_click(
                page,
                selectors=["button#deny"],
                deep_search=True
            )
            
            page.wait_for_timeout(1500)
            return "continue"
            
        except Exception as e:
            self.logger.error(f"AdsPreferencesPopup2Handler: Failed - {e}", extra={"account_id": self.account.id})
            return "retry"

class SmartFeaturesPopupHandler(StateHandler):
    """Handle smart features popup"""
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            self.logger.info("SmartFeaturesPopupHandler: Accepting", extra={"account_id": self.account.id})
            
            self.automation.human_click(
                page,
                selectors=['button[data-component-path="acceptall-button"]'],
                deep_search=True
            )
            page.wait_for_timeout(1500)
            page.reload()
            return "continue"
            
        except Exception as e:
            self.logger.error(f"SmartFeaturesPopupHandler: Failed - {e}", extra={"account_id": self.account.id})
            return "retry"

class UnknownPageHandler(StateHandler):
    """Handle unknown pages - redirect to GMX"""
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            self.logger.warning("UnknownPageHandler: Redirecting to GMX", extra={"account_id": self.account.id})
            
            navigate_to(page, "https://www.gmx.net/")
            self.automation.human_behavior.read_delay()
            return "retry"
            
        except Exception as e:
            self.logger.error(f"UnknownPageHandler: Failed - {e}", extra={"account_id": self.account.id})
            return "retry"
