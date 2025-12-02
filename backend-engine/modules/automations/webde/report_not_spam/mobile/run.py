import logging
from playwright.sync_api import Page
from automations.webde.authenticate.mobile.run import WebDEAuthentication
from core.browser.browser_helper import PlaywrightBrowserFactory
from core.utils.decorators import retry, RequiredActionFailed
from core.humanization.actions import HumanAction
from core.utils.identifier import identify_page
from .flows import ReportNotSpamFlowHandler
from automations.webde.signatures.mobile import PAGE_SIGNATURES

class ReportNotSpam(HumanAction):
    """
    State-based WebDE mobile report not spam orchestrator
    """
    
    # Define the flow map: page_identifier -> handler_method
    FLOW_MAP = {
        "webde_folder_list_page": "handle_folder_list_page",
        "webde_spam": "handle_spam_page",
        "unknown": "handle_unknown_page"
    }
    
    # Define goal states (report not spam is complete)
    GOAL_STATES = {"task_completed"}
    
    # Maximum flow iterations to prevent infinite loops
    MAX_FLOW_ITERATIONS = 15
    
    def __init__(self, email, password, proxy_config=None, user_agent_type="mobile", search_text=None):
        super().__init__()
        self.email = email
        self.password = password
        self.proxy_config = proxy_config
        self.user_agent_type = user_agent_type
        self.search_text = search_text
        self.logger = logging.getLogger("autoisp")
        self.profile = self.email.split('@')[0]
        self.signatures = PAGE_SIGNATURES
        self.action_completed = False

        self.browser = PlaywrightBrowserFactory(
            profile_dir=f"Profile_{self.profile}",
            proxy_config=proxy_config,
            user_agent_type=user_agent_type
        )
        
        # Initialize flow handler
        self.flow_handler = ReportNotSpamFlowHandler(self, email, password, search_text)

    @retry(max_retries=3, delay=5, required=True)
    def execute(self):
        self.logger.info(f"Starting Report Not Spam (Mobile) for {self.email}")
        
        try:
            # Start browser with proxy configuration
            self.browser.start()
            
            # Create new page
            page = self.browser.new_page()
            
            # Authenticate first
            webde_auth = WebDEAuthentication(self.email, self.password, self.proxy_config, self.user_agent_type, signatures=self.signatures)
            webde_auth.authenticate(page)

            # Report not spam using state-based flow
            self.report_not_spam(page)
            
            self.logger.info(f"Report not spam successful for {self.email}")
            return {"status": "success", "message": "Reported not spam"}
        
        except RequiredActionFailed as e:
            self.logger.error(f"Report not spam failed for {self.email}: {e}")
            return {"status": "failed", "message": str(e)}
        except Exception as e:
            self.logger.error(f"Unexpected error for {self.email}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            # Close browser
            self.browser.close()

    def report_not_spam(self, page: Page):
        """
        State-based report not spam flow
        Automatically handles different page states until reaching goal state
        """
        # We assume we are already authenticated
        
        iteration = 0
        current_page_id = None
        
        while iteration < self.MAX_FLOW_ITERATIONS:
            iteration += 1
            
            # Identify current page
            page.wait_for_timeout(2_000)
            current_page_id = identify_page(page, page.url, self.signatures)
            
            # Override state if action is completed
            if self.action_completed:
                current_page_id = "task_completed"
                
            self.logger.info(f"[Iteration {iteration}] Current page: {current_page_id}")
            
            # Check if we've reached goal state
            if current_page_id in self.GOAL_STATES:
                self.logger.info(f"Goal state reached: {current_page_id}")
                return
            
            # Get the handler method for this page
            handler_method_name = self.FLOW_MAP.get(current_page_id, "handle_unknown_page")
            handler_method = getattr(self.flow_handler, handler_method_name)
            
            # Execute the handler
            expected_next_page = handler_method(page)
            self.logger.info(f"Executed handler: {handler_method_name}, expecting: {expected_next_page}")
            
            # Wait for page transition
            page.wait_for_load_state("load")
            self.human_behavior.read_delay()
        
        # If we exit the loop without reaching goal state
        raise RequiredActionFailed(
            f"Failed to reach goal state after {self.MAX_FLOW_ITERATIONS} iterations. "
            f"Last page: {current_page_id}"
        )
