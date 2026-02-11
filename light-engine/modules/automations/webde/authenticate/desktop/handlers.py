"""
State handlers for web.de Desktop Authentication using StatefulFlow.
"""
import logging
import time
from playwright.sync_api import Page
from core.flow_engine.state_handler import StateHandler
from modules.core.flow_state import FlowResult
from core.utils.element_finder import deep_find_elements
from core.utils.browser_utils import navigate_to
from core.utils.extension_helper import get_mailcheck_options_url, get_mailcheck_mail_panel_url

class LoginPageHandler(StateHandler):
    """Handle web.de login page - redirect to extension for login"""

    def __init__(self, automation, logger, context=None):
        super().__init__(automation, logger)
        self.context = context  # Needed for popup handling later

    def handle(self, page: Page) -> FlowResult:
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
                return FlowResult.SUCCESS

            # Check if we should use extension flow (default for new login)
            # self.logger.info("Redirecting to MailCheck extension for login", extra={"account_id": self.account.id})
            
            # ext_options_url = get_mailcheck_options_url(page)
            # if ext_options_url:
            #     navigate_to(page, ext_options_url)
            #     page.wait_for_load_state("domcontentloaded")
            #     return FlowResult.SUCCESS
            # else:
            #     self.logger.warning("Extension not found, falling back to standard login", extra={"account_id": self.account.id})

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
                return FlowResult.SUCCESS

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
            return FlowResult.SUCCESS
            
        except Exception as e:
            self.logger.error(f"Failed - {e}", extra={"account_id": self.account.id})
            return FlowResult.RETRY

class LoginPageV2Handler(StateHandler):
    """Handle GMX login page v2 - split email and password entry"""
    
    def __init__(self, automation, logger, context=None):
        super().__init__(automation, logger)
        self.context = context
    
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

            # Check if we should use extension flow (default for new login)
            # self.logger.info("Redirecting to MailCheck extension for login", extra={"account_id": self.account.id})
            
            # ext_options_url = get_mailcheck_options_url(page)
            # if ext_options_url:
            #     navigate_to(page, ext_options_url)
            #     page.wait_for_load_state("domcontentloaded")
            #     return FlowResult.SUCCESS
            # else:
            #     self.logger.warning("Extension not found, falling back to standard login", extra={"account_id": self.account.id})

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

class MailCheckOptionsHandler(StateHandler):
    """Handle MailCheck extension options page - perform login via extension"""
    
    def __init__(self, automation, logger, context=None):
        super().__init__(automation, logger)
        self.context = context  # BrowserContext for expect_page()
    
    def handle(self, page: Page) -> FlowResult:
        try:
            self.logger.info("Performing extension-based login", extra={"account_id": self.account.id})
            
            # 1. Click add account
            page.click("button#email-add")
            page.wait_for_timeout(500)  # Allow UI to update
            
            
            # 2. Click Web.de brand label
            page.click("label#icon-webde")
            page.wait_for_timeout(500)  # Allow UI to update
            
            # 3. Fill email address
            page.fill("input#emailaddress", self.account.email)
            
            # 4. Click add-account and capture popup
            # Requires context to be passed to handler
            if not self.context:
                self.logger.error("Browser context not available for popup handling", extra={"account_id": self.account.id})
                return FlowResult.ABORT

            with self.context.expect_page(timeout=10000) as popup_info:
                page.click("button#add-account")
            
            popup = popup_info.value
            popup.wait_for_load_state("domcontentloaded")
            self.logger.info("Popup opened", extra={"account_id": self.account.id})

            # 5. Fill password in popup
            popup.wait_for_selector('input[type="password"]', timeout=10000)
            popup.fill('input[type="password"]', self.account.password)
            popup.wait_for_timeout(950)
            
            # 6. Click submit button
            popup.click("button#submitButton")
            popup.wait_for_timeout(1150)
            
            # 7. Wait for popup to close or redirect
            # Assuming popup closes after successful login or redirects
            # We iterate until popup is closed or we can verify login success in main page
            try:
                popup.wait_for_event("close", timeout=15000)
                self.logger.info("Popup closed", extra={"account_id": self.account.id})
            except:
                self.logger.info("Popup did not close automatically, checking main page...", extra={"account_id": self.account.id})

            # 7. Navigate to mail panel to finalize login
            self.logger.info("Navigate to mail panel to finalize login", extra={"account_id": self.account.id})
            mail_panel_url = get_mailcheck_mail_panel_url(page)
            if mail_panel_url:
                navigate_to(page, mail_panel_url)
                page.wait_for_load_state("domcontentloaded")
                
                # Click on the email address and expect a new page
                self.logger.info("Clicking email address and waiting for new page...", extra={"account_id": self.account.id})
                with self.context.expect_page(timeout=15000) as new_page_info:
                    page.click("span.email-address")
                
                inbox_page = new_page_info.value
                inbox_page.wait_for_load_state("domcontentloaded")
                
                # Check if the opened page is the inbox
                try:
                    inbox_page.wait_for_selector("header.navigator__brand-logo-appname", timeout=15000)
                    self.logger.info("Opened page verified as Web.de Inbox.", extra={"account_id": self.account.id})
                    inbox_page.close() # Close the extra tab, we'll use the main one
                except Exception as e:
                    self.logger.warning(f"Opened page check failed: {e}", extra={"account_id": self.account.id})
                    # Don't fail hard, maybe the main navigation will still work
            
            # 8. Navigate to Web.de entry link to verify/finalize on the main page
            WEBDE_ENTRY_URL = "https://alligator.navigator.web.de/go/?targetURI=https://link.web.de/mail/showStartView&ref=link"
            navigate_to(page, WEBDE_ENTRY_URL)
            
            # 9. Wait for inbox to load (managed by next state check or explicitly here)
            # If we return continue, the flow engine will identify the new page (hopefully inbox)
            return FlowResult.SUCCESS
            
        except Exception as e:
            self.logger.error(f"Extension login failed: {e}", extra={"account_id": self.account.id})
            return FlowResult.RETRY

class LoggedInPageHandler(StateHandler):
    """Handle already authenticated page - click continue"""

    def handle(self, page: Page) -> FlowResult:
        try:
            self.logger.info("Clicking continue", extra={"account_id": self.account.id})
            
            start_time = time.perf_counter()
            self.automation.human_click(
                page, selectors=["button[data-component-path='openInbox.continue-button']"], deep_search=True
            )
            
            duration = time.perf_counter() - start_time
            self.logger.info(f"Continue clicked: {duration:.2f} seconds", extra={"account_id": self.account.id})
            
            page.wait_for_selector("header.navigator__brand-logo-appname") # Wait for inbox page to load
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
            self.automation.human_click(page, selectors=["button#save-all-pur"], deep_search=True)
            
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
            self.automation.human_click(page, selectors=["button#deny"], deep_search=True)
            
            duration = time.perf_counter() - start_time
            self.logger.info(f"Ads preferences popup denied: {duration:.2f} seconds", extra={"account_id": self.account.id})
            
            page.wait_for_timeout(1500)
            return FlowResult.SUCCESS
            
        except Exception as e:
            self.logger.error(f"Failed - {e}", extra={"account_id": self.account.id})
            return FlowResult.RETRY

class UnknownPageHandler(StateHandler):
    """Handle unknown pages - redirect to web.de"""
    
    def handle(self, page: Page) -> FlowResult:
        try:
            self.logger.warning("Redirecting to web.de", extra={"account_id": self.account.id})
            
            navigate_to(page, "https://web.de/")
            self.automation.human_behavior.read_delay()
            return FlowResult.RETRY
            
        except Exception as e:
            self.logger.error(f"Failed - {e}", extra={"account_id": self.account.id})
            return FlowResult.RETRY