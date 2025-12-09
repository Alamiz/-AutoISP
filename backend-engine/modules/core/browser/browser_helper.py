from playwright.sync_api import sync_playwright, BrowserContext, Page
from core.browser.chrome_profiles_manager import ChromeProfileManager
import os
from typing import Optional, List, Dict

STEALTH_INIT_SCRIPT = """
// Minimal evasions for navigator properties commonly checked
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3,4,5] });

// Provide minimal chrome object shape expected by some sites
window.chrome = window.chrome || { runtime: {} };

// Overwrite permissions query to avoid "denied" anomalies
const originalQuery = navigator.permissions && navigator.permissions.query;
if (originalQuery) {
  navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
      Promise.resolve({ state: Notification.permission }) :
      originalQuery(parameters)
  );
}
"""

class PlaywrightBrowserFactory:
    """
    Helper to create a Playwright persistent Chrome context with
    common stealth patches and human-like helpers.

    Notes:
      - Pass a path to a real Chrome profile (a profile you used manually) to reduce detection.
      - This reduces some detectable signals but does NOT guarantee undetectability.
      - Prefer official APIs (e.g., Gmail API) for account automation.
    """

    def __init__(
        self,
        profile_dir: str,
        channel: str = "chrome",
        headless: bool = False,
        executable_path: Optional[str] = None,
        additional_args: Optional[List[str]] = None,
        use_stealth: bool = True,
        start_maximized: bool = True,
        slow_mo: Optional[int] = None,
        proxy_config: Optional[Dict] = None,
        user_agent_type: str = "desktop",  # "desktop" or "mobile"
    ):
        self.profile_path = os.path.join(ChromeProfileManager().chrome_data_path, profile_dir)
        self.profile_dir = profile_dir
        self.channel = channel
        self.headless = headless
        self.executable_path = executable_path
        self.additional_args = additional_args or []
        self.use_stealth = use_stealth
        self.start_maximized = start_maximized
        self.slow_mo = slow_mo
        self.proxy_config = proxy_config
        self.user_agent_type = user_agent_type

        self._pw = None
        self._context: Optional[BrowserContext] = None
        self._opened = False

    def start(self):
        """Start browser with extension"""
        if self._opened:
            return
            
        print(f"🚀 Starting browser with {self.user_agent_type} user agent...")

        os.makedirs(self.profile_path, exist_ok=True)
        self._pw = sync_playwright().start()
        
        args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--no-default-browser-check",
            "--disable-dev-shm-usage",
        ]

        # Only start maximized for desktop
        if self.user_agent_type == "desktop":
            args.append("--start-maximized")
        
        launch_kwargs = dict(
            user_data_dir=self.profile_path,
            channel=self.channel,
            headless=self.headless,
            args=args,
            ignore_default_args=["--enable-automation"],
            user_agent=self._get_user_agent()
        )
        
        # Proxy configuration
        if self.proxy_config:
            proxy_settings = {
                'server': f"{self.proxy_config['protocol']}://{self.proxy_config['host']}:{self.proxy_config['port']}"
            }
            
            if 'username' in self.proxy_config and 'password' in self.proxy_config:
                proxy_settings['username'] = self.proxy_config['username']
                proxy_settings['password'] = self.proxy_config['password']
            
            launch_kwargs['proxy'] = proxy_settings
        
        try:
            self._context = self._pw.chromium.launch_persistent_context(**launch_kwargs)
            print("✅ Browser started successfully")

            self._opened = True
            
        except Exception as e:
            print(f"❌ Failed to start browser: {e}")
            raise
        
    def _get_user_agent(self):
        """Get user agent string based on type"""
        user_agents = {
            "desktop": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.90 Safari/537.36",
            "mobile": "Mozilla/5.0 (Linux; Android 12; Redmi Note 11 Build/SKQ1.211019.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/99.0.4844.88 Mobile Safari/537.36"
        }
        return user_agents.get(self.user_agent_type, user_agents["desktop"])

    def _get_mobile_viewport(self):
        """Get mobile viewport dimensions"""
        mobile_viewports = {
            "iphone_12": {"width": 390, "height": 844},
            "samsung_galaxy": {"width": 412, "height": 915},
            "pixel_5": {"width": 393, "height": 851},
        }
        # Using samsung galaxy dimensions as default
        return mobile_viewports["samsung_galaxy"]

    def get_page(self) -> Page:
        if not self._opened:
            self.start()
        pages = self._context.pages
        page = pages[0] if pages else self._context.new_page()
        
        # Set viewport for mobile after page is created
        if self.user_agent_type == "mobile":
            mobile_viewport = self._get_mobile_viewport()
            page.set_viewport_size(mobile_viewport)
            print(f"✅ Mobile viewport set: {mobile_viewport['width']}x{mobile_viewport['height']}")
        
        return page

    def new_page(self) -> Page:
        if not self._opened:
            self.start()
        page = self._context.new_page()
        
        # Set viewport for mobile after page is created
        if self.user_agent_type == "mobile":
            mobile_viewport = self._get_mobile_viewport()
            page.set_viewport_size(mobile_viewport)
            print(f"✅ Mobile viewport set: {mobile_viewport['width']}x{mobile_viewport['height']}")
        
        return page

    def close(self):
        """Close context and stop Playwright."""
        if self._context:
            try:
                self._context.close()
            except Exception:
                pass
            self._context = None
        if self._pw:
            try:
                self._pw.stop()
            except Exception:
                pass
            self._pw = None
        self._opened = False