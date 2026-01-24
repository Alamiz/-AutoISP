# automations/webde/authenticate/mobile/handlers.py
"""
State handlers for web.de Mobile Authentication using StatefulFlow.
"""
from playwright.sync_api import Page
from core.flow_engine.state_handler import StateHandler, HandlerAction
from core.humanization.actions import HumanAction
from core.utils.element_finder import deep_find_elements
from core.utils.browser_utils import navigate_to
from core.models import Account

class RegisterPageHandler(StateHandler):
    """Handle web.de mobile register page - click login button"""
    def handle(self, page: Page) -> HandlerAction:
        try:
            self.logger.info("RegisterPageHandler: Clicking login button", extra={"account_id": self.account.id})
            
            self.automation.human_click(
                page,
                selectors=['form.login-link.login-mobile > button[type="submit"]'],
            )
            page.wait_for_timeout(2000)
            return "continue"
            
        except Exception as e:
            self.logger.error(f"RegisterPageHandler: Failed - {e}", extra={"account_id": self.account.id})
            return "retry"


class LoginPageHandler(StateHandler):
    """Handle web.de mobile login page - enter credentials"""
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            # Check if we are already at the password step (e.g. after captcha retry)
            if page.is_visible('form input#password'):
                self.logger.info("LoginPageHandler: Password field visible, skipping email entry", extra={"account_id": self.account.id})
                
                self.automation.human_fill(
                    page,
                    selectors=['form input#password'],
                    text=self.account.password,
                )
                
                self.automation.human_click(
                    page,
                    selectors=['button[type="submit"][data-testid="button-next"]'],
                )
                
                page.wait_for_timeout(3_000)
                self.logger.info("LoginPageHandler: Credentials submitted (password only)", extra={"account_id": self.account.id})
                return "continue"

            self.logger.info("LoginPageHandler: Entering credentials", extra={"account_id": self.account.id})
            
            # Fill email
            self.automation.human_fill(
                page,
                selectors=['form input#username'],
                text=self.account.email,
            )
            
            # Click continue
            self.automation.human_click(
                page,
                selectors=['form button[type="submit"]'],
            )

            # Check if captcha is present
            captcha_elements = deep_find_elements(page, 'div[data-testid="captcha-container"]')
            if captcha_elements:
                return "continue"
            
            # Fill password
            self.automation.human_fill(
                page,
                selectors=['form input#password'],
                text=self.account.password,
            )
            
            # Click submit
            self.automation.human_click(
                page,
                selectors=['button[type="submit"][data-testid="button-next"]'],
            )
            
            page.wait_for_timeout(3_000)
            self.logger.info("LoginPageHandler: Credentials submitted", extra={"account_id": self.account.id})
            
            return "continue"
            
        except Exception as e:
            self.logger.error(f"LoginPageHandler: Failed - {e}", extra={"account_id": self.account.id})
            return "retry"

class LoggedInPageHandler(StateHandler):
    """Handle web.de mobile logged in page - click continue to inbox"""
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            self.logger.info("LoggedInPageHandler: Clicking profile and continue", extra={"account_id": self.account.id})
            
            # Click profile avatar
            self.automation.human_click(
                page,
                selectors=['div.login-wrapper  > account-avatar'],
            )
            page.wait_for_timeout(2000)
            
            # Click continue to inbox button
            self.automation.human_click(
                page,
                selectors=['div#appa-account-flyout > section.account-avatar__flyout-content > section.appa-account-avatar__buttons > button:nth-of-type(2)'],
                deep_search=True
            )
            page.wait_for_timeout(2000)
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

class UnknownPageHandler(StateHandler):
    """Handle unknown pages - redirect to web.de mobile"""
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            self.logger.warning("UnknownPageHandler: Redirecting to web.de mobile", extra={"account_id": self.account.id})
            
            navigate_to(page, "https://lightmailer-bs.web.de/")
            self.automation.human_behavior.read_delay()
            return "retry"
            
        except Exception as e:
            self.logger.error(f"UnknownPageHandler: Failed - {e}", extra={"account_id": self.account.id})
            return "retry"
