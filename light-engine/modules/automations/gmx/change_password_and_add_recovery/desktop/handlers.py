"""
State handlers for gmx.net Desktop Change Password and Add Recovery.
"""
from playwright.sync_api import Page
from core.flow_engine.state_handler import StateHandler, HandlerAction
from core.utils.browser_utils import navigate_to


class UnknownPageHandler(StateHandler):
    """Handle unknown pages by redirecting to gmx.net homepage."""

    def handle(self, page: Page) -> HandlerAction:
        try:
            navigate_to(page, "https://gmx.net/")
            return "retry"
        except Exception as e:
            return "abort"