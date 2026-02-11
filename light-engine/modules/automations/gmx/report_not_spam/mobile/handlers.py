from playwright.sync_api import Page
from core.flow_engine.state_handler import StateHandler
from modules.core.flow_state import FlowResult
from core.humanization.actions import HumanAction
from core.utils.browser_utils import navigate_to

class UnknownPageHandler(StateHandler):
    """Handle unknown pages"""

    def handle(self, page: Page) -> FlowResult:
        try:
            navigate_to(page, "https://lightmailer-bs.gmx.net/")
            return FlowResult.RETRY
        except Exception:
            return FlowResult.ABORT