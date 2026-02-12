import logging
import time
from playwright.sync_api import Page
from core.browser.browser_helper import PlaywrightBrowserFactory
from core.humanization.actions import HumanAction
from core.utils.browser_utils import navigate_to

class OpenProfile(HumanAction):
    """
    Simple automation to open the browser with the user's profile for Libero.
    """
    
    def __init__(self, account, user_agent_type="desktop", duration=10, job_id=None):
        super().__init__()
        self.duration = duration
        self.account = account
        self.user_agent_type = user_agent_type
        self.job_id = job_id
        self.logger = logging.getLogger("autoisp")
        self.profile = self.account.email.split('@')[0]
        
        self.browser = PlaywrightBrowserFactory(
            profile_dir=f"Profile_{self.profile}",
            account=self.account,
            user_agent_type=user_agent_type,
            job_id=job_id
        )

    def execute(self):
        """
        Opens the browser and navigates to the homepage.
        """
        self.logger.info(f"Opening profile for {self.account.email}", extra={"account_id": self.account.id})
        
        try:
            self.browser.start()
            if self.job_id:
                pass
                # job_manager.register_browser(self.job_id, self.browser)
            page = self.browser.new_page()
            
            # Navigate to Libero mail
            navigate_to(page, "https://login.libero.it/")
            
            self.logger.info("Profile opened. Waiting for manual interaction...")
            
            # Keep open for the specified duration or until closed
            # duration is in minutes
            page.wait_for_timeout(int(self.duration) * 60 * 1000)
            
            return {"status": "success", "message": "Profile opened"}
        
        except Exception as e:
            self.logger.error(f"Error opening profile: {e}", extra={"account_id": self.account.id})
            return {"status": "failed", "message": str(e)}
        finally:
            if self.job_id:
                pass
                # job_manager.unregister_browser(self.job_id)
            self.browser.close()
