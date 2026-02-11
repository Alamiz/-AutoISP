import logging
from playwright.sync_api import Page, Error as PlaywrightError
from core.browser.browser_helper import PlaywrightBrowserFactory
from core.utils.retry_decorators import RequiredActionFailed
from core.utils.exceptions import JobCancelledException
from core.humanization.actions import HumanAction
from core.utils.identifier import identify_page
from core.flow_engine.smart_flow import StatefulFlow
from core.utils.navigation import navigate_with_retry
from core.flow_engine.state_handler import StateHandlerRegistry
from modules.core.flow_state import FlowResult
from .handlers import (
    OnboardingPageHandler,
    LoginPageHandler,
    LoginPageV2Handler,
    LoggedInPageHandler,
    AdsPreferencesPopup1Handler,
    # AdsPreferencesPopup2Handler,
    SmartFeaturesPopupHandler,
    UnknownPageHandler,
)
from automations.common_handlers import (
    WrongPasswordPageHandler,
    WrongEmailPageHandler,
    LoginCaptchaHandler,
    SecuritySuspensionHandler,
    PhoneVerificationHandler
)
from core.pages_signatures.gmx.desktop import PAGE_SIGNATURES
# from crud.account import update_account_state

class GMXAuthentication(HumanAction):
    """
    State-based GMX authentication using StatefulFlow
    """
    
    # Define goal states (authentication is complete)
    GOAL_STATES = {"gmx_inbox"}
    
    # Maximum flow iterations to prevent infinite loops
    MAX_FLOW_ITERATIONS = 15
    
    def __init__(self, account, user_agent_type="desktop", job_id=None):
        super().__init__()
        self.account = account
        self.user_agent_type = user_agent_type
        self.signatures = PAGE_SIGNATURES
        # self.job_id = job_id  # For browser registration with job_manager
        
        self.logger = logging.getLogger("autoisp")
        self.profile = self.account.email.split('@')[0]
        
        self.browser = PlaywrightBrowserFactory(
            profile_dir=f"Profile_{self.profile}",
            account=self.account,
            user_agent_type=user_agent_type,
            job_id=job_id
        )

    def _setup_state_handlers(self) -> StateHandlerRegistry:
        """
        Setup state handler registry with all authentication handlers.
        """
        registry = StateHandlerRegistry(
            identifier_func=identify_page,
            signatures=self.signatures,
            logger=self.logger
        )
        
        # Register handlers for authentication page states
        registry.register("gmx_onboarding_page", OnboardingPageHandler(self, self.logger))
        registry.register("gmx_login_page", LoginPageHandler(self, self.logger))
        registry.register("gmx_login_page_v2", LoginPageV2Handler(self, self.logger))
        registry.register("gmx_login_wrong_password", WrongPasswordPageHandler(self, self.logger))
        registry.register("gmx_login_wrong_username", WrongEmailPageHandler(self, self.logger))
        registry.register("gmx_login_captcha_page", LoginCaptchaHandler(self, self.logger, self.job_id))
        registry.register("gmx_login_captcha_page_v2", LoginCaptchaHandler(self, self.logger, self.job_id))
        registry.register("gmx_logged_in_page", LoggedInPageHandler(self, self.logger))
        registry.register("gmx_inbox_ads_preferences_popup_1_core", AdsPreferencesPopup1Handler(self, self.logger))
        # registry.register("gmx_inbox_ads_preferences_popup_1", AdsPreferencesPopup1Handler(self, self.logger))
        # registry.register("gmx_inbox_ads_preferences_popup_2", AdsPreferencesPopup2Handler(self, self.logger))
        registry.register("gmx_inbox_smart_features_popup", SmartFeaturesPopupHandler(self, self.logger))
        registry.register("gmx_security_suspension", SecuritySuspensionHandler(self, self.logger))
        registry.register("gmx_phone_verification", PhoneVerificationHandler(self, self.logger))
        registry.register("unknown", UnknownPageHandler(self, self.logger))
        
        return registry

    def _is_goal_reached(self, page: Page) -> bool:
        """Check if we've reached a goal state (inbox)."""
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
        """
        Runs authentication flow for GMX
        """
        # from modules.core.job_manager import job_manager  # Import here to avoid circular deps
        
        self.logger.info(f"Starting authentication flow", extra={"account_id": self.account.id})
        
        # Log proxy usage if configured
        if self.account.proxy_settings:
            proxy_info = f"{self.account.proxy_settings['protocol']}://{self.account.proxy_settings['host']}:{self.account.proxy_settings['port']}"
            if 'username' in self.account.proxy_settings:
                proxy_info = f"{self.account.proxy_settings['protocol']}://{self.account.proxy_settings['username']}:***@{self.account.proxy_settings['host']}:{self.account.proxy_settings['port']}"
            self.logger.info(f"Using proxy: {proxy_info}", extra={"account_id": self.account.id})

        try:
            # Start browser with proxy configuration
            self.browser.start()
            
            # Register browser with job_manager for force-close on stop
            if self.job_id:
                pass
                # job_manager.register_browser(self.job_id, self.browser)
            
            # Create new page
            page = self.browser.new_page()

            # Authenticate using StatefulFlow
            self.authenticate(page)
            
            # Update account state to active on success
            # update_account_state(self.account.id, "active")
            
            self.logger.info(f"Authentication successful", extra={"account_id": self.account.id})
            return {"status": "success", "message": "Authentication completed successfully"}
        
        except JobCancelledException:
            raise
        except PlaywrightError as e:
            if "Target closed" in str(e):
                self.logger.warning(f"Browser closed manually", extra={"account_id": self.account.id})
                return {"status": "failed", "message": "Browser closed manually"}
            self.logger.error(f"Playwright error: {e}", extra={"account_id": self.account.id})
            return {"status": "failed", "message": str(e)}
        except RequiredActionFailed as e:
            self.logger.error(f"Authentication failed: {e}", extra={"account_id": self.account.id})
            status = e.status.name if e.status else "failed"
            return {"status": status, "message": str(e)}
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}", extra={"account_id": self.account.id})
            return {"status": "failed", "message": str(e)}
        finally:
            # Unregister browser from job_manager
            if self.job_id:
                pass
                # job_manager.unregister_browser(self.job_id)
            # Close browser
            self.browser.close()

    def authenticate(self, page: Page):
        """
        State-based authentication using StatefulFlow.
        Automatically handles different page states until reaching goal state.
        """
        # Navigate to GMX with retry on network errors
        navigate_with_retry(page, "https://alligator.navigator.gmx.net/go/?targetURI=https://link.gmx.net/mail/showStartView&ref=link", max_retries=3, account=self.account, logger=self.logger)
        self.human_behavior.read_delay()
        
        # Setup state handlers
        state_registry = self._setup_state_handlers()
        
        # Create and run StatefulFlow
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
            raise RequiredActionFailed(
                f"Failed to reach inbox. Status: {result.status.name}, Message: {result.message}", status=result.status
            )
        
        self.logger.info("Authentication completed", extra={"account_id": self.account.id})