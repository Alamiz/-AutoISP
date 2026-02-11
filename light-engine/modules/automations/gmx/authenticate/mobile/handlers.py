"""
State handlers for GMX Mobile Authentication using StatefulFlow.
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

class RegisterPageHandler(StateHandler):
    """Handle GMX mobile register page - click login button"""
    
    def handle(self, page: Page) -> FlowResult:
        try:
            self.logger.info("Clicking login button", extra={"account_id": self.account.id})
            
            start_time = time.perf_counter()
            self.automation.human_click(
                page,
                selectors=['form.login-link.login-mobile > button[type="submit"]'],
            )
            
            duration = time.perf_counter() - start_time
            self.logger.info(f"Login button clicked: {duration:.2f} seconds", extra={"account_id": self.account.id})
            
            page.wait_for_timeout(2000)
            return FlowResult.SUCCESS
            
        except Exception as e:
            self.logger.error(f"Failed - {e}", extra={"account_id": self.account.id})
            return FlowResult.RETRY


class LoginPageHandler(StateHandler):
    """Handle GMX mobile login page - enter credentials"""

    def handle(self, page: Page) -> FlowResult:
        try:
            # Check if we are already at the password step (e.g. after captcha retry)
            if page.is_visible('form input#password'):
                self.logger.info("Password field visible, skipping email entry", extra={"account_id": self.account.id})
                
                start_time = time.perf_counter()
                self.automation.human_fill(
                    page,
                    selectors=['form input#password'],
                    text=self.account.password,
                )
                
                self.automation.human_click(
                    page,
                    selectors=['button[type="submit"][data-testid="button-next"]'],
                )
                
                duration = time.perf_counter() - start_time
                self.logger.info(f"Credentials submitted (password only): {duration:.2f} seconds", extra={"account_id": self.account.id})
                
                page.wait_for_timeout(10_000)
                return FlowResult.SUCCESS

            self.logger.info("Entering credentials", extra={"account_id": self.account.id})
            
            start_time = time.perf_counter()
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
            
            duration = time.perf_counter() - start_time
            self.logger.info(f"Email submitted: {duration:.2f} seconds", extra={"account_id": self.account.id})

            # Check if captcha is present
            start_time = time.perf_counter()
            captcha_elements = deep_find_elements(page, 'div[data-testid="captcha-container"]')
            if captcha_elements:
                duration = time.perf_counter() - start_time
                self.logger.info(f"Captcha check took: {duration:.2f} seconds", extra={"account_id": self.account.id})
                return FlowResult.SUCCESS
            
            start_time = time.perf_counter()
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
            
            duration = time.perf_counter() - start_time
            self.logger.info(f"Credentials submitted: {duration:.2f} seconds", extra={"account_id": self.account.id})
            
            page.wait_for_timeout(10_000)
            return FlowResult.SUCCESS
            
        except Exception as e:
            self.logger.error(f"Failed - {e}", extra={"account_id": self.account.id})
            return FlowResult.RETRY

class LoggedInPageHandler(StateHandler):
    """Handle GMX mobile logged in page - click continue to inbox"""
    
    def handle(self, page: Page) -> FlowResult:
        try:
            self.logger.info("Clicking profile and continue", extra={"account_id": self.account.id})
            
            start_time = time.perf_counter()
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
            
            duration = time.perf_counter() - start_time
            self.logger.info(f"Profile and continue clicked: {duration:.2f} seconds", extra={"account_id": self.account.id})
            
            page.wait_for_timeout(2000)
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
            self.logger.error(f"Failed - {e}", extra={"account_id": self.account.id})
            return FlowResult.RETRY


class AdsPreferencesPopup2Handler(StateHandler):
    """Handle ads preferences popup type 2"""
    
    def handle(self, page: Page) -> FlowResult:
        try:
            self.logger.info("Denying ads preferences popup", extra={"account_id": self.account.id})
            
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
            self.logger.error(f"Failed - {e}", extra={"account_id": self.account.id})
            return FlowResult.RETRY

class UnknownPageHandler(StateHandler):
    """Handle unknown pages - redirect to GMX mobile"""
    
    def handle(self, page: Page) -> FlowResult:
        try:
            self.logger.warning("Redirecting to GMX mobile", extra={"account_id": self.account.id})
            
            navigate_to(page, "https://lightmailer-bs.gmx.net/")
            self.automation.human_behavior.read_delay()
            return FlowResult.RETRY
            
        except Exception as e:
            self.logger.error(f"Failed - {e}", extra={"account_id": self.account.id})
            return FlowResult.RETRY