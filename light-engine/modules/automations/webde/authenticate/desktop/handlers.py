# automations/webde/authenticate/desktop/handlers.py
"""
State handlers for web.de Desktop Authentication using StatefulFlow.
"""
import logging
import time
from playwright.sync_api import Page
from core.flow_engine.state_handler import StateHandler, HandlerAction
from core.utils.element_finder import deep_find_elements
from core.utils.browser_utils import navigate_to

class LoginPageHandler(StateHandler):
    """Handle web.de login page - enter credentials"""

    def handle(self, page: Page) -> HandlerAction:
        try:
            # Check if we are already at the password step (e.g. after captcha retry)
            # Use deep_find_elements because it's in an iframe
            password_elements = deep_find_elements(page, "input#password", timeout_ms=2000)
            password_field_visible = any(el.is_visible() for el in password_elements)

            if password_field_visible:
                self.logger.info("Password field visible, skipping email entry", extra={"account_id": self.account.id})
                
                start_time = time.perf_counter()
                self.automation.human_fill(
                    page, selectors=['input#password'], text=self.account.password, deep_search=True
                )
                self.automation.human_click(
                    page, selectors=['button[type="submit"][data-testid="button-submit"]'], deep_search=True
                )
                
                duration = time.perf_counter() - start_time
                self.logger.info(f"Password submitted: {duration:.2f} seconds", extra={"account_id": self.account.id})

                page.wait_for_selector("header.navigator__brand-logo-appname") # Wait for inbox page to load
                return "continue"

            self.logger.info("Entering credentials", extra={"account_id": self.account.id})
            
            start_time = time.perf_counter()
            self.automation.human_fill(
                page, selectors=['input#username'], text=self.account.email, deep_search=True
            )
            self.automation.human_click(
                page, selectors=['button[type="submit"][data-testid="button-continue"]'], deep_search=True
            )
            
            duration = time.perf_counter() - start_time
            self.logger.info(f"Email submitted: {duration:.2f} seconds", extra={"account_id": self.account.id})
            
            # Check for captcha after clicking continue
            start_time = time.perf_counter()
            captcha_elements = deep_find_elements(page, "div[data-testid='captcha']", timeout_ms=8000)
            if len(captcha_elements) > 0:
                duration = time.perf_counter() - start_time
                self.logger.info(f"Captcha check took: {duration:.2f} seconds", extra={"account_id": self.account.id})
                return "continue"

            start_time = time.perf_counter()
            self.automation.human_fill(
                page, selectors=['input#password'], text=self.account.password, deep_search=True
            )
            self.automation.human_click(
                page, selectors=['button[type="submit"][data-testid="button-submit"]'], deep_search=True
            )
            
            duration = time.perf_counter() - start_time
            self.logger.info(f"Password submitted: {duration:.2f} seconds", extra={"account_id": self.account.id})
            
            page.wait_for_selector("header.navigator__brand-logo-appname") # Wait for inbox page to load
            return "continue"
            
        except Exception as e:
            self.logger.error(f"Failed - {e}", extra={"account_id": self.account.id})
            return "retry"

class LoggedInPageHandler(StateHandler):
    """Handle already authenticated page - click continue"""

    def handle(self, page: Page) -> HandlerAction:
        try:
            self.logger.info("Clicking continue", extra={"account_id": self.account.id})
            
            start_time = time.perf_counter()
            self.automation.human_click(
                page, selectors=["button[data-component-path='openInbox.continue-button']"], deep_search=True
            )
            
            duration = time.perf_counter() - start_time
            self.logger.info(f"Continue clicked: {duration:.2f} seconds", extra={"account_id": self.account.id})
            
            page.wait_for_selector("header.navigator__brand-logo-appname") # Wait for inbox page to load
            return "continue"
            
        except Exception as e:
            self.logger.error(f"Failed - {e}", extra={"account_id": self.account.id})
            return "retry"


class AdsPreferencesPopup1Handler(StateHandler):
    """Handle ads preferences popup type 1"""

    def handle(self, page: Page) -> HandlerAction:
        try:
            self.logger.info("Accepting ads preferences popup", extra={"account_id": self.account.id})
            
            start_time = time.perf_counter()
            self.automation.human_click(page, selectors=["button#save-all-pur"], deep_search=True)
            
            duration = time.perf_counter() - start_time
            self.logger.info(f"Ads preferences popup accepted: {duration:.2f} seconds", extra={"account_id": self.account.id})
            
            page.wait_for_timeout(1500)
            return "continue"
            
        except Exception as e:
            self.logger.error(f"Failed - {e}", extra={"account_id": self.account.id})
            return "retry"


class AdsPreferencesPopup2Handler(StateHandler):
    """Handle ads preferences popup type 2"""

    def handle(self, page: Page) -> HandlerAction:
        try:
            self.logger.info("Denying ads preferences popup", extra={"account_id": self.account.id})
            
            start_time = time.perf_counter()
            self.automation.human_click(page, selectors=["button#deny"], deep_search=True)
            
            duration = time.perf_counter() - start_time
            self.logger.info(f"Ads preferences popup denied: {duration:.2f} seconds", extra={"account_id": self.account.id})
            
            page.wait_for_timeout(1500)
            return "continue"
            
        except Exception as e:
            self.logger.error(f"Failed - {e}", extra={"account_id": self.account.id})
            return "retry"


class SmartFeaturesPopupHandler(StateHandler):
    """Handle smart features popup"""
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            self.logger.info("Accepting smart features popup", extra={"account_id": self.account.id})
            
            start_time = time.perf_counter()
            self.automation.human_click(
                page, selectors=['button[data-component-path="accept-button"]'], deep_search=True
            )
            
            duration = time.perf_counter() - start_time
            self.logger.info(f"Smart features popup accepted: {duration:.2f} seconds", extra={"account_id": self.account.id})
            
            page.wait_for_timeout(1500)
            page.reload()
            return "continue"
            
        except Exception as e:
            self.logger.error(f"Failed - {e}", extra={"account_id": self.account.id})
            return "retry"

class UnknownPageHandler(StateHandler):
    """Handle unknown pages - redirect to web.de"""
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            self.logger.warning("Redirecting to web.de", extra={"account_id": self.account.id})
            
            navigate_to(page, "https://web.de/")
            self.automation.human_behavior.read_delay()
            return "retry"
            
        except Exception as e:
            self.logger.error(f"Failed - {e}", extra={"account_id": self.account.id})
            return "retry"