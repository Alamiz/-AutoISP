import logging
import time
from playwright.sync_api import Page
from core.browser.browser_helper import PlaywrightBrowserFactory
from core.humanization.actions import HumanAction
from core.utils.browser_utils import navigate_to

class OpenProfile(HumanAction):
    """
    Simple automation to open the browser with the user's profile.
    """
    
    def __init__(self, email, password, proxy_config=None, user_agent_type="desktop", duration=10, job_id=None):
        super().__init__()
        self.duration = duration
        self.email = email
        self.password = password
        self.proxy_config = proxy_config
        self.user_agent_type = user_agent_type
        self.job_id = job_id
        self.logger = logging.getLogger("autoisp")
        self.profile = self.email.split('@')[0]
        
        self.browser = PlaywrightBrowserFactory(
            profile_dir=f"Profile_{self.profile}",
            proxy_config=proxy_config,
            user_agent_type=user_agent_type
        )

    def execute(self):
        """
        Opens the browser and navigates to the homepage.
        """
        from modules.core.job_manager import job_manager
        
        self.logger.info(f"Opening profile for {self.email}")
        
        try:
            self.browser.start()
            if self.job_id:
                job_manager.register_browser(self.job_id, self.browser)
            page = self.browser.new_page()
            
            navigate_to(page, "https://www.gmx.net/")
            
            self.logger.info("Profile opened. Waiting for manual interaction...")
            
            # Keep open for the specified duration or until closed
            page.wait_for_timeout(int(self.duration)* 60 * 1000)
            
            return {"status": "success", "message": "Profile opened"}
        
        except Exception as e:
            self.logger.error(f"Error opening profile: {e}")
            return {"status": "failed", "message": str(e)}
        finally:
            if self.job_id:
                job_manager.unregister_browser(self.job_id)
            self.browser.close()

