# automations/webde/report_not_spam/mobile/handlers.py
"""
State handlers for web.de Mobile Report Not Spam using StatefulFlow.
"""
from playwright.sync_api import Page
from core.flow_engine.state_handler import StateHandler, HandlerAction
from core.humanization.actions import HumanAction
from core.utils.browser_utils import navigate_to

class UnknownPageHandler(StateHandler):
    """Handle unknown pages"""
    
    def __init__(self, human_action: HumanAction = None, logger=None):
        super().__init__(logger)
        self.human_action = human_action
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            navigate_to(page, "https://lightmailer-bs.web.de/")
            return "retry"
        except Exception:
            return "abort"
