from core.flow_engine.state_handler import StateHandler
from modules.core.flow_state import FlowResult
import time
from playwright.sync_api import Page
from core.utils.browser_utils import navigate_to

class LiberoLoginPageHandler(StateHandler):
    """Handle Libero Login Page (Enter Email)"""
    def handle(self, page: Page) -> FlowResult:
        try:
            self.logger.info("Entering email", extra={"account_id": self.account.id})
            
            # Handle Cookies Consent
            try:
                if page.locator("div#iubenda-cs-banner").is_visible():
                    self.logger.info("Cookies banner detected immediately", extra={"account_id": self.account.id})
                    self.automation.human_click(
                        page,
                        selectors=['div#iubenda-cs-banner button.iubenda-cs-accept-btn.ubl-cst__btn--accept'],
                        deep_search=False
                    )
                else: 
                     # Wait up to 5s
                    try:
                        page.wait_for_selector("div#iubenda-cs-banner", state="visible", timeout=5000)
                        self.logger.info("Cookies banner appeared", extra={"account_id": self.account.id})
                        self.automation.human_click(
                            page,
                            selectors=['div#iubenda-cs-banner button.iubenda-cs-accept-btn.ubl-cst__btn--accept'],
                            deep_search=False
                        )
                    except:
                        self.logger.info("No cookies banner detected within 5s", extra={"account_id": self.account.id})

            except Exception as e:
                self.logger.warning(f"Error handling cookies banner: {e}", extra={"account_id": self.account.id})
            
            # Fill email
            self.automation.human_fill(
                page,
                selectors=['input#loginid'], 
                text=self.account.email,
                deep_search=False
            )

            # Check Remember Me
            self.logger.info("Checking remember me", extra={"account_id": self.account.id})
            self.automation.human_click(
                page,
                selectors=['label.iol-material-checkbox'],
                deep_search=False
            )
            
            # Click Next/Submit
            self.automation.human_click(
                page,
                selectors=['button#form_submit'],
                deep_search=False
            )

            # Wait for either Password Input (Skip Captcha) OR Captcha Solved
            self.logger.info("Waiting for next state (Password or Captcha)...", extra={"account_id": self.account.id})
            
            password_selector = 'input#password'
            # Using class that indicates checked state instead of checkmark element which might always exist
            solved_selector = '.recaptcha-checkbox-checked'
            
            start_time = time.time()
            
            while time.time() - start_time < 300: # 5 minutes
                # 1. Check for Password Field
                if page.locator(password_selector).is_visible():
                    self.logger.info("Password field detected, skipping CAPTCHA wait", extra={"account_id": self.account.id})
                    return FlowResult.SUCCESS  # Flow will switch to LiberoPasswordPageHandler
                
                # 2. Check for Captcha Solved Class (Deep search style)
                captcha_solved = False
                for frame in page.frames:
                    try:
                        if frame.locator(solved_selector).count() > 0:
                            captcha_solved = True
                            break
                    except:
                        pass
                
                if captcha_solved:
                    self.logger.info("CAPTCHA solved (checked class found)", extra={"account_id": self.account.id})
                    
                    # Click Submit again
                    self.logger.info("Clicking submit again after CAPTCHA", extra={"account_id": self.account.id})
                    self.automation.human_click(
                        page,
                        selectors=['button#form_submit'],
                        deep_search=False
                    )
                    return FlowResult.SUCCESS

                time.sleep(1)
            
            self.logger.warning("Timeout waiting for Password or Captcha", extra={"account_id": self.account.id})
            page.reload()
            return FlowResult.RETRY

        except Exception as e:
            self.logger.error(f"LiberoLoginPageHandler failed: {e}", extra={"account_id": self.account.id})
            return FlowResult.RETRY

class LiberoPasswordPageHandler(StateHandler):
    """Handle Libero Password Page"""
    def handle(self, page: Page) -> FlowResult:
        try:
            self.logger.info("Entering password", extra={"account_id": self.account.id})
            
            # Fill password
            self.automation.human_fill(
                page,
                selectors=['input#password'],
                text=self.account.password,
                deep_search=False
            )
            
            # Click Submit
            self.automation.human_click(
                page,
                selectors=['button#form_submit'],
                deep_search=False
            )
            return FlowResult.SUCCESS
        except Exception as e:
            self.logger.error(f"LiberoPasswordPageHandler failed: {e}", extra={"account_id": self.account.id})
            return FlowResult.RETRY

class LiberoInboxPageHandler(StateHandler):
    """Handle Libero Inbox Page and popups"""
    def handle(self, page: Page) -> FlowResult:
        try:
            self.logger.info("Handling Inbox Page", extra={"account_id": self.account.id})
            
            # Check for Wizard/Welcome Dialog
            wizard = page.locator('div.wizard-container')
            if wizard.is_visible():
                self.logger.info("Closing wizard popup", extra={"account_id": self.account.id})
                self.automation.human_click(
                    page,
                    selectors=['div.wizard-container button.wizard-close'],
                    deep_search=False
                )
                page.wait_for_timeout(2000)
            
            # Check for Ad Dialog
            ad_dialog = page.locator('div.io-ox-dialog-wrapper')
            if ad_dialog.is_visible():
                self.logger.info("Closing ad popup", extra={"account_id": self.account.id})
                self.automation.human_click(
                    page,
                    selectors=['div.io-ox-dialog-wrapper a.close'],
                    deep_search=False
                )
                page.wait_for_timeout(2000)

            return FlowResult.SUCCESS
        except Exception as e:
            self.logger.error(f"LiberoInboxPageHandler failed: {e}", extra={"account_id": self.account.id})
            return FlowResult.RETRY

class LiberoSuspendedPageHandler(StateHandler):
    """Handle Libero suspended Page"""
    def handle(self, page: Page) -> FlowResult:
        self.logger.info("Handling suspended Page", extra={"account_id": self.account.id})
        return FlowResult.SUSPENDED

class UnknownPageHandler(StateHandler):
    """Handle unknown pages - redirect to Libero"""
    
    def handle(self, page: Page) -> FlowResult:
        try:
            self.logger.warning("UnknownPageHandler: Redirecting to Libero", extra={"account_id": self.account.id})
            
            navigate_to(page, "https://mail1.libero.it/")
            self.automation.human_behavior.read_delay()
            return FlowResult.RETRY
            
        except Exception as e:
            self.logger.error(f"UnknownPageHandler: Failed - {e}", extra={"account_id": self.account.id})
            return FlowResult.RETRY
