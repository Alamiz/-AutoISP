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
from .steps import NavigateToSpamStep, ReportSpamEmailsStep, OpenReportedEmailsStep
from .handlers import UnknownPageHandler
from core.pages_signatures.webde.desktop import PAGE_SIGNATURES


class ReportNotSpam(HumanAction):
    """
    web.de Desktop Report Not Spam using SequentialFlow
    """
    
    def __init__(self, email, password, proxy_config=None, user_agent_type="desktop", search_text=None, job_id=None):
        super().__init__()
        self.email = email
        self.password = password
        self.proxy_config = proxy_config
        self.user_agent_type = user_agent_type
        self.search_text = search_text
        self.job_id = job_id
        self.logger = logging.getLogger("autoisp")
        self.profile = self.email.split('@')[0]
        self.signatures = PAGE_SIGNATURES
        self.reported_email_ids = []

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
        self.logger.info(f"Starting Report Not Spam for {self.email}")
        
        try:
            self.browser.start()
            if self.job_id:
                from modules.core.job_manager import job_manager
                job_manager.register_browser(self.job_id, self.browser)
            page = self.browser.new_page()
            
            # Authenticate first
            webde_auth = WebDEAuthentication(
                self.email, 
                self.password, 
                self.proxy_config,
                self.user_agent_type
            )
            webde_auth.authenticate(page)

            # Report not spam using SequentialFlow
            self.report_not_spam(page)
            
            self.logger.info(f"Report not spam successful for {self.email}")
            return {"status": "success", "message": "Reported not spam"}
        
        except RequiredActionFailed as e:
            self.logger.error(f"Report not spam failed for {self.email}: {e}")
            return {"status": "failed", "message": str(e)}
        except Exception as e:
            self.logger.error(f"Unexpected error for {self.email}: {e}")
            return {"status": "failed", "message": str(e)}
        finally:
            if self.job_id:
                from modules.core.job_manager import job_manager
                job_manager.unregister_browser(self.job_id)
            self.browser.close()

    def report_not_spam(self, page: Page):
        """Report not spam using SequentialFlow."""
        state_registry = self._setup_state_handlers()
        
        # Define steps in order
        steps = [
            NavigateToSpamStep(self, self.logger),
            ReportSpamEmailsStep(self, self.logger),
            OpenReportedEmailsStep(self, self.logger),
        ]
        
        flow = SequentialFlow(steps, state_registry=state_registry, logger=self.logger)
        result = flow.run(page)
        
        if result.status == StepStatus.FAILURE:
            raise RequiredActionFailed(f"Failed to complete report. Last error: {result.message}")
        
        self.logger.info("Report not spam completed via SequentialFlow")
