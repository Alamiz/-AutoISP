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
    
    def handle_login_page(self, page: Page) -> str:
        """
        Handle GMX login page - full authentication flow
        Returns: Next expected page identifier
        """
        self.logger.info("Detected login page - starting full authentication")
        
        # Fill email
        self.human_action.human_fill(
            page,
            selectors=['input#username'],
            text=self.email,
            deep_search=True
        )
        
        # Click continue
        self.human_action.human_click(
            page,
            selectors=['button[type="submit"][data-testid="button-continue"]'],
            deep_search=True
        )
        
        # Fill password
        self.human_action.human_fill(
            page,
            selectors=['input#password'],
            text=self.password,
            deep_search=True
        )
        
        # Click submit
        self.human_action.human_click(
            page,
            selectors=['button[type="submit"][data-testid="button-submit"]'],
            deep_search=True
        )
        
        page.wait_for_timeout(2000)
        self.logger.info("Login form submitted successfully")
        
        return "gmx_logged_in_page"  # Expected next page
    
    def handle_logged_in_page(self, page: Page) -> str:
        """
        Handle already authenticated page - just click continue
        Returns: Next expected page identifier
        """
        self.logger.info("Detected logged-in page - clicking continue button")
        
        self.human_action.human_click(
            page,
            selectors=["button[data-component-path='openInbox.continue-button']"],
            deep_search=True
        )
        
        self.logger.info("Continue button clicked successfully")
        page.wait_for_timeout(10_000)
        
        return "gmx_inbox"  # Expected next page

    def handle_inbox_ads_preferences_popup_1(self, page: Page) -> str:
        """
        Handle inbox page with ads preferences popup (type 1)
        Returns: Next expected page identifier
        """
        self.logger.info("Detected preferences popup (type 1) - clicking accept button")
        
        self.human_action.human_click(
            page,
            selectors=["button#save-all-pur"],
            deep_search=True
        )
        
        page.wait_for_timeout(1500)
        self.logger.info("Accept button clicked successfully")
        
        return "gmx_inbox"  # Expected next page

    def handle_inbox_ads_preferences_popup_2(self, page: Page) -> str:
        """
        Handle inbox page with ads preferences popup (type 2)
        Returns: Next expected page identifier
        """
        self.logger.info("Detected preferences popup (type 2) - clicking deny button")
        
        self.human_action.human_click(
            page,
            selectors=["button#deny"],
            deep_search=True
        )
        
        page.wait_for_timeout(1500)
        self.logger.info("Continue button clicked successfully")
        
        return "gmx_inbox"  # Expected next page
    
    def handle_inbox_smart_features_popup(self, page: Page) -> str:
        """
        Handle inbox page with smart fetures popup
        Returns: Next expected page identifier
        """
        self.logger.info("Detected smart features popup - clicking accept button")
        
        self.human_action.human_click(
            page,
            selectors=['button[data-component-path="acceptall-button"]'],
            deep_search=True
        )
        page.wait_for_timeout(1500)
        self.logger.info("Accept button clicked successfully")

        page.reload()
        
        return "gmx_inbox"  # Expected next page
    
    def handle_inbox_page(self, page: Page) -> str:
        """
        Handle inbox page - already fully authenticated
        Returns: Current page identifier (no action needed)
        """
        self.logger.info("Already at inbox - authentication complete")
        return "gmx_inbox"  # Stay on current page
    
    def handle_unknown_page(self, page: Page) -> str:
        """
        Handle unknown page - navigate to login
        Returns: Next expected page identifier
        """
        self.logger.warning("Unknown page detected - navigating to GMX login")
        page.goto("https://www.gmx.net/")
        self.human_action.human_behavior.read_delay()
        return "gmx_login_page"  # Expected next page