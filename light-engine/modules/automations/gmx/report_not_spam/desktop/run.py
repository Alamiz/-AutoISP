import logging
import random
from playwright.async_api import Page, Error as PlaywrightError
from core.browser.browser_helper import PlaywrightBrowserFactory
from modules.automations.gmx.authenticate.desktop.run import GMXAuthentication
from core.utils.retry_decorators import RequiredActionFailed
from core.utils.exceptions import JobCancelledException, AccountSuspendedError
from core.flow_engine.smart_flow import SequentialFlow, FlowResult
from core.flow_engine.state_handler import StateHandlerRegistry
from core.utils.identifier import identify_page
from core.pages_signatures.gmx.desktop import PAGE_SIGNATURES

from .steps import NavigateToSpamStep, ReportSpamEmailsStep, OpenReportedEmailsStep
from .handlers import UnknownPageHandler
# from crud.account import update_account_state

class ReportNotSpam:
    """
    Orchestrates the 'Report Not Spam' automation for GMX Desktop.
    """
    
    def __init__(self, account, job_id=None, **kwargs):
        self.account = account
        self.job_id = job_id
        self.kwargs = kwargs
        
        self.logger = logging.getLogger("autoisp")
        self.profile = self.account.email.split('@')[0]
        
        # Inject kwargs into self for steps to access
        for key, value in kwargs.items():
            setattr(self, key, value)
            
        self.browser = PlaywrightBrowserFactory(
            profile_dir=f"Profile_{self.profile}",
            account=self.account,
            user_agent_type="desktop",
            job_id=job_id
        )

    async def execute(self):
        # from modules.core.job_manager import job_manager
        
        self.logger.info(f"Starting Report Not Spam (Desktop)", extra={"account_id": self.account.id})
        
        try:
            await self.browser.start()
            
            if self.job_id:
                pass
                # job_manager.register_browser(self.job_id, self.browser)

            page = await self.browser.new_page()

            # 1. Authenticate
            gmx_auth = GMXAuthentication(account=self.account, job_id=self.job_id)
            await gmx_auth.authenticate(page)
            
            # 2. Run Report Not Spam Flow
            await self.report_not_spam(page)
            
            self.logger.info(f"Report Not Spam completed successfully", extra={"account_id": self.account.id})
            return {"status": "success", "message": "Report Not Spam completed"}

        except JobCancelledException:
            raise
        except AccountSuspendedError as e:
            self.logger.warning(f"Account suspended: {e}", extra={"account_id": self.account.id})
            # update_account_state(self.account.id, "suspended")
            return {"status": "failed", "message": f"Account suspended: {e}"}
        except Exception as e:
            self.logger.error(f"Automation failed: {e}", extra={"account_id": self.account.id})
            return {"status": "failed", "message": str(e)}
        finally:
            if self.job_id:
                pass
                # job_manager.unregister_browser(self.job_id)
            await self.browser.close()

    async def report_not_spam(self, page: Page):
        """
        Executes the specific steps to report emails as not spam.
        """
        # Register handlers used during this flow
        state_registry = StateHandlerRegistry(identify_page, PAGE_SIGNATURES, self.logger)
        state_registry.register("unknown", UnknownPageHandler(self, self.logger))

        # Define the sequence of steps
        # Can be dynamic based on user settings
        steps = []
        
        # If keywords are provided, we look for emails
        if hasattr(self, "search_text") and self.search_text:
             # Decide strategy? For now default:
             # 1. Check Spam for keywords -> Report Not Spam
             # 2. Check Inbox/All for keywords -> Open/Star/Reply etc
             
             steps.append(NavigateToSpamStep(self.account, self.logger))
             steps.append(ReportSpamEmailsStep(self.account, self.logger))
             steps.append(OpenReportedEmailsStep(self.account, self.logger))

        if not steps:
            self.logger.info("No steps configured for ReportNotSpam", extra={"account_id": self.account.id})
            return

        flow = SequentialFlow(steps, state_registry=state_registry, account=self.account, logger=self.logger)
        result = await flow.run(page)
        
        if result.status == FlowResult.ABORT:
            raise RequiredActionFailed(f"Flow aborted: {result.message}", status=result.status)
        if result.status == FlowResult.FAIL:
             raise Exception(f"Flow failed: {result.message}")
