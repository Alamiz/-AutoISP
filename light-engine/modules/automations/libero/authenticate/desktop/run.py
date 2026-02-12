import logging
import time
from playwright.sync_api import Page, Error as PlaywrightError
from core.browser.browser_helper import PlaywrightBrowserFactory
from core.utils.retry_decorators import RequiredActionFailed
from core.utils.exceptions import JobCancelledException
from core.humanization.actions import HumanAction
from core.utils.identifier import identify_page
from core.flow_engine.smart_flow import StatefulFlow
from core.utils.navigation import navigate_with_retry
from core.utils.extension_helper import get_rektcaptcha_popup_url
from core.flow_engine.state_handler import StateHandlerRegistry
from modules.core.flow_state import FlowResult
from .handlers import (
    LiberoLoginPageHandler,
    LiberoPasswordPageHandler,
    LiberoInboxPageHandler,
    LiberoSuspendedPageHandler,
    UnknownPageHandler
)
from core.pages_signatures.libero.desktop import PAGE_SIGNATURES

class LiberoAuthentication(HumanAction):
    """
    State-based Libero authentication using StatefulFlow
    """
    
    # Define goal states (authentication is complete)
    GOAL_STATES = {"libero_inbox_page"}
    
    # Maximum flow iterations to prevent infinite loops
    MAX_FLOW_ITERATIONS = 15
    
    def __init__(self, account, user_agent_type="desktop", job_id=None):
        super().__init__()
        self.account = account
        self.user_agent_type = user_agent_type
        self.signatures = PAGE_SIGNATURES
        self.job_id = job_id  # For browser registration with job_manager
        
        self.logger = logging.getLogger("autoisp")
        self.profile = self.account.email.split('@')[0]
        
        self.browser = PlaywrightBrowserFactory(
            profile_dir=f"Profile_{self.profile}",
            account=self.account,
            user_agent_type=user_agent_type,
            job_id=job_id
        )
 
    def _setup_state_handlers(self) -> StateHandlerRegistry:
        """
        Setup state handler registry with all authentication handlers.
        """
        registry = StateHandlerRegistry(
            identifier_func=identify_page,
            signatures=self.signatures,
            logger=self.logger
        )
        
        # Register handlers for authentication page states
        registry.register("libero_login_page", LiberoLoginPageHandler(self, self.logger))
        registry.register("libero_login_password_page", LiberoPasswordPageHandler(self, self.logger))
        registry.register("libero_inbox_page", LiberoInboxPageHandler(self, self.logger))
        registry.register("libero_suspended_page", LiberoSuspendedPageHandler(self, self.logger))
        
        registry.register("unknown", UnknownPageHandler(self, self.logger))
        # TODO: Add handlers for captcha, wrong password, etc.
        
        return registry
 
    def _is_goal_reached(self, page: Page) -> bool:
        """Check if we've reached a goal state (inbox) and popups are closed."""
        try:
            page_id = identify_page(page, page.url, self.signatures)
            if page_id not in self.GOAL_STATES:
                return False
            
            # Check for popups that must be closed for the goal to be considered reached
            if page.locator('div.wizard-container').is_visible() or \
               page.locator('div.io-ox-dialog-wrapper').is_visible():
                self.logger.debug("Inbox reached but popups found, continuing handling", extra={"account_id": self.account.id})
                return False
                
            self.logger.debug(f"Goal state reached: {page_id}", extra={"account_id": self.account.id})
            return True
        except Exception as e:
            self.logger.warning(f"Error checking goal: {e}", extra={"account_id": self.account.id})
            return False

    def execute(self) -> dict:
        """
        Runs authentication flow for Libero
        """
        self.logger.info(f"Starting authentication flow", extra={"account_id": self.account.id})
        
        # Log proxy usage if configured
        if self.account.proxy_settings:
            proxy_info = f"{self.account.proxy_settings['protocol']}://{self.account.proxy_settings['host']}:{self.account.proxy_settings['port']}"
            if 'username' in self.account.proxy_settings:
                proxy_info = f"{self.account.proxy_settings['protocol']}://{self.account.proxy_settings['username']}:***@{self.account.proxy_settings['host']}:{self.account.proxy_settings['port']}"
            self.logger.info(f"Using proxy: {proxy_info}", extra={"account_id": self.account.id})

        try:
            # Start browser with proxy configuration
            self.browser.start()
            
            # Create new page
            page = self.browser.new_page()

            # Authenticate using StatefulFlow
            result = self.authenticate(page)
            
            if result["status"] == "success":
                self.logger.info(f"Authentication successful", extra={"account_id": self.account.id})
            else:
                self.logger.warning(f"Authentication ended with status: {result['status']}", extra={"account_id": self.account.id})
            
            return result
        
        except JobCancelledException:
            raise
        except PlaywrightError as e:
            if "Target closed" in str(e):
                self.logger.warning(f"Browser closed manually", extra={"account_id": self.account.id})
                return {"status": "failed", "message": "Browser closed manually"}
            self.logger.error(f"Playwright error: {e}", extra={"account_id": self.account.id})
            return {"status": "failed", "message": str(e)}
        except RequiredActionFailed as e:
            self.logger.error(f"Authentication failed: {e}", extra={"account_id": self.account.id})
            return {"status": "failed", "message": str(e)}
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}", extra={"account_id": self.account.id})
            return {"status": "failed", "message": str(e)}
        finally:
            # Close browser
            self.browser.close()

    def _configure_extension(self, page: Page):
        """Configure rektCaptcha extension settings"""
        try:
            self.logger.info("Configuring rektCaptcha extension...", extra={"account_id": self.account.id})
            popup_url = get_rektcaptcha_popup_url(page)
            
            if not popup_url:
                self.logger.warning("rektCaptcha extension not found, skipping configuration", extra={"account_id": self.account.id})
                return

            # Navigate to popup
            page.goto(popup_url)
            page.wait_for_load_state("networkidle")
            
            # Helper to toggle setting if needed
            def toggle_setting(selector):
                element = page.locator(selector)
                if element.count() > 0:
                    class_attr = element.get_attribute("class") or ""
                    if "on" not in class_attr:
                        self.logger.info(f"Enabling {selector}...", extra={"account_id": self.account.id})
                        element.click()
                        time.sleep(0.5) # Small delay for UI update
                    else:
                        self.logger.info(f"{selector} already enabled", extra={"account_id": self.account.id})
                else:
                    self.logger.warning(f"Setting selector {selector} not found", extra={"account_id": self.account.id})

            # Enable auto open
            toggle_setting('div[data-settings="recaptcha_auto_open"]')
            
            # Enable auto solve
            toggle_setting('div[data-settings="recaptcha_auto_solve"]')
            
            self.logger.info("rektCaptcha configuration completed", extra={"account_id": self.account.id})
            
        except Exception as e:
            self.logger.error(f"Failed to configure rektCaptcha: {e}", extra={"account_id": self.account.id})

    def authenticate(self, page: Page):
        """
        State-based authentication using StatefulFlow.
        Automatically handles different page states until reaching goal state.
        """
        # Configure extension first
        self._configure_extension(page)

        # Navigate to Libero with retry on network errors
        navigate_with_retry(page, "https://mail1.libero.it/", max_retries=3, account=self.account, logger=self.logger)
        self.human_behavior.read_delay()
        
        # Setup state handlers
        state_registry = self._setup_state_handlers()
        
        # Create and run StatefulFlow
        flow = StatefulFlow(
            state_registry=state_registry,
            goal_checker=self._is_goal_reached,
            account=self.account,
            max_steps=self.MAX_FLOW_ITERATIONS,
            logger=self.logger,
            job_id=self.job_id
        )
        
        result = flow.run(page)
        
        if result.status != FlowResult.SUCCESS:
            # Return the actual status name (e.g. "suspended", "locked")
            return {"status": result.status.name.lower(), "message": result.message}
        
        self.logger.info("Authentication completed", extra={"account_id": self.account.id})
        return {"status": "success", "message": "Authentication completed successfully"}
