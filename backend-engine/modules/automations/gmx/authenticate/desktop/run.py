import logging
from playwright.sync_api import Page
from core.browser.browser_helper import PlaywrightBrowserFactory
from core.utils.decorators import retry, RequiredActionFailed
from core.humanization.actions import HumanAction
from core.utils.identifier import identify_page
from ..desktop.flows import GMXFlowHandler


class GMXAuthentication(HumanAction):
    """
    State-based GMX authentication orchestrator
    """
    
    # Define the flow map: page_identifier -> handler_method
    FLOW_MAP = {
        "gmx_login_page": "handle_login_page",
        "gmx_logged_in_page": "handle_logged_in_page",
        "gmx_inbox_ads_preferences_popup_1_core": "handle_inbox_ads_preferences_popup_1",
        "gmx_inbox_ads_preferences_popup_1": "handle_inbox_ads_preferences_popup_1",
        "gmx_inbox_ads_preferences_popup_2": "handle_inbox_ads_preferences_popup_2",
        "gmx_inbox_smart_features_popup": "handle_inbox_smart_features_popup",
        "gmx_inbox": "handle_inbox_page",
        "unknown": "handle_unknown_page"
    }
    
    # Define goal states (authentication is complete)
    GOAL_STATES = {"gmx_inbox"}
    
    # Maximum flow iterations to prevent infinite loops
    MAX_FLOW_ITERATIONS = 10
    
    def __init__(self, email, password, proxy_config=None, user_agent_type="desktop", signatures=None):
        super().__init__()
        self.email = email
        self.password = password
        self.proxy_config = proxy_config
        self.user_agent_type = user_agent_type
        self.signatures = signatures
        
        self.logger = logging.getLogger("autoisp")
        self.profile = self.email.split('@')[0]
        
        self.browser = PlaywrightBrowserFactory(
            profile_dir=f"Profile_{self.profile}",
            proxy_config=proxy_config,
            user_agent_type=user_agent_type
        )
        
        # Initialize flow handler
        self.flow_handler = GMXFlowHandler(self, email, password)


    @retry(max_retries=3, delay=5, required=True)
    def execute(self) -> bool:
        """
        Runs authentication flow for GMX
        """
        self.logger.info(f"Starting authentication flow for {self.email}")
        
        # Log proxy usage if configured
        if self.proxy_config:
            proxy_info = f"{self.proxy_config['type']}://{self.proxy_config['host']}:{self.proxy_config['port']}"
            if 'username' in self.proxy_config:
                proxy_info = f"{self.proxy_config['type']}://{self.proxy_config['username']}:***@{self.proxy_config['host']}:{self.proxy_config['port']}"
            self.logger.info(f"Using proxy: {proxy_info}")

        try:
            # Start browser with proxy configuration
            self.browser.start()
            
            # Create new page
            page = self.browser.new_page()
            
            # Authenticate using state-based flow
            self.authenticate(page)
            
            self.logger.info(f"Authentication successful for {self.email}")
            return True
        
        except RequiredActionFailed as e:
            self.logger.error(f"Authentication failed for {self.email}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error for {self.email}: {e}")
            return False
        finally:
            # Close browser
            self.browser.close()

    def authenticate(self, page: Page):
        """
        State-based authentication flow
        Automatically handles different page states until reaching goal state
        """
        # Navigate to GMX
        page.goto("https://www.gmx.net/")
        self.human_behavior.read_delay()
        page.wait_for_timeout(100_100_100)

        current_page_id = identify_page(page, page.url, self.signatures)
        self.logger.info(f"Current page: {current_page_id}")

        iteration = 0
        current_page_id = None
        
        while iteration < self.MAX_FLOW_ITERATIONS: 
            iteration += 1
            
            # Identify current page
            current_page_id = identify_page(page, page.url, self.signatures)
            self.logger.info(f"[Iteration {iteration}] Current page: {current_page_id}")
            
            # Check if we've reached a goal state
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

