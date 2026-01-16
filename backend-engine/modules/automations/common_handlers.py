from playwright.sync_api import Page
from core.flow_engine.state_handler import StateHandler, HandlerAction
from crud.account import update_account_state
from core.utils.retry_decorators import retry_action
from core.humanization.actions import HumanAction

class CommonHandler(StateHandler):
    """Base class for common handlers that need account_id"""
    def __init__(self, account_id: int, logger=None):
        super().__init__(logger)
        self.account_id = account_id

class WrongPasswordPageHandler(CommonHandler):
    """Handle wrong password page"""
    def handle(self, page: Page = None) -> HandlerAction:
        if self.logger:
            self.logger.warning("WrongPasswordPageHandler: Wrong password detected")
        update_account_state(self.account_id, "wrong_password")
        return "abort"

class WrongEmailPageHandler(CommonHandler):
    """Handle wrong email page"""
    def handle(self, page: Page = None) -> HandlerAction:
        if self.logger:
            self.logger.warning("WrongEmailPageHandler: Wrong email detected")
        update_account_state(self.account_id, "wrong_username")
        return "abort"

class LoginNotPossiblePageHandler(CommonHandler):
    """Handle login not possible page"""
    def handle(self, page: Page = None) -> HandlerAction:
        if self.logger:
            self.logger.warning("LoginNotPossiblePageHandler: Login not possible detected")
        update_account_state(self.account_id, "error")
        return "abort"

class LoginCaptchaHandler(CommonHandler, HumanAction):
    """Handle login captcha with auto-solve + fallback to user"""

    CAPTCHA_SELECTOR = [
        'div[data-testid="captcha-view"] div.cf-checkbox'
    ]

    PASSWORD_SELECTOR = "input#password"

    def __init__(self, account_id: int, logger=None, job_id=None):
        CommonHandler.__init__(self, account_id, logger)
        HumanAction.__init__(self, job_id=job_id)

    def handle(self, page: Page = None) -> HandlerAction:
        from core.utils.element_finder import deep_find_elements
        import time

        if self.logger:
            self.logger.warning(
                "LoginCaptchaHandler: Captcha detected. Attempting automatic solve..."
            )

        update_account_state(self.account_id, "captcha")

        # 1. Try to solve captcha automatically
        solved = False

        try:
            solved = self._try_solve_captcha(page)
        except Exception as e:
            self.logger.warning("LoginCaptchaHandler: Auto-solve failed. Waiting for user...")

        if solved:
            if self.logger:
                self.logger.info("LoginCaptchaHandler: Captcha solved automatically.")
            return "retry"

        # 2. Fallback → wait for user
        if self.logger:
            self.logger.warning(
                "LoginCaptchaHandler: Auto-solve failed. Waiting for user..."
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

        # Allow Cloudflare to process the interaction
        page.wait_for_timeout(3000)

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

    def _wait_for_user_solution(self, page: Page) -> HandlerAction:
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
                                "LoginCaptchaHandler: Captcha solved by user."
                            )
                        return "retry"

                page.wait_for_timeout(1000)

            if self.logger:
                self.logger.error(
                    "LoginCaptchaHandler: Timeout waiting for captcha solution."
                )
            return "abort"

        except Exception as e:
            if self.logger:
                self.logger.error(
                    f"LoginCaptchaHandler: Error while waiting for user captcha solve: {e}"
                )
            return "abort"


class SecuritySuspensionHandler(CommonHandler):
    """Handle security suspension page"""
    def handle(self, page: Page = None) -> HandlerAction:
        if self.logger:
            self.logger.warning("SecuritySuspensionHandler: Account suspended")
        update_account_state(self.account_id, "suspended")
        return "abort"

class PhoneVerificationHandler(CommonHandler):
    """Handle phone verification page"""
    def handle(self, page: Page = None) -> HandlerAction:
        if self.logger:
            self.logger.warning("PhoneVerificationHandler: Phone verification required")
        update_account_state(self.account_id, "phone_verification")
        return "abort"
