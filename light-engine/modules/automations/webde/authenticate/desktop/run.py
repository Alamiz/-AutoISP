import time
import logging
from playwright.sync_api import Page, Error as PlaywrightError
from core.browser.browser_helper import PlaywrightBrowserFactory
from core.utils.retry_decorators import RequiredActionFailed
from core.utils.exceptions import JobCancelledException
from core.humanization.actions import HumanAction
from core.utils.identifier import identify_page
from core.flow_engine.smart_flow import StatefulFlow
from core.flow_engine.state_handler import StateHandlerRegistry
from modules.core.flow_state import FlowResult
from .handlers import (
    LoginPageHandler,
    LoginPageV2Handler,
    LoggedInPageHandler,
    AdsPreferencesPopup1Handler,
    AdsPreferencesPopup2Handler,
    UnknownPageHandler,
    MailCheckOptionsHandler,
)
from automations.common_handlers import (
    WrongPasswordPageHandler,
    WrongEmailPageHandler,
    LoginCaptchaHandler,
    SecuritySuspensionHandler,
    PhoneVerificationHandler,
    InboxHandler,
    SmartFeaturesPopupHandler
)
from core.pages_signatures.webde.desktop import PAGE_SIGNATURES
from core.utils.browser_utils import navigate_to
from core.utils.extension_helper import get_rektcaptcha_popup_url

class WebDEAuthentication(HumanAction):
    """
    State-based web.de authentication using StatefulFlow
    """
    
    GOAL_STATES = {"webde_inbox"}
    MAX_FLOW_ITERATIONS = 15
    
    def __init__(self, account, user_agent_type="desktop", job_id=None):
        super().__init__()
        self.account = account
        self.user_agent_type = user_agent_type
        self.signatures = PAGE_SIGNATURES
        self.job_id = job_id
        
        self.logger = logging.getLogger("autoisp")
        self.profile = self.account.email.split('@')[0]
        
        self.browser = PlaywrightBrowserFactory(
            profile_dir=f"Profile_{self.profile}",
            account=self.account,
            user_agent_type=user_agent_type,
            job_id=job_id
        )

    def _setup_state_handlers(self) -> StateHandlerRegistry:
        """Setup state handler registry with all authentication handlers."""
        registry = StateHandlerRegistry(
            identifier_func=identify_page,
            signatures=self.signatures,
            logger=self.logger
        )
        
        registry.register("webde_login_page", LoginPageHandler(self, self.logger, self.browser._context))
        registry.register("webde_login_page_v2", LoginPageV2Handler(self, self.logger, self.browser._context))
        registry.register("mailcheck_options_page", MailCheckOptionsHandler(self, self.logger, self.browser._context))
        registry.register("webde_login_wrong_password", WrongPasswordPageHandler(self, self.logger))
        registry.register("webde_login_wrong_username", WrongEmailPageHandler(self, self.logger))
        registry.register("webde_login_captcha_page", LoginCaptchaHandler(self, self.logger, self.job_id))
        registry.register("webde_logged_in_page", LoggedInPageHandler(self, self.logger))
        registry.register("webde_inbox_ads_preferences_popup_1_core", AdsPreferencesPopup1Handler(self, self.logger))
        # registry.register("webde_inbox_ads_preferences_popup_1", AdsPreferencesPopup1Handler(self, self.logger))
        # registry.register("webde_inbox_ads_preferences_popup_2", AdsPreferencesPopup2Handler(self, self.logger))
        registry.register("webde_inbox_smart_features_popup", SmartFeaturesPopupHandler(self, self.logger))
        registry.register("webde_security_suspension", SecuritySuspensionHandler(self, self.logger))
        registry.register("webde_phone_verification", PhoneVerificationHandler(self, self.logger))
        registry.register("webde_inbox", InboxHandler(self, self.logger))
        registry.register("unknown", UnknownPageHandler(self, self.logger))
        
        return registry

    def _is_goal_reached(self, page: Page) -> bool:
        """Check if we've reached inbox."""
        try:
            page_id = identify_page(page, page.url, self.signatures)
            is_goal = page_id in self.GOAL_STATES
            if is_goal:
                self.logger.debug(f"Goal state reached: {page_id}", extra={"account_id": self.account.id})
            return is_goal
        except Exception as e:
            self.logger.warning(f"Error checking goal: {e}", extra={"account_id": self.account.id})
            return False

    def execute(self) -> dict:
        """Runs authentication flow for web.de"""
        self.logger.info(f"Starting authentication for {self.account.email}", extra={"account_id": self.account.id})
        
        if self.account.proxy_settings:
            proxy_info = f"{self.account.proxy_settings['protocol']}://{self.account.proxy_settings['host']}:{self.account.proxy_settings['port']}"
            self.logger.info(f"Using proxy: {proxy_info}", extra={"account_id": self.account.id})

        try:
            self.browser.start()
            if self.job_id:
                pass
                # from modules.core.job_manager import job_manager
                # job_manager.register_browser(self.job_id, self.browser)
            page = self.browser.new_page()
            self.authenticate(page)
            
            self.logger.info(f"Authentication successful for {self.account.email}", extra={"account_id": self.account.id})
            return {"status": "success", "message": "Authentication completed successfully"}
        
        except JobCancelledException:
            raise
        except PlaywrightError as e:
            if "Target closed" in str(e):
                self.logger.warning(f"Browser closed manually for {self.account.email}", extra={"account_id": self.account.id})
                return {"status": "failed", "message": "Browser closed manually"}
            self.logger.error(f"Playwright error for {self.account.email}: {e}", extra={"account_id": self.account.id})
            return {"status": "failed", "message": str(e)}
        except RequiredActionFailed as e:
            self.logger.error(f"Authentication failed for {self.account.email}: {e}", extra={"account_id": self.account.id})
            status = e.status.name if e.status else "failed"
            return {"status": status, "message": str(e)}
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}", extra={"account_id": self.account.id})
            return {"status": "failed", "message": str(e)}
        finally:
            if self.job_id:
                pass
                # from modules.core.job_manager import job_manager
                # job_manager.unregister_browser(self.job_id)
            self.browser.close()

    def authenticate(self, page: Page):
        """State-based authentication using StatefulFlow."""
        # Use specific entry URL that redirects to login if needed
        WEBDE_ENTRY_URL = "https://alligator.navigator.web.de/go/?targetURI=https://link.web.de/mail/showStartView&ref=link"
        navigate_to(page, WEBDE_ENTRY_URL)
        self.human_behavior.read_delay()
        
        state_registry = self._setup_state_handlers()
        
        flow = StatefulFlow(
            state_registry=state_registry,
            goal_checker=self._is_goal_reached,
            account=self.account,
            max_steps=self.MAX_FLOW_ITERATIONS,
            logger=self.logger,
            job_id=self.job_id
        )
        
        result = flow.run(page)
        
        if result.status not in (FlowResult.SUCCESS, FlowResult.COMPLETED):
            raise RequiredActionFailed(f"Failed to reach inbox. Status: {result.status.name}, Message: {result.message}", status=result.status)
        
        # Update account state to active on success
        # update_account_state(self.account.id, "active")

        self.logger.info("Authentication completed", extra={"account_id": self.account.id})