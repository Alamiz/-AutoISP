"""
State handlers for GMX Authentication using StatefulFlow.
Each handler manages a specific page state during authentication.
"""
import time
from playwright.sync_api import Page
from core.flow_engine.state_handler import StateHandler
from modules.core.flow_state import FlowResult
from core.utils.element_finder import deep_find_elements
from core.utils.browser_utils import navigate_to

class OnboardingPageHandler(StateHandler):
    """Handle GMX onboarding page"""
    
    def handle(self, page: Page) -> FlowResult:
        try:
            self.logger.info("Clicking deny", extra={"account_id": self.account.id})
            start_time = time.perf_counter()
            self.automation.human_click(
                page,
                selectors=["button[data-importance='secondary']"],
                deep_search=False
            )

            duration = time.perf_counter() - start_time
            self.logger.info(f"Deny clicked: {duration:.2f} seconds", extra={"account_id": self.account.id})
            
            page.wait_for_timeout(1500)
            return FlowResult.SUCCESS
            
        except Exception as e:
            self.logger.error(f"Failed - {e}", extra={"account_id": self.account.id})
            return FlowResult.RETRY

class LoginPageHandler(StateHandler):
    """Handle GMX login page - enter credentials"""
    
    def handle(self, page: Page) -> FlowResult:
        try:
            # Check if we are already at the password step (e.g. after captcha retry)
            # Use deep_find_elements because it's in an iframe
            password_elements = deep_find_elements(page, "input#password")
            password_field_visible = any(el.is_visible() for el in password_elements)

            if password_field_visible:
                self.logger.info("Password field visible, skipping email entry", extra={"account_id": self.account.id})
                
                start_time = time.perf_counter()
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
                
                duration = time.perf_counter() - start_time
                self.logger.info(f"Password submitted: {duration:.2f} seconds", extra={"account_id": self.account.id})
                return FlowResult.SUCCESS

            self.logger.info("Entering credentials", extra={"account_id": self.account.id})
            
            start_time = time.perf_counter()
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
            duration = time.perf_counter() - start_time
            self.logger.info(f"Email submitted: {duration:.2f} seconds", extra={"account_id": self.account.id})

            self.logger.info("Checking for captcha", extra={"account_id": self.account.id})
            # Check for captcha after clicking continue
            start_time = time.perf_counter()
            captcha_elements = deep_find_elements(page, "div[data-testid='captcha']")
            if len(captcha_elements) > 0:
                duration = time.perf_counter() - start_time
                self.logger.info(f"Captcha check took: {duration:.2f} seconds", extra={"account_id": self.account.id})
                return FlowResult.SUCCESS
            
            start_time = time.perf_counter()
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
            duration = time.perf_counter() - start_time
            self.logger.info(f"Password submitted: {duration:.2f} seconds", extra={"account_id": self.account.id})
            
            return FlowResult.SUCCESS
            
        except Exception as e:
            self.logger.error(f"Failed - {e}", extra={"account_id": self.account.id})
            return FlowResult.RETRY

class LoginPageV2Handler(StateHandler):
    """Handle GMX login page v2 - split email and password entry"""
    
    def handle(self, page: Page) -> FlowResult:
        try:
            # Check if we are already at the password step
            password_field_visible = False
            try:
                page.wait_for_selector('input[name="password"]', state="visible", timeout=2000)
                password_field_visible = True
            except:
                pass

            if password_field_visible:
                self.logger.info("Password field visible, skipping email entry", extra={"account_id": self.account.id})
                
                start_time = time.perf_counter()
                self.automation.human_fill(
                    page,
                    selectors=['input[name="password"]'],
                    text=self.account.password,
                    deep_search=False
                )
                
                self.automation.human_click(
                    page,
                    selectors=['button[type="submit"]'],
                    deep_search=False
                )
                
                duration = time.perf_counter() - start_time
                self.logger.info(f"Password submitted: {duration:.2f} seconds", extra={"account_id": self.account.id})
                return FlowResult.SUCCESS

            self.logger.info("Entering credentials (V2 flow)", extra={"account_id": self.account.id})
            
            start_time = time.perf_counter()
            # Fill email
            self.automation.human_fill(
                page,
                selectors=['input[name="username"]'],
                text=self.account.email,
                deep_search=False
            )
            
            # Click continue
            self.automation.human_click(
                page,
                selectors=['button[type="submit"]'],
                deep_search=False
            )
            duration = time.perf_counter() - start_time
            self.logger.info(f"Email submitted: {duration:.2f} seconds", extra={"account_id": self.account.id})

            self.logger.info("Checking for captcha", extra={"account_id": self.account.id})
            # Check for captcha after clicking continue
            start_time = time.perf_counter()
            captcha_found = False
            for selector in ["div[data-testid='captcha']", "div[data-testid='captcha-container']"]:
                try:
                    page.wait_for_selector(selector, state="attached", timeout=1000)
                    captcha_found = True
                    break
                except:
                    continue
            
            if captcha_found:
                duration = time.perf_counter() - start_time
                self.logger.info(f"Captcha detected: {duration:.2f} seconds", extra={"account_id": self.account.id})
                return FlowResult.SUCCESS
            
            # If no captcha, wait for password field to appear and fill it
            try:
                page.wait_for_selector('input[name="password"]', timeout=10000)
                
                start_time = time.perf_counter()
                self.automation.human_fill(
                    page,
                    selectors=['input[name="password"]'],
                    text=self.account.password,
                    deep_search=False
                )
                
                self.automation.human_click(
                    page,
                    selectors=['button[type="submit"]'],
                    deep_search=False
                )
                duration = time.perf_counter() - start_time
                self.logger.info(f"Password submitted: {duration:.2f} seconds", extra={"account_id": self.account.id})
            except Exception as e:
                self.logger.info(f"Password field did not appear immediately: {e}. Re-identifying status.", extra={"account_id": self.account.id})
            
            return FlowResult.SUCCESS
            
        except Exception as e:
            self.logger.error(f"Failed LoginPageV2Handler - {e}", extra={"account_id": self.account.id})
            return FlowResult.RETRY

class LoggedInPageHandler(StateHandler):
    """Handle already authenticated page - click continue"""
    
    def handle(self, page: Page) -> FlowResult:
        try:
            self.logger.info("Clicking continue", extra={"account_id": self.account.id})
            start_time = time.perf_counter()
            self.automation.human_click(
                page,
                selectors=["button[data-component-path='openInbox.continue-button']"],
                deep_search=True
            )

            duration = time.perf_counter() - start_time
            self.logger.info(f"Continue clicked: {duration:.2f} seconds", extra={"account_id": self.account.id})
            
            page.wait_for_timeout(10_000)
            return FlowResult.SUCCESS
            
        except Exception as e:
            self.logger.error(f"Failed - {e}", extra={"account_id": self.account.id})
            return FlowResult.RETRY

class AdsPreferencesPopup1Handler(StateHandler):
    """Handle ads preferences popup type 1"""
    
    def handle(self, page: Page) -> FlowResult:
        try:
            self.logger.info("Accepting ads preferences popup", extra={"account_id": self.account.id})
            
            start_time = time.perf_counter()
            self.automation.human_click(
                page,
                selectors=["button#save-all-pur"],
                deep_search=True
            )

            duration = time.perf_counter() - start_time
            self.logger.info(f"Ads preferences popup accepted: {duration:.2f} seconds", extra={"account_id": self.account.id})
            
            page.wait_for_timeout(1500)
            return FlowResult.SUCCESS
            
        except Exception as e:
            self.logger.error(f"Ads preferences popup handler failed - {e}", extra={"account_id": self.account.id})
            return FlowResult.RETRY

class AdsPreferencesPopup2Handler(StateHandler):
    """Handle ads preferences popup type 2"""
    
    def handle(self, page: Page) -> FlowResult:
        try:
            self.logger.info("Ads preferences popup handler: Denying", extra={"account_id": self.account.id})
            
            start_time = time.perf_counter()
            self.automation.human_click(
                page,
                selectors=["button#deny"],
                deep_search=True
            )

            duration = time.perf_counter() - start_time
            self.logger.info(f"Ads preferences popup denied: {duration:.2f} seconds", extra={"account_id": self.account.id})
            
            page.wait_for_timeout(1500)
            return FlowResult.SUCCESS
            
        except Exception as e:
            self.logger.error(f"Ads preferences popup handler failed - {e}", extra={"account_id": self.account.id})
            return FlowResult.RETRY

class SmartFeaturesPopupHandler(StateHandler):
    """Handle smart features popup"""
    
    def handle(self, page: Page) -> FlowResult:
        try:
            self.logger.info("Smart features popup handler: Accepting", extra={"account_id": self.account.id})
            
            start_time = time.perf_counter()
            self.automation.human_click(
                page,
                selectors=['button[data-component-path="acceptall-button"]'],
                deep_search=True
            )

            duration = time.perf_counter() - start_time
            self.logger.info(f"Smart features popup accepted: {duration:.2f} seconds", extra={"account_id": self.account.id})
            
            page.wait_for_timeout(1500)
            page.reload()
            return FlowResult.SUCCESS
            
        except Exception as e:
            self.logger.error(f"Smart features popup handler failed - {e}", extra={"account_id": self.account.id})
            return FlowResult.RETRY

class UnknownPageHandler(StateHandler):
    """Handle unknown pages - redirect to GMX"""
    
    def handle(self, page: Page) -> FlowResult:
        try:
            self.logger.warning("UnknownPageHandler: Redirecting to GMX", extra={"account_id": self.account.id})
            
            navigate_to(page, "https://alligator.navigator.gmx.net/go/?targetURI=https://link.gmx.net/mail/showStartView&ref=link")
            self.automation.human_behavior.read_delay()
            return FlowResult.RETRY
            
        except Exception as e:
            self.logger.error(f"UnknownPageHandler: Failed - {e}", extra={"account_id": self.account.id})
            return FlowResult.RETRY