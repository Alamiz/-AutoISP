import logging
from playwright.sync_api import Page
from core.browser.browser_helper import PlaywrightBrowserFactory
from core.utils.retry_decorators import RequiredActionFailed
from core.humanization.actions import HumanAction
from core.utils.identifier import identify_page
from core.flow_engine.smart_flow import StatefulFlow
from core.flow_engine.state_handler import StateHandlerRegistry
from core.flow_engine.step import StepStatus
from .handlers import (
    RegisterPageHandler,
    LoginPageHandler,
    LoggedInPageHandler,
    AdsPreferencesPopup1Handler,
    AdsPreferencesPopup2Handler,
    UnknownPageHandler,
)
from automations.common_handlers import (
    WrongPasswordPageHandler,
    WrongEmailPageHandler,
    LoginCaptchaHandler,
    SecuritySuspensionHandler,
    PhoneVerificationHandler
)
from core.pages_signatures.gmx.mobile import PAGE_SIGNATURES
from crud.account import update_account_state
from core.utils.browser_utils import navigate_to

class GMXAuthentication(HumanAction):
    """
    State-based GMX Mobile authentication using StatefulFlow
    """
    
    GOAL_STATES = {"gmx_folder_list_page"}
    MAX_FLOW_ITERATIONS = 15
    
    def __init__(self, account_id, email, password, proxy_config=None, user_agent_type="mobile", job_id=None):
        super().__init__()
        self.account_id = account_id
        self.email = email
        self.password = password
        self.proxy_config = proxy_config
        self.user_agent_type = user_agent_type
        self.signatures = PAGE_SIGNATURES
        self.job_id = job_id  # For browser registration
        
        self.logger = logging.getLogger("autoisp")
        self.profile = self.email.split('@')[0]
        
        self.browser = PlaywrightBrowserFactory(
            profile_dir=f"Profile_{self.profile}",
            proxy_config=proxy_config,
            user_agent_type=user_agent_type
        )

    def _setup_state_handlers(self) -> StateHandlerRegistry:
        """Setup state handler registry with all mobile authentication handlers."""
        registry = StateHandlerRegistry(
            identifier_func=identify_page,
            signatures=self.signatures,
            logger=self.logger
        )
        
        registry.register("gmx_register_page", RegisterPageHandler(self, self.logger))
        registry.register("gmx_login_page", LoginPageHandler(self, self.email, self.password, self.logger))
        registry.register("gmx_login_wrong_password", WrongPasswordPageHandler(self.account_id, self.logger))
        registry.register("gmx_login_wrong_username", WrongEmailPageHandler(self.account_id, self.logger))
        registry.register("gmx_login_captcha_page", LoginCaptchaHandler(self.account_id, self.logger))
        registry.register("gmx_logged_in_page", LoggedInPageHandler(self, self.logger))
        registry.register("gmx_inbox_ads_preferences_popup_1", AdsPreferencesPopup1Handler(self, self.logger))
        registry.register("gmx_inbox_ads_preferences_popup_2", AdsPreferencesPopup2Handler(self, self.logger))
        registry.register("gmx_security_suspension", SecuritySuspensionHandler(self.account_id, self.logger))
        registry.register("gmx_phone_verification", PhoneVerificationHandler(self.account_id, self.logger))
        registry.register("unknown", UnknownPageHandler(self, self.logger))
        
        return registry

    def _is_goal_reached(self, page: Page) -> bool:
        """Check if we've reached a goal state."""
        try:
            page_id = identify_page(page, page.url, self.signatures)
            is_goal = page_id in self.GOAL_STATES
            if is_goal:
                self.logger.info(f"Goal state reached: {page_id}")
            return is_goal
        except Exception as e:
            self.logger.warning(f"Error checking goal: {e}")
            return False

    def execute(self) -> dict:
        """Runs authentication flow for GMX Mobile"""
        from modules.core.job_manager import job_manager
        
        self.logger.info(f"Starting mobile authentication for {self.email}")
        
        if self.proxy_config:
            proxy_info = f"{self.proxy_config['protocol']}://{self.proxy_config['host']}:{self.proxy_config['port']}"
            self.logger.info(f"Using proxy: {proxy_info}")

        try:
            self.browser.start()
            if self.job_id:
                job_manager.register_browser(self.job_id, self.browser)
            page = self.browser.new_page()

            self.authenticate(page)
            
            # Update account state to active on success
            update_account_state(self.account_id, "active")
            
            self.logger.info(f"Authentication successful for {self.email}")
            return {"status": "success", "message": "Authentication completed successfully"}
        
        except RequiredActionFailed as e:
            self.logger.error(f"Authentication failed for {self.email}: {e}")
            return {"status": "failed", "message": str(e)}
        except Exception as e:
            self.logger.error(f"Unexpected error for {self.email}: {e}")
            return {"status": "failed", "message": str(e)}
        finally:
            if self.job_id:
                job_manager.unregister_browser(self.job_id)
            self.browser.close()

    def authenticate(self, page: Page):
        """State-based authentication using StatefulFlow."""
        navigate_to(page, "https://lightmailer-bs.gmx.net/")
        self.human_behavior.read_delay()
        
        state_registry = self._setup_state_handlers()
        
        flow = StatefulFlow(
            state_registry=state_registry,
            goal_checker=self._is_goal_reached,
            max_steps=self.MAX_FLOW_ITERATIONS,
            logger=self.logger
        )
        
        result = flow.run(page)
        
        if result.status == StepStatus.FAILURE:
            raise RequiredActionFailed(f"Failed to reach folder list. Last error: {result.message}")
        
        self.logger.info("Authentication completed via StatefulFlow")


def main(account_id, email, password, proxy_config=None, device_type="mobile"):
    """Entry point for GMX mobile authentication"""
    auth = GMXAuthentication(account_id, email, password, proxy_config, device_type)
    return auth.execute()