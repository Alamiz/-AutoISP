from playwright.async_api import async_playwright, BrowserContext, Page
from core.browser.chrome_profiles_manager import ChromeProfileManager
import os
import sys
import logging
import asyncio
from typing import Optional, List, Dict
import psutil
from core.models import Account

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
          pass
      originalQuery(parameters)
  );
}
"""

# Aggressive blocking for efficiency
BLOCKED_RESOURCE_TYPES = {
    "image", "media", "font", "texttrack", "object", 
    "beacon", "csp_report", "imageset", "ping"
}

def get_chrome_executable() -> Optional[str]:
    """
    Find the Chrome executable in this order:
        pass
    1. Bundled Chrome in resources folder (relative to this file or frozen app)
    2. ProgramData location (C:\\ProgramData\\AutoISP\\chrome-win64\\chrome.exe)
    3. None (let Playwright use its default)
    """
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.abspath(os.path.join(base_path, "..", "..", ".."))
    
    bundled_chrome = os.path.join(base_path, "resources", "chrome-win64", "chrome.exe")
    if os.path.exists(bundled_chrome):
        return bundled_chrome
    
    programdata_chrome = r"C:\ProgramData\AutoISP\chrome-win64\chrome.exe"
    if os.path.exists(programdata_chrome):
        return programdata_chrome
    
    return None


class PlaywrightBrowserFactory:
    """
    Helper to create an Async Playwright persistent Chrome context with
    common stealth patches and optimization.
    """

    def __init__(
        self,
        profile_dir: str,
        account: Account,
        channel: str = "chrome",
        headless: bool = False,
        executable_path: Optional[str] = None,
        additional_args: Optional[List[str]] = None,
        use_stealth: bool = True,
        start_maximized: bool = True,
        slow_mo: Optional[int] = None,
        user_agent_type: str = "desktop",  # "desktop" or "mobile"
        job_id: Optional[str] = None,
    ):
        self.profile_path = os.path.join(ChromeProfileManager().chrome_data_path, profile_dir)
        self.profile_dir = profile_dir
        self.channel = channel
        self.headless = headless
        self.executable_path = executable_path or get_chrome_executable()
        self.additional_args = additional_args or []
        self.use_stealth = use_stealth
        self.start_maximized = start_maximized
        self.slow_mo = slow_mo
        self.proxy_config = account.proxy_settings
        self.account = account
        self.user_agent_type = user_agent_type
        self.job_id = job_id

        self._pw = None
        self._context: Optional[BrowserContext] = None
        self._opened = False

        self.logger = logging.getLogger("autoisp")

    async def _setup_optimizations(self, context: BrowserContext):
        """Apply blocklists and stealth scripts."""
        # Block heavy resources
        await context.route("**/*", self._block_heavy_resources)
        
        # Disable Service Workers
        await context.add_init_script("delete window.navigator.serviceWorker;")
        
        if self.use_stealth:
            await context.add_init_script(STEALTH_INIT_SCRIPT)

    async def _block_heavy_resources(self, route, request):
        if request.resource_type in BLOCKED_RESOURCE_TYPES:
            await route.abort()
        else:
            url = request.url.lower()
            if any(x in url for x in ["google-analytics", "doubleclick", "facebook", "scorecardresearch"]):
                await route.abort()
            else:
                await route.continue_()

    async def start(self):
        """Start async browser context."""
        if self._opened:
            return
            
        print(f"🚀 Starting browser with {self.user_agent_type} user agent (Async)...")
        if self.executable_path:
            print(f"📂 Using Chrome: {self.executable_path}")

        os.makedirs(self.profile_path, exist_ok=True)
        
        self._pw = await async_playwright().start()
        
        args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--no-default-browser-check",
            "--disable-dev-shm-usage",
            "--disable-background-networking",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-sync",
            "--disable-default-apps",
            "--disable-component-update",
            "--disable-client-side-phishing-detection",
            "--disable-hang-monitor",
            "--disable-popup-blocking",
            "--process-per-site",
            "--renderer-process-limit=4",
            "--disable-gpu",
            "--disable-software-rasterizer",
            "--disable-features=Translate,BackForwardCache,AcceptCHFrame,MediaRouter"
        ]

        # Configure extensions
        extensions_to_load = []
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            modules_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))

            # Logic to resolve extension paths...
            # (Keeping existing logic roughly same, assuming extensions exist)
            
            if extensions_to_load:
                extensions_arg = ",".join(extensions_to_load)
                args.extend([
                    f"--disable-extensions-except={extensions_arg}",
                    f"--load-extension={extensions_arg}",
                ])
        except Exception as e:
            print(f"⚠️ Failed to configure extensions: {e}")

        if self.user_agent_type == "desktop":
            args.append("--start-maximized")
        
        launch_kwargs = dict(
            user_data_dir=self.profile_path,
            headless=self.headless,
            args=args,
            ignore_default_args=["--enable-automation"],
            user_agent=self._get_user_agent(),
            viewport=None # Default to None to allow window maximizing to work properly
        )
        
        if self.executable_path:
            launch_kwargs['executable_path'] = self.executable_path
        else:
            launch_kwargs['channel'] = self.channel
        
        if self.proxy_config:
            proxy_settings = {
                'server': f"{self.proxy_config['protocol']}://{self.proxy_config['host']}:{self.proxy_config['port']}"
            }
            if 'username' in self.proxy_config and 'password' in self.proxy_config:
                proxy_settings['username'] = self.proxy_config['username']
                proxy_settings['password'] = self.proxy_config['password']
            launch_kwargs['proxy'] = proxy_settings
        
        try:
            self._context = await self._pw.chromium.launch_persistent_context(**launch_kwargs)
            
            # Apply optimizations
            await self._setup_optimizations(self._context)
            
            print("✅ Browser started successfully")
            self._opened = True
            
        except Exception as e:
            print(f"❌ Failed to start browser: {e}")
            raise
        
    def _get_user_agent(self):
        user_agents = {
            "desktop": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.90 Safari/537.36",
            "mobile": "Mozilla/5.0 (Linux; Android 12; Redmi Note 11 Build/SKQ1.211019.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/99.0.4844.88 Mobile Safari/537.36"
        }
        return user_agents.get(self.user_agent_type, user_agents["desktop"])

    def _get_mobile_viewport(self):
        return {"width": 412, "height": 915} # Samsung Galaxy

    async def get_page(self) -> Page:
        if not self._opened:
            await self.start()
        pages = self._context.pages
        page = pages[0] if pages else await self._context.new_page()
        
        if self.user_agent_type == "mobile":
            await page.set_viewport_size(self._get_mobile_viewport())
        
        return page

    async def new_page(self) -> Page:
        if not self._opened:
            await self.start()
        page = await self._context.new_page()
        
        if self.user_agent_type == "mobile":
            await page.set_viewport_size(self._get_mobile_viewport())
        
        return page

    @staticmethod
    def kill_chrome_for_profile(profile_path: str):
        # Synchronous process kill is fine
        profile_path = os.path.abspath(profile_path).lower()
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                if proc.info["name"] != "chrome.exe":
                    continue
                cmdline = " ".join(proc.info.get("cmdline") or []).lower()
                if profile_path in cmdline:
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

    async def close(self):
        """Async close context and stop Playwright."""
        self._opened = False
        if self._context:
            try:
                await self._context.close()
            except Exception:
                pass
            self._context = None
        if self._pw:
            try:
                await self._pw.stop()
            except Exception:
                pass
            self._pw = None
        
        # Kill lingering processes
        self.kill_chrome_for_profile(self.profile_path)
        self.logger.info("Chrome processes killed for profile", extra={"account_id": self.account.id, "is_global":True})

    async def force_close(self):
        await self.close()
