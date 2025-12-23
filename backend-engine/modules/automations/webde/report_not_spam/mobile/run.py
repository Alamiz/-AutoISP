import logging
from playwright.sync_api import Page
from automations.webde.authenticate.mobile.run import WebDEAuthentication
from core.browser.browser_helper import PlaywrightBrowserFactory
from core.utils.retry_decorators import RequiredActionFailed
from core.humanization.actions import HumanAction
from core.utils.identifier import identify_page
from core.flow_engine.smart_flow import SequentialFlow
from core.flow_engine.state_handler import StateHandlerRegistry
from core.flow_engine.step import StepStatus
from .steps import NavigateToSpamStep, ReportSpamEmailsStep, OpenReportedEmailsStep
from .handlers import UnknownPageHandler
from core.pages_signatures.webde.mobile import PAGE_SIGNATURES

class ReportNotSpam(HumanAction):
    """
    web.de Mobile Report Not Spam using SequentialFlow
    """
    
    def __init__(self, account_id, email, password, proxy_config=None, user_agent_type="mobile", search_text=None, max_flow_retries=3, job_id=None):
        super().__init__()
        self.account_id = account_id
        self.email = email
        self.password = password
        self.proxy_config = proxy_config
        self.user_agent_type = user_agent_type
        self.search_text = search_text
        self.max_flow_retries = max_flow_retries
        self.job_id = job_id
        self.logger = logging.getLogger("autoisp")
        self.profile = self.email.split('@')[0]
        self.signatures = PAGE_SIGNATURES
        self.reported_email_ids = []

        self.browser = PlaywrightBrowserFactory(
            profile_dir=f"Profile_{self.profile}",
            proxy_config=proxy_config,
            user_agent_type=user_agent_type
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

    def _execute_flow(self, page: Page) -> dict:
        """Execute the automation flow using SequentialFlow."""
        try:
            state_registry = self._setup_state_handlers()

            steps = [
                NavigateToSpamStep(self, self.logger),
                ReportSpamEmailsStep(self, self.logger),
                OpenReportedEmailsStep(self, self.logger),
            ]

            flow = SequentialFlow(steps, state_registry=state_registry, logger=self.logger)
            result = flow.run(page)
            
            if result.status == StepStatus.FAILURE:
                return {"status": "failed", "message": result.message, "retry_recommended": True}

            return {
                "status": "success",
                "message": "Reported not spam",
                "emails_processed": len(self.reported_email_ids)
            }

        except Exception as e:
            self.logger.error(f"Exception in flow execution: {e}", exc_info=True)
            return {"status": "failed", "message": str(e), "retry_recommended": True}

    def execute(self):
        self.logger.info(f"Starting Report Not Spam (Mobile) for {self.email}")
        
        flow_attempt = 0
        last_result = None
        
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

            try:
                webde_auth.authenticate(page)
            except Exception as e:
                self.logger.error(f"Authentication failed: {e}")
                return {"status": "failed", "message": "Authentication failed"}
            
            self.logger.info("Authentication successful")

            # Flow-level retry loop
            while flow_attempt < self.max_flow_retries:
                flow_attempt += 1
                
                self.logger.info(f"FLOW ATTEMPT {flow_attempt}/{self.max_flow_retries}")
                self.reported_email_ids = []
                
                result = self._execute_flow(page)
                last_result = result
                
                if result["status"] == "success":
                    self.logger.info(f"Flow completed successfully on attempt {flow_attempt}")
                    return result
                
                if not result.get("retry_recommended", False):
                    return result
                
                if flow_attempt < self.max_flow_retries:
                    wait_time = 5000 * flow_attempt
                    self.logger.info(f"Waiting {wait_time/1000}s before retry...")
                    page.wait_for_timeout(wait_time)
                    
                    try:
                        page.goto("https://lightmailer-bs.web.de/")
                        page.wait_for_load_state("domcontentloaded")
                    except Exception as e:
                        self.logger.warning(f"Failed to reset to main page: {e}")
            
            self.logger.error(f"Flow failed after {self.max_flow_retries} attempts")
            return {
                "status": "failed",
                "message": f"Flow failed after {self.max_flow_retries} attempts",
                "last_error": last_result.get('message') if last_result else None
            }

        except Exception as e:
            self.logger.error(f"Critical error in automation: {e}", exc_info=True)
            return {"status": "failed", "message": f"Critical error: {str(e)}"}
        finally:
            if self.job_id:
                from modules.core.job_manager import job_manager
                job_manager.unregister_browser(self.job_id)
            self.browser.close()
