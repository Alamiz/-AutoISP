import logging
from playwright.sync_api import Page
from core.browser.browser_helper import PlaywrightBrowserFactory
from core.humanization.actions import HumanAction
from automations.gmx.authenticate.desktop.run import GMXAuthentication
from core.flow_engine.smart_flow import SequentialFlow
from core.flow_engine.state_handler import StateHandlerRegistry
from .steps import NavigateToSpamStep
from .handlers import (
    UnknownPageHandler,
)
from core.pages_signatures.gmx.desktop import PAGE_SIGNATURES

class ReportNotSpam(HumanAction):
    """
    GMX Report Not Spam automation using step-based flow with state handling
    
    Retry Strategy:
    - Step-level: Each step retries based on max_retries (default: 1)
    - Flow-level: Entire automation can be retried via execute() max_flow_retries parameter
    """
    def __init__(
        self, 
        email, 
        password, 
        proxy_config=None, 
        user_agent_type="desktop", 
        search_text=None,
        max_flow_retries=3,
        job_id=None
    ):
        super().__init__()
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
        """
        Setup state handler registry with all handlers.
        """
        from core.utils.identifier import identify_page
        
        registry = StateHandlerRegistry(
            identifier_func=identify_page,
            signatures=self.signatures,
            logger=self.logger
        )
        
        # Register handlers for different page states
        registry.register("unknown", UnknownPageHandler(logger=self.logger))
        
        return registry

    def _execute_flow(self, page: Page) -> dict:
        """
        Internal method to execute the automation flow once.
        Separated for flow-level retry logic.
        """
        try:
            # Setup state handlers
            state_registry = self._setup_state_handlers()

            # Start the step-based flow with state handling
            # Define steps for the sequential flow
            from .steps import NavigateToSpamStep, ReportSpamEmailsStep, OpenReportedEmailsStep
            from core.flow_engine.smart_flow import SequentialFlow
            
            steps = [
                NavigateToSpamStep(self, self.logger),
                ReportSpamEmailsStep(self, self.logger),
                OpenReportedEmailsStep(self, self.logger)
            ]

            # Start the sequential flow with state handling
            flow = SequentialFlow(steps, state_registry=state_registry, logger=self.logger)
            
            result = flow.run(page)
            
            if result.status.value == "failure":
                return {
                    "status": "failed", 
                    "message": result.message,
                    "retry_recommended": True  # Signal that retry might help
                }

            return {
                "status": "success", 
                "message": "Reported not spam",
                "emails_processed": len(self.reported_email_ids)
            }

        except Exception as e:
            self.logger.error(f"Exception in flow execution: {e}", exc_info=True)
            return {
                "status": "failed", 
                "message": str(e),
                "retry_recommended": True
            }

    def execute(self):
        """
        Execute the automation with flow-level retry logic.
        
        Returns:
            dict: Result with status, message, and metadata
        """
        self.logger.info(f"Starting GMX Report Not Spam for {self.email}")
        self.logger.info(f"Flow retry configuration: max_retries={self.max_flow_retries}")
        
        flow_attempt = 0
        last_result = None
        
        try:
            self.browser.start()
            # Register browser for stop functionality
            if self.job_id:
                from modules.core.job_manager import job_manager
                job_manager.register_browser(self.job_id, self.browser)
            page = self.browser.new_page()

            # Authenticate first (outside retry loop - auth failures are terminal)
            self.logger.info("Authenticating...")
            gmx_auth = GMXAuthentication(
                self.email, 
                self.password, 
                self.proxy_config, 
                self.user_agent_type
            )
            try:
                gmx_auth.authenticate(page)
            except Exception as e:
                self.logger.error(f"Authentication failed: {e}")
                return {"status": "failed", "message": "Authentication failed"}

            self.logger.info("Authentication successful")

            # Flow-level retry loop
            while flow_attempt < self.max_flow_retries:
                flow_attempt += 1
                
                self.logger.info("=" * 60)
                self.logger.info(f"FLOW ATTEMPT {flow_attempt}/{self.max_flow_retries}")
                self.logger.info("=" * 60)
                
                # Reset state for retry
                self.reported_email_ids = []
                
                # Execute the flow
                result = self._execute_flow(page)
                last_result = result
                
                # Check if successful
                if result["status"] == "success":
                    self.logger.info(f"✓ Flow completed successfully on attempt {flow_attempt}")
                    return result
                
                # Check if retry is recommended
                if not result.get("retry_recommended", False):
                    self.logger.error(f"Flow failed with non-retryable error: {result['message']}")
                    return result
                
                # Log retry
                if flow_attempt < self.max_flow_retries:
                    self.logger.warning(
                        f"Flow attempt {flow_attempt} failed: {result['message']}"
                    )
                    self.logger.info(f"Retrying flow (attempt {flow_attempt + 1}/{self.max_flow_retries})...")
                    
                    # Wait before retry (progressive backoff)
                    wait_time = 5000 * flow_attempt
                    self.logger.info(f"Waiting {wait_time/1000}s before retry...")
                    page.wait_for_timeout(wait_time)
                    
                    # Navigate back to inbox for clean retry
                    try:
                        page.goto("https://www.gmx.net/")
                        page.wait_for_load_state("domcontentloaded")
                        page.wait_for_timeout(2000)
                    except Exception as e:
                        self.logger.warning(f"Failed to reset to inbox: {e}")
            
            # All retries exhausted
            self.logger.error(f"Flow failed after {self.max_flow_retries} attempts")
            return {
                "status": "failed",
                "message": f"Flow failed after {self.max_flow_retries} attempts. Last error: {last_result.get('message', 'Unknown')}",
                "attempts": flow_attempt,
                "last_error": last_result.get('message')
            }

        except Exception as e:
            self.logger.error(f"Critical error in automation: {e}", exc_info=True)
            return {
                "status": "failed", 
                "message": f"Critical error: {str(e)}",
                "attempts": flow_attempt
            }
        finally:
            if self.job_id:
                from modules.core.job_manager import job_manager
                job_manager.unregister_browser(self.job_id)
            self.browser.close()

