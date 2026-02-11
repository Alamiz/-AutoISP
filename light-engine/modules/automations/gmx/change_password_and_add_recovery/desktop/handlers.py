"""
State handlers for gmx.net Desktop Change Password and Add Recovery.
"""
from playwright.sync_api import Page
from core.flow_engine.state_handler import StateHandler
from modules.core.flow_state import FlowResult
from core.utils.browser_utils import navigate_to

class UnknownPageHandler(StateHandler):
    """Handle unknown pages by redirecting to gmx.net homepage."""

    def handle(self, page: Page) -> FlowResult:
        try:
            navigate_to(page, "https://alligator.navigator.gmx.net/go/?targetURI=https://link.gmx.net/mail/showStartView&ref=link")
            return FlowResult.RETRY
        except Exception as e:
            return FlowResult.ABORT