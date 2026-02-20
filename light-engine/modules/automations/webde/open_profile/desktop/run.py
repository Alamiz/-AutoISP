import logging
import time
from playwright.async_api import Page
from core.browser.browser_helper import PlaywrightBrowserFactory
from core.humanization.actions import HumanAction
from core.utils.browser_utils import navigate_to

class OpenProfile(HumanAction):
    """
    Simple automation to open the browser with the user's profile.
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

    async def execute(self):
        self.logger.info("Opening profile", extra={"account_id": self.account.id})
        
        try:
            await self.browser.start()
            page = await self.browser.new_page()
            
            await navigate_to(page, "https://alligator.navigator.web.de/go/?targetURI=https://link.web.de/mail/showStartView&ref=link")
            
            self.logger.info("Profile opened. Waiting for manual interaction...", extra={"account_id": self.account.id})
            
            # Keep open for duration minutes
            await page.wait_for_timeout(int(self.duration) * 60 * 1000) 
            
            return {"status": "success", "message": "Profile opened"}
        
        except Exception as e:
            self.logger.error("Error opening profile", extra={"account_id": self.account.id})
            return {"status": "failed", "message": str(e)}
        finally:
            await self.browser.close()
