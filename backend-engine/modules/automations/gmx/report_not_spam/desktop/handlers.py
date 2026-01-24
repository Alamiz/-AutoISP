from playwright.sync_api import Page
from core.flow_engine.state_handler import StateHandler, HandlerAction
from core.humanization.actions import HumanAction
from core.utils.element_finder import deep_find_elements
from core.utils.browser_utils import navigate_to

class UnknownPageHandler(StateHandler):
    """Handle unknown pages"""

    def handle(self, page: Page) -> HandlerAction:
        try:
            navigate_to(page, "https://gmx.net/")
            return "retry"
        except Exception as e:
            return "abort"
