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
        """
        Opens the browser and navigates to the homepage.
        Keeps running for a bit or until closed? 
        Actually, run_automation is usually a background task.
        If we want to keep it open for the user, we might need a different approach or just wait long enough.
        But usually 'Open Profile' implies the user wants to interact.
        
        If we return, the browser might close if we use context managers or if the object is garbage collected.
        PlaywrightBrowserFactory.start() starts it.
        
        If we want to keep it open, we should probably just wait in a loop or sleep.
        Let's sleep for a long time or until closed manually.
        """
        self.logger.info(f"Opening profile for {self.email}")
        
        try:
            self.browser.start()
            page = self.browser.new_page()
            
            page.goto("https://www.gmx.net/")
            
            self.logger.info("Profile opened. Waiting for manual interaction...")
            
            # Keep open for the specified duration or until closed
            page.wait_for_timeout(int(self.duration)* 60 * 1000)
            
            return {"status": "success", "message": "Profile opened"}
        
        except Exception as e:
            self.logger.error(f"Error opening profile: {e}")
            return {"status": "failed", "message": str(e)}
        finally:
            self.browser.close()
