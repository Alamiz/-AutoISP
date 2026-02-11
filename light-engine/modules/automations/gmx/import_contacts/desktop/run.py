import logging
import os
from playwright.sync_api import Page
from automations.gmx.authenticate.desktop.run import GMXAuthentication
from core.browser.browser_helper import PlaywrightBrowserFactory
from core.utils.retry_decorators import RequiredActionFailed
from core.humanization.actions import HumanAction
from core.utils.identifier import identify_page
from core.flow_engine.smart_flow import SequentialFlow
from core.flow_engine.state_handler import StateHandlerRegistry
from modules.core.flow_state import FlowResult
from .steps import (
    OpenAddressBookStep,
    OpenImportPanelStep,
    SelectSourceStep,
    UploadFileStep,
    UploadContactsStep,
    ImportContactsStep,
    VerifyImportStep
)
from .handlers import UnknownPageHandler
from core.pages_signatures.gmx.desktop import PAGE_SIGNATURES


class ImportContacts(HumanAction):
    """
    web.de Desktop Import Contacts using SequentialFlow
    """
    
    def __init__(self, account, user_agent_type="desktop", vcf_file_path=None, job_id=None, log_dir=None):
        super().__init__()
        self.account = account
        self.user_agent_type = user_agent_type
        self.vcf_file_path = vcf_file_path
        self.job_id = job_id
        self.log_dir = log_dir
        self.logger = logging.getLogger("autoisp")
        self.profile = self.account.email.split('@')[0]
        self.signatures = PAGE_SIGNATURES

        self.browser = PlaywrightBrowserFactory(
            profile_dir=f"Profile_{self.profile}",
            account=self.account,
            user_agent_type=user_agent_type,
            headless=False
        )

    def _setup_state_handlers(self) -> StateHandlerRegistry:
        """Setup state handler registry for unexpected page states."""
        registry = StateHandlerRegistry(
            identifier_func=identify_page,
            signatures=self.signatures,
            logger=self.logger
        )
        registry.register("unknown", UnknownPageHandler(self, self.logger))
        return registry

    def execute(self):
        self.logger.info(f"Starting Import Contacts", extra={"account_id": self.account.id})
        page = None
        status = "failed"
        
        try:
            self.browser.start()
            if self.job_id:
                pass
                # from modules.core.job_manager import job_manager
                # job_manager.register_browser(self.job_id, self.browser)
            page = self.browser.new_page()
            
            # Authenticate first
            gmx_auth = GMXAuthentication(
                account=self.account,
                user_agent_type=self.user_agent_type,
                job_id=self.job_id
            )
            gmx_auth.authenticate(page)

            # Import contacts using SequentialFlow
            self.import_contacts(page)
            
            self.logger.info("Import contacts successful", extra={"account_id": self.account.id})
            status = "success"
            return {"status": "success", "message": "Contacts imported successfully"}
        
        except RequiredActionFailed as e:
            self.logger.error("Import contacts failed", extra={"account_id": self.account.id})
            status = e.status.name if e.status else "failed"
            return {"status": status, "message": str(e)}
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}", extra={"account_id": self.account.id})
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

            if self.job_id:
                pass
                # from modules.core.job_manager import job_manager
                # job_manager.unregister_browser(self.job_id)
            self.browser.close()

    def import_contacts(self, page: Page):
        """Import contacts using SequentialFlow."""
        state_registry = self._setup_state_handlers()
        
        # Define steps in order
        steps = [
            OpenAddressBookStep(self, self.logger),
            OpenImportPanelStep(self, self.logger),
            SelectSourceStep(self, self.logger),
            UploadFileStep(self, self.logger),
            UploadContactsStep(self, self.logger),
            ImportContactsStep(self, self.logger),
            VerifyImportStep(self, self.logger),
        ]
        
        flow = SequentialFlow(steps, account=self.account, logger=self.logger)
        result = flow.run(page)
        
        if result.status not in (FlowResult.SUCCESS, FlowResult.COMPLETED):
            raise RequiredActionFailed(f"Failed to complete import. Status: {result.status.name}, Message: {result.message}", status=result.status)
        
        self.logger.info("Import contacts completed via SequentialFlow", extra={"account_id": self.account.id})
