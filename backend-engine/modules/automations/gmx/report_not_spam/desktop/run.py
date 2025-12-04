# automations/gmx/report_not_spam/desktop/run.py
import logging
from playwright.sync_api import Page
from core.browser.browser_helper import PlaywrightBrowserFactory
from core.humanization.actions import HumanAction
from automations.gmx.authenticate.desktop.run import GMXAuthentication
from core.flow_engine.runner import StepRunner
from .steps import NavigateToSpamStep, HandleUnknownPageStep
from automations.gmx.signatures.desktop import PAGE_SIGNATURES

class ReportNotSpam(HumanAction):
    """
    GMX Report Not Spam automation using step-based flow
    """
    def __init__(self, email, password, proxy_config=None, user_agent_type="desktop", search_text=None):
        super().__init__()
        self.email = email
        self.password = password
        self.proxy_config = proxy_config
        self.user_agent_type = user_agent_type
        self.search_text = search_text
        self.logger = logging.getLogger("autoisp")
        self.profile = self.email.split('@')[0]
        self.signatures = PAGE_SIGNATURES
        self.reported_email_ids = []

        self.browser = PlaywrightBrowserFactory(
            profile_dir=f"Profile_{self.profile}",
            proxy_config=proxy_config,
            user_agent_type=user_agent_type
        )

        # Human behavior helper
        self.human_action = self

    def execute(self):
        self.logger.info(f"Starting GMX Report Not Spam for {self.email}")
        try:
            self.browser.start()
            page = self.browser.new_page()

            # Authenticate first
            gmx_auth = GMXAuthentication(
                self.email, self.password, self.proxy_config, self.user_agent_type, signatures=self.signatures
            )
            gmx_auth.authenticate(page)

            # Start the step-based flow
            # ✅ Don't pass page to constructor - steps receive it in run()
            start_step = NavigateToSpamStep(self, self.logger)
            runner = StepRunner(start_step)
            
            # ✅ Pass page to run() method
            result = runner.run(page)
            
            if result.status.value == "failure":
                self.logger.error(f"Flow failed: {result.message}")
                return {"status": "error", "message": result.message}

            self.logger.info(f"Report Not Spam completed for {self.email}")
            return {"status": "success", "message": "Reported not spam"}

        except Exception as e:
            self.logger.error(f"Error in Report Not Spam: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            self.browser.close()