import logging
from playwright.sync_api import Page
from automations.webde.authenticate.desktop.run import WebDEAuthentication
from core.browser.browser_helper import PlaywrightBrowserFactory
from core.utils.retry_decorators import RequiredActionFailed
from core.humanization.actions import HumanAction
from core.utils.identifier import identify_page
from core.flow_engine.smart_flow import SequentialFlow
from core.flow_engine.state_handler import StateHandlerRegistry
from core.flow_engine.step import StepStatus
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
from core.pages_signatures.webde.desktop import PAGE_SIGNATURES


class ImportContacts(HumanAction):
    """
    web.de Desktop Import Contacts using SequentialFlow
    """
    
    def __init__(self, account_id, email, password, proxy_config=None, user_agent_type="desktop", vcf_file_path=None, job_id=None):
        super().__init__()
        self.account_id = account_id
        self.email = email
        self.password = password
        self.proxy_config = proxy_config
        self.user_agent_type = user_agent_type
        self.vcf_file_path = vcf_file_path
        self.job_id = job_id
        self.logger = logging.getLogger("autoisp")
        self.profile = self.email.split('@')[0]
        self.signatures = PAGE_SIGNATURES

        self.browser = PlaywrightBrowserFactory(
            profile_dir=f"Profile_{self.profile}",
            proxy_config=proxy_config,
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
        self.logger.info(f"Starting Import Contacts for {self.email}")
        
        try:
            self.browser.start()
            if self.job_id:
                from modules.core.job_manager import job_manager
                job_manager.register_browser(self.job_id, self.browser)
            page = self.browser.new_page()
            
            # Authenticate first
            webde_auth = WebDEAuthentication(
                self.account_id,
                self.email, 
                self.password, 
                self.proxy_config,
                self.user_agent_type,
                self.job_id
            )
            webde_auth.authenticate(page)

            # Import contacts using SequentialFlow
            self.import_contacts(page)
            
            self.logger.info(f"Import contacts successful for {self.email}")
            return {"status": "success", "message": "Contacts imported successfully"}
        
        except RequiredActionFailed as e:
            self.logger.error(f"Import contacts failed for {self.email}: {e}")
            return {"status": "failed", "message": str(e)}
        except Exception as e:
            self.logger.error(f"Unexpected error for {self.email}: {e}")
            return {"status": "failed", "message": str(e)}
        finally:
            if self.job_id:
                from modules.core.job_manager import job_manager
                job_manager.unregister_browser(self.job_id)
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
        
        flow = SequentialFlow(steps, logger=self.logger)
        result = flow.run(page)
        
        if result.status == StepStatus.FAILURE:
            raise RequiredActionFailed(f"Failed to complete import. Last error: {result.message}")
        
        self.logger.info("Import contacts completed via SequentialFlow")
