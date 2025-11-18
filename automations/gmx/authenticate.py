import logging
from core.browser_helper import PlaywrightBrowserFactory
from core.utils import retry, RequiredActionFailed, find_element_in_frame

class GMXAuthentication:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.logger = logging.getLogger("autoisp")
        self.profile = self.email.split('@')[0]
        self.browser = PlaywrightBrowserFactory(profile_dir=f"Profile_{self.profile}")

    def run(self) -> bool:
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
    def authenticate(self, page):

        iframe_selector = 'iframe[src^="https://alligator.navigator.gmx.net"]'

        # Navigate to GMX login page
        page.goto("https://www.gmx.net/")

        email_field_selectors = [
            "input#username"
        ]

        email_input = find_element_in_frame(page, email_field_selectors, iframe_selector)
        email_input.fill(self.email)

        submit_button_selectors = [
            'button[type="submit"]'
        ]

        submit_button = find_element_in_frame(page, submit_button_selectors, iframe_selector)
        submit_button.click()
        
        password_field_selectors = [
            "input#password"
        ]

        password_input = find_element_in_frame(page, password_field_selectors, iframe_selector)
        password_input.fill(self.password)

        submit_button = find_element_in_frame(page, submit_button_selectors, iframe_selector)
        submit_button.click()

        page.wait_for_timeout(150_000_000)

def main(email, password):
    auth = GMXAuthentication(email, password)
    return auth.run()