import logging
import time
from playwright.sync_api import Page
from core.browser.browser_helper import PlaywrightBrowserFactory
from core.humanization.actions import HumanAction

class OpenProfile(HumanAction):
    """
    Simple automation to open the browser with the user's profile.
    """
    
    def __init__(self, email, password, proxy_config=None, user_agent_type="desktop", duration=10):
        super().__init__()
        self.duration = duration
        self.email = email
        self.password = password
        self.proxy_config = proxy_config
        self.user_agent_type = user_agent_type
        self.logger = logging.getLogger("autoisp")
        self.profile = self.email.split('@')[0]
        
        self.browser = PlaywrightBrowserFactory(
            profile_dir=f"Profile_{self.profile}",
            proxy_config=proxy_config,
            user_agent_type=user_agent_type
        )

    def execute(self):
        self.logger.info(f"Opening profile for {self.email}")
        
        try:
            self.browser.start()
            page = self.browser.new_page()
            
            page.goto("https://web.de/")
            
            self.logger.info("Profile opened. Waiting for manual interaction...")
            
            # Keep open for duration minutes
            page.wait_for_timeout(self.duration * 60 * 1000) 
            
            return {"status": "success", "message": "Profile opened"}
        
        except Exception as e:
            self.logger.error(f"Error opening profile: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            self.browser.close()
