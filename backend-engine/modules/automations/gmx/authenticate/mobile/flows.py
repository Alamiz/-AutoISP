import logging
from playwright.sync_api import Page
from core.humanization.actions import HumanAction


class GMXFlowHandler:
    """Handles different GMX page flows"""
    
    def __init__(self, human_action: HumanAction, email: str, password: str):
        self.human_action = human_action
        self.email = email
        self.password = password
        self.logger = logging.getLogger("autoisp")
    
    def handle_register_page(self, page: Page) -> str:
        """
        Handle GMX register page - full authentication flow (mobile)
        Returns: Next expected page identifier
        """
        self.logger.info("Detected register page - starting mobile full authentication")
        
        # Click login button
        self.human_action.human_click(
            page,
            selectors=['form.login-link.login-mobile > button[type="submit"]'],
        )
                
        page.wait_for_timeout(2000)
        self.logger.info("Login button clicked successfully")
        
        return "gmx_login_page"  # Expected next page

    def handle_logged_in_page(self, page: Page) -> str:
        """
        Handle GMX logged in page - full authentication flow (mobile)
        Returns: Next expected page identifier
        """
        self.logger.info("Detected logged in page - starting mobile full authentication")
        
        # Click profile avatar
        self.human_action.human_click(
            page,
            selectors=['div.login-wrapper  > account-avatar'],
        )
                
        page.wait_for_timeout(2000)
        self.logger.info("Profile avatar clicked successfully")
        
        # Click continue to inbox button
        self.human_action.human_click(
            page,
            selectors=['div#appa-account-flyout > section.account-avatar__flyout-content > section.appa-account-avatar__buttons > button:nth-of-type(2)'],
            deep_search=True
        )
                
        page.wait_for_timeout(2000)
        self.logger.info("Continue to inbox button clicked successfully")
        
        return "gmx_folder_list_page"  # Expected next page

    def handle_login_page(self, page: Page) -> str:
        """
        Handle GMX login page - full authentication flow
        Returns: Next expected page identifier
        """
        self.logger.info("Detected login page - starting full authentication")
        
        # Fill email
        self.human_action.human_fill(
            page,
            selectors=['form input#username'],
            text=self.email,
        )
        
        # Click continue
        self.human_action.human_click(
            page,
            selectors=['form button[type="submit"]'],
        )
        
        # Fill password
        self.human_action.human_fill(
            page,
            selectors=['form input#password'],
            text=self.password,
        )
        
        # Click submit
        self.human_action.human_click(
            page,
            selectors=['button[type="submit"][data-testid="button-next"]'],
        )
        
        page.wait_for_timeout(10_000)
        self.logger.info("Login form submitted successfully")
        
        return "gmx_folder_list"  # Expected next page
    
    def handle_folder_list_page(self, page: Page) -> str:
        """
        Handle inbox page - already fully authenticated
        Returns: Current page identifier (no action needed)
        """
        self.logger.info("Already at inbox - authentication complete")
        return "gmx_folder_list"  # Stay on current page
    
    def handle_unknown_page(self, page: Page) -> str:
        """
        Handle unknown page - navigate to login
        Returns: Next expected page identifier
        """
        self.logger.warning("Unknown page detected - navigating to GMX login")
        page.goto("https://lightmailer-bs.gmx.net/")
        self.human_action.human_behavior.read_delay()
        return "gmx_login_page"  # Expected next page