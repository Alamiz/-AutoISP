import logging
import random
from abc import ABC
from typing import Optional, List
from playwright.sync_api import Page, Locator
from core.utils.element_finder import find_element, find_element_in_frame
from core.humanization.behavior import HumanBehavior

class HumanAction(ABC):
    """
    Base class for automation scripts with humanization.
    Browser lifecycle is managed by runner.py
    """
    
    def __init__(self):
        self.logger = logging.getLogger("autoisp")
        self.human_behavior = HumanBehavior()
    
    def _find_element_with_humanization(self, page: Page, selectors: List[str], 
                                         iframe_selector: Optional[str] = None,
                                         wait_visible: bool = True) -> Locator:
        """Find element with humanization - uses your existing utility functions"""
        
        # Add slight delay before searching (human reads page first)
        if random.random() > 0.6:  # 40% chance
            self.human_behavior.read_delay()
        
        # Use appropriate finder based on whether iframe is specified
        if iframe_selector:
            element = find_element_in_frame(page, selectors, iframe_selector)
        else:
            element = find_element(page, selectors)
        
        if wait_visible and random.random() > 0.5:  # 50% chance to scroll
            self.human_behavior.scroll_into_view(element)
        
        return element
    
    def human_fill(self, page: Page, selectors: List[str], text: str,
                   iframe_selector: Optional[str] = None):
        """Find and fill input with human-like typing"""
        self.human_behavior.wait_before_action()
        element = self._find_element_with_humanization(page, selectors, iframe_selector)
        self.human_behavior.type_text(element, text)
    
    def human_click(self, page: Page, selectors: List[str],
                   iframe_selector: Optional[str] = None, force: bool = False):
        """Find and click element with human-like behavior"""
        self.human_behavior.wait_before_action()
        element = self._find_element_with_humanization(page, selectors, iframe_selector)
        self.human_behavior.click(element, force=force)