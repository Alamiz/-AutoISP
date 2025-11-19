import logging
from playwright.sync_api import Page
from core.browser.browser_helper import PlaywrightBrowserFactory
from core.utils.decorators import retry, RequiredActionFailed
from core.humanization.actions import HumanAction
from core.utils.identifier import identify_page

class GMXAuthentication(HumanAction):
    def __init__(self, email, password):
        super().__init__()
        self.email = email
        self.password = password
        self.logger = logging.getLogger("autoisp")
        self.profile = self.email.split('@')[0]
        self.browser = PlaywrightBrowserFactory(profile_dir=f"Profile_{self.profile}")
        self.login_frame_selector = 'iframe[src^="https://alligator.navigator.gmx.net"]'


    def execute(self) -> bool:
        """
        Runs authentication flow for GMX
        """

        self.logger.info(f"Starting authentication flow for {self.email}")

        try:
            # Start browser
            self.browser.start()

            # Create new page
            page = self.browser.new_page()

            # Authenticate
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

    @retry(max_retries=3, delay=5, required=True)
    def authenticate(self, page: Page):
        """
        Handles authentication flow for GMX
        """

        # Navigate to GMX login page
        page.goto("https://www.gmx.net/")
        self.human.read_delay()

        identified_page = identify_page(page, page.url)
        print("Current page is: ", identified_page)

        # Fill email
        self.human_fill(
            page,
            selectors=['input#username'],
            text=self.email,
            iframe_selector=self.login_frame_selector
        )

        # Click submit
        self.human_click(
            page,
            selectors=['button[type="submit"]'],
            iframe_selector=self.login_frame_selector
        )

        
        # Fill password
        self.human_fill(
            page,
            selectors=['input#password'],
            text=self.password,
            iframe_selector=self.login_frame_selector
        )

        # Final submit
        self.human_click(
            page,
            selectors=['button[type="submit"]'],
            iframe_selector=self.login_frame_selector
        )

        # Wait for success indicator
        page.wait_for_timeout(2000)
        
        self.logger.info(f"GMX authentication completed for {self.email}")

def main(email, password):
    auth = GMXAuthentication(email, password)
    return auth.execute()