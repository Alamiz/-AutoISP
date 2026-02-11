import logging
import os
import datetime
from playwright.sync_api import Page
from automations.webde.authenticate.desktop.run import WebDEAuthentication
from core.browser.browser_helper import PlaywrightBrowserFactory
from core.utils.retry_decorators import RequiredActionFailed
from core.humanization.actions import HumanAction
from core.utils.identifier import identify_page
from core.flow_engine.smart_flow import SequentialFlow
from core.flow_engine.state_handler import StateHandlerRegistry
from modules.core.flow_state import FlowResult
from .steps import (
    OpenAccountMenuStep,
    NavigateToAccountSettingsStep,
    ChangePasswordStep,
    AddRecoveryEmailStep,
    SaveSecuredAccountStep,
)
from .handlers import UnknownPageHandler
from automations.common_handlers import (
    SmartFeaturesPopupHandler
)
from core.pages_signatures.webde.desktop import PAGE_SIGNATURES


class ChangePasswordAndAddRecovery(HumanAction):
    """
    web.de Desktop - Change Password and Add Recovery Email automation.
    """
    
    def __init__(self, account, user_agent_type="desktop", job_id=None, log_dir=None):
        super().__init__()
        self.account = account
        self.user_agent_type = user_agent_type
        self.job_id = job_id
        self.log_dir = log_dir
        self.logger = logging.getLogger("autoisp")
        self.profile = self.account.email.split('@')[0]
        self.signatures = PAGE_SIGNATURES
        
        # Will be set during execution
        self.new_password = None
        self.recovery_email = None
        self.output_dir = None
        
        # Log path for recovery email and password change
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.recovery_log_path = os.path.join("output", "recovery_and_password", f"processed_{timestamp}.txt")

        self.browser = PlaywrightBrowserFactory(
            profile_dir=f"Profile_{self.profile}",
            account=self.account,
            user_agent_type=user_agent_type,
            job_id=job_id
        )

    def _setup_state_handlers(self) -> StateHandlerRegistry:
        """Setup state handler registry for unexpected page states."""
        registry = StateHandlerRegistry(
            identifier_func=identify_page,
            signatures=self.signatures,
            logger=self.logger
        )
        registry.register("webde_inbox_smart_features_popup", SmartFeaturesPopupHandler(self, self.logger))
        registry.register("unknown", UnknownPageHandler(self, self.logger))
        return registry

    def execute(self):
        self.logger.info("Starting Change Password and Add Recovery", extra={"account_id": self.account.id})
        page = None
        status = "failed"
        
        # Determine output directory from log_dir
        if self.log_dir:
            self.output_dir = os.path.dirname(os.path.dirname(self.log_dir))
        
        try:
            self.browser.start()
            page = self.browser.new_page()
            
            # Authenticate first
            webde_auth = WebDEAuthentication(
                account=self.account,
                user_agent_type=self.user_agent_type,
                job_id=self.job_id
            )
            webde_auth.authenticate(page)

            # Change password and add recovery email using SequentialFlow
            self.change_password_and_add_recovery(page)
            
            self.logger.info("Change password and add recovery successful", extra={"account_id": self.account.id})
            status = "success"
            return {"status": "success", "message": "Password changed and recovery email added"}
        
        except RequiredActionFailed as e:
            self.logger.error("Change password and add recovery failed", extra={"account_id": self.account.id})
            status = e.status.name if e.status else "failed"
            return {"status": status, "message": str(e)}
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}", exc_info=True, extra={"account_id": self.account.id})
            return {"status": "failed", "message": str(e)}
        finally:
            # Take screenshot before closing
            if page and self.log_dir:
                try:
                    screenshot_path = os.path.join(self.log_dir, f"screenshot_{status}.png")
                    page.screenshot(path=screenshot_path)
                    self.logger.info(f"Screenshot saved to {screenshot_path}")
                except Exception as e:
                    self.logger.error(f"Failed to take screenshot: {e}")
            
            self.browser.close()

    def change_password_and_add_recovery(self, page: Page):
        """Change password and add recovery email using SequentialFlow."""
        state_registry = self._setup_state_handlers()
        
        # Define steps in order: Recovery first, then Password Change
        steps = [
            OpenAccountMenuStep(self, self.logger),
            NavigateToAccountSettingsStep(self, self.logger),
            AddRecoveryEmailStep(self, self.logger),
            ChangePasswordStep(self, self.logger),
            SaveSecuredAccountStep(self, self.logger),
        ]
        
        flow = SequentialFlow(steps, state_registry=state_registry, account=self.account, logger=self.logger)
        result = flow.run(page)
        
        if result.status not in (FlowResult.SUCCESS, FlowResult.COMPLETED):
            raise RequiredActionFailed(f"Failed to complete process. Status: {result.status.name}, Message: {result.message}", status=result.status)
        
        self.logger.info("Change password and add recovery completed via SequentialFlow", extra={"account_id": self.account.id})