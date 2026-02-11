import logging
import os
from playwright.sync_api import Page
from automations.webde.authenticate.mobile.run import WebDEAuthentication
from core.browser.browser_helper import PlaywrightBrowserFactory
from core.utils.retry_decorators import RequiredActionFailed
from core.humanization.actions import HumanAction
from core.utils.identifier import identify_page
from core.flow_engine.smart_flow import SequentialFlow
from core.flow_engine.state_handler import StateHandlerRegistry
from modules.core.flow_state import FlowResult
from .steps import NavigateToSpamStep, ReportSpamEmailsStep, OpenReportedEmailsStep
from .handlers import UnknownPageHandler
from core.pages_signatures.webde.mobile import PAGE_SIGNATURES
from datetime import datetime
from core.utils.browser_utils import navigate_to

class ReportNotSpam(HumanAction):
    """
    web.de Mobile Report Not Spam using SequentialFlow
    """
    
    def __init__(self, account, user_agent_type="mobile", search_text=None, max_flow_retries=3, start_date=None, end_date=None, job_id=None, log_dir=None):
        super().__init__()
        self.account = account
        self.user_agent_type = user_agent_type
        self.search_text = search_text
        self.max_flow_retries = max_flow_retries
        self.job_id = job_id
        self.log_dir = log_dir
        self.logger = logging.getLogger("autoisp")
        self.profile = self.account.email.split('@')[0]
        self.signatures = PAGE_SIGNATURES
        self.reported_email_ids = []

        self.browser = PlaywrightBrowserFactory(
            profile_dir=f"Profile_{self.profile}",
            account=self.account,
            user_agent_type=user_agent_type,
            job_id=job_id
        )

        # Parse dates
        if start_date:
            try:
                self.start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            except ValueError:
                self.logger.error(f"Invalid start_date format: {start_date}", extra={"account_id": self.account.id})
                self.start_date = datetime(1970, 1, 1).date()
        else:
            self.start_date = datetime(1970, 1, 1).date()

        if end_date:
            try:
                self.end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            except ValueError:
                self.logger.error(f"Invalid end_date format: {end_date}", extra={"account_id": self.account.id})
                self.end_date = datetime.now().date()
        else:
            self.end_date = datetime.now().date()


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

            flow = SequentialFlow(steps, state_registry=state_registry, account=self.account, logger=self.logger)
            result = flow.run(page)
            
            if result.status not in (FlowResult.SUCCESS, FlowResult.COMPLETED):
                return {"status": result.status.name, "message": f"Flow failed with status {result.status.name}: {result.message}", "retry_recommended": True}

            return {
                "status": "success",
                "message": "Reported not spam",
                "emails_processed": len(self.reported_email_ids)
            }

        except Exception as e:
            self.logger.error(f"Exception in flow execution: {e}", extra={"account_id": self.account.id})
            return {"status": "failed", "message": str(e), "retry_recommended": True}

    def execute(self):
        self.logger.info(f"Starting Report Not Spam (Mobile)", extra={"account_id": self.account.id})
        
        flow_attempt = 0
        last_result = None
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
            webde_auth = WebDEAuthentication(
                account=self.account,
                user_agent_type=self.user_agent_type,
                job_id=self.job_id
            )

            try:
                webde_auth.authenticate(page)
            except RequiredActionFailed as e:
                self.logger.error(f"Authentication failed with status {e.status.name if e.status else 'failed'}: {e}", extra={"account_id": self.account.id})
                return {"status": e.status.name if e.status else "failed", "message": str(e)}
            except Exception as e:
                self.logger.error(f"Authentication failed: {e}", extra={"account_id": self.account.id})
                return {"status": "failed", "message": "Authentication failed"}
            
            self.logger.info("Authentication successful", extra={"account_id": self.account.id})

            # Flow-level retry loop
            while flow_attempt < self.max_flow_retries:
                flow_attempt += 1
                
                self.logger.info(f"FLOW ATTEMPT {flow_attempt}/{self.max_flow_retries}", extra={"account_id": self.account.id})
                self.reported_email_ids = []
                
                result = self._execute_flow(page)
                last_result = result
                
                if result["status"] == "success":
                    self.logger.info(f"Flow completed successfully on attempt {flow_attempt}", extra={"account_id": self.account.id})
                    status = "success"
                    return result
                
                if not result.get("retry_recommended", False):
                    return result
                
                if flow_attempt < self.max_flow_retries:
                    wait_time = 5000 * flow_attempt
                    self.logger.info(f"Waiting {wait_time/1000}s before retry...", extra={"account_id": self.account.id})
                    page.wait_for_timeout(wait_time)
                    
                    try:
                        navigate_to(page, "https://alligator.navigator.web.de/go/?targetURI=https://link.web.de/mail/showStartView&ref=link")
                        page.wait_for_load_state("domcontentloaded")
                    except Exception as e:
                        self.logger.warning(f"Failed to reset to main page: {e}", extra={"account_id": self.account.id})
            
            self.logger.error(f"Flow failed after {self.max_flow_retries} attempts", extra={"account_id": self.account.id})
            return {
                "status": last_result.get("status", "failed") if last_result else "failed",
                "message": f"Flow failed after {self.max_flow_retries} attempts",
                "last_error": last_result.get('message') if last_result else None
            }

        except RequiredActionFailed as e:
            self.logger.error(f"Critical error in automation: {e}", extra={"account_id": self.account.id})
            return {"status": e.status.name if e.status else "failed", "message": str(e)}
        except Exception as e:
            self.logger.error(f"Critical error in automation: {e}", extra={"account_id": self.account.id}, exc_info=True)
            return {"status": "failed", "message": f"Critical error: {str(e)}"}
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
