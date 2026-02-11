from playwright.sync_api import Page
from core.flow_engine.state_handler import StateHandler
from modules.core.flow_state import FlowResult
# from crud.account import update_account_state
from core.utils.retry_decorators import retry_action
from core.humanization.actions import HumanAction
from core.utils.navigation import navigate_with_retry

class CommonHandler(StateHandler):
    """Base class for common handlers that need account_id"""
    def __init__(self, automation, logger=None):
        super().__init__(automation, logger)

class InboxHandler(CommonHandler):
    """Handle inbox page"""
    def handle(self, page: Page = None) -> FlowResult:
        return FlowResult.SUCCESS

class WrongPasswordPageHandler(CommonHandler):
    """Handle wrong password page"""
    def handle(self, page: Page = None) -> FlowResult:
        if self.logger:
            self.logger.warning("WrongPasswordPageHandler: Wrong password detected")
        # update_account_state(self.account.id, "wrong_password")
        return FlowResult.WRONG_PASSWORD

class WrongEmailPageHandler(CommonHandler):
    """Handle wrong email page"""
    def handle(self, page: Page = None) -> FlowResult:
        if self.logger:
            self.logger.warning("WrongEmailPageHandler: Wrong email detected")
        # update_account_state(self.account.id, "wrong_username")
        return FlowResult.WRONG_EMAIL

class LoginNotPossiblePageHandler(CommonHandler):
    """Handle login not possible page"""
    def handle(self, page: Page = None) -> FlowResult:
        if self.logger:
            self.logger.warning("LoginNotPossiblePageHandler: Login not possible detected")
        # update_account_state(self.account.id, "error")
        return FlowResult.FAILED

class LoginCaptchaHandler(CommonHandler, HumanAction):
    """Handle login captcha with auto-solve + fallback to user"""

    CAPTCHA_SELECTOR = 'div[data-testid="captcha-view"] div.cf-checkbox, div[data-testid="captcha-container"] div.cf-checkbox'

    PASSWORD_SELECTOR = "input#password, input[name='password']"

    def __init__(self, automation, logger=None, job_id=None):
        CommonHandler.__init__(self, automation, logger)
        HumanAction.__init__(self, job_id=job_id)

    def handle(self, page: Page = None) -> FlowResult:
        from core.utils.element_finder import deep_find_elements
        import time

        if self.logger:
            self.logger.warning(
                "CaptchaHandler: Captcha detected. Attempting automatic solve...",
                extra={"account_id": self.account.id}
            )

        # update_account_state(self.account.id, "captcha")

        # 1. Try to solve captcha automatically
        solved = False

        try:
            solved = self._try_solve_captcha(page)
        except Exception as e:
            self.logger.warning(
                "CaptchaHandler: Auto-solve failed. Waiting for user...",
                extra={"account_id": self.account.id}
            )

        if solved:
            if self.logger:
                self.logger.info(
                    "CaptchaHandler: Captcha solved automatically.",
                    extra={"account_id": self.account.id}
                )
            return FlowResult.RETRY

        # 2. Fallback → wait for user
        if self.logger:
            self.logger.warning(
                "CaptchaHandler: Auto-solve failed. Waiting for user...",
                extra={"account_id": self.account.id}
            )

        return self._wait_for_user_solution(page)

    # ------------------------------------------------------------------ #
    # Automatic captcha solving (with retry decorator)
    # ------------------------------------------------------------------ #

    @retry_action(max_attempts=3, delay=2)
    def _try_solve_captcha(self, page: Page) -> bool:
        """
        Attempt to solve captcha by clicking the checkbox
        with human-like behavior.
        """

        # Give the page some time to stabilize
        page.wait_for_timeout(1500)

        # Human-like click (mouse movement + hesitation handled internally)
        self.human_click(
            page=page,
            selectors=self.CAPTCHA_SELECTOR,
            deep_search=True,
            force=False,
            timeout=5000
        )

        # Check if captcha is solved
        return self._is_captcha_solved(page)

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    def _is_captcha_solved(self, page: Page) -> bool:
        """Captcha is considered solved when password input appears."""
        from core.utils.element_finder import deep_find_elements

        elements = deep_find_elements(page, self.PASSWORD_SELECTOR)
        return any(el.is_visible() for el in elements)

    def _wait_for_user_solution(self, page: Page) -> FlowResult:
        """Wait up to 1440 seconds for user to solve captcha."""
        from core.utils.element_finder import deep_find_elements
        import time

        start_time = time.time()
        timeout = 1440  # 24 minutes

        try:
            while time.time() - start_time < timeout:
                elements = deep_find_elements(page, self.PASSWORD_SELECTOR)

                for element in elements:
                    if element.is_visible():
                        if self.logger:
                            self.logger.info(
                                "CaptchaHandler: Captcha solved by user.",
                                extra={"account_id": self.account.id}
                            )
                        return FlowResult.RETRY

                page.wait_for_timeout(1000)

            if self.logger:
                self.logger.error(
                    "CaptchaHandler: Timeout waiting for captcha solution."
                )
            return FlowResult.CAPTCHA

        except Exception as e:
            if self.logger:
                self.logger.error(
                    f"CaptchaHandler: Error while waiting for user captcha solve: {e}"
                )
            return FlowResult.ABORT


class SecuritySuspensionHandler(CommonHandler):
    """Handle security suspension page"""
    def handle(self, page: Page = None) -> FlowResult:
        if self.logger:
            self.logger.warning("SecuritySuspensionHandler: Account suspended")
        # update_account_state(self.account.id, "suspended")
        return FlowResult.SUSPENDED

class PhoneVerificationHandler(CommonHandler):
    """Handle phone verification page"""
    def handle(self, page: Page = None) -> FlowResult:
        if self.logger:
            self.logger.warning("PhoneVerificationHandler: Phone verification required")
        # update_account_state(self.account.id, "phone_verification")
        return FlowResult.PHONE_VERIFICATION

class SmartFeaturesPopupHandler(StateHandler):
    """Handle smart features popup"""
    
    def handle(self, page: Page) -> FlowResult:
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
            return FlowResult.SUCCESS
            
        except Exception as e:
            self.logger.error(f"Failed - {e}", extra={"account_id": self.account.id})
            return FlowResult.RETRY

class UnknownPageHandler(StateHandler):
    """Handle unknown pages"""

    def handle(self, page: Page, reset_link: str = None) -> FlowResult:
        try:
            if reset_link:
                navigate_with_retry(page, reset_link, self.account)
            else:
                page.reload()
            return FlowResult.RETRY
        except Exception as e:
            return FlowResult.ABORT