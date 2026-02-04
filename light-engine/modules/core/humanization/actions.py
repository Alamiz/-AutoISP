import logging
import random
from abc import ABC
from playwright.sync_api import Page
from core.utils.element_finder import deep_find_elements, ElementNotFound
from core.humanization.behavior import HumanBehavior
from typing import Optional

class HumanAction(ABC):
    """
    Base class for automation scripts with humanization.
    Browser lifecycle is managed by runner.py
    """
    
    def __init__(self, job_id: Optional[str] = None):
        self.logger = logging.getLogger("autoisp")
        self.job_id = job_id
        self.human_behavior = HumanBehavior(job_id=job_id)
    
    def _find_element_with_humanization(
        self,
        page: Page,
        selectors: list[str] | str,
        deep_search: bool = False,
        timeout: Optional[int] = 3000,
        wait_visible: bool = True
    ):
        """
        Find element with humanization, optionally using deep search for nested shadow/iframe elements.
        """
        if isinstance(selectors, str):
            selectors = [selectors]
        if timeout is None:
            timeout = 3000

        # Slight random delay before searching
        # if random.random() > 0.6:

        #     self.human_behavior.read_delay()

        element = None

        if deep_search:
            # Use universal deep search to find the element
            for selector in selectors:
                elements = deep_find_elements(page, selector, timeout)
                if elements:
                    element = elements[0]
                    break
        else:
            # Fast default search (main DOM only)
            for selector in selectors:
                try:
                    element = page.wait_for_selector(selector, timeout=timeout)
                    if element:
                        break
                except Exception:
                    continue

        if not element:
            raise ElementNotFound(f"No element found for selectors: {selectors}")

        # Scroll into view with some randomness
        if wait_visible and random.random() > 0.5:
            self.human_behavior.scroll_into_view(element)

        return element

    
    def human_fill(self, page: Page, selectors: list[str], text: str, deep_search: bool = False, timeout: Optional[int] = None):
        """
        Find input element and fill it with human-like typing.
        Uses deep_search if the element might be inside shadow DOM or nested iframes.
        """
        self.human_behavior.wait_before_action()
        element = self._find_element_with_humanization(page, selectors, deep_search=deep_search, timeout=timeout)
        # self.human_behavior.type_text(element, text)
        element.fill(text)
        
    def human_click(self, page: Page, selectors: list[str], deep_search: bool = False, force: bool = False, timeout: Optional[int] = None):
        """
        Find and click element with human-like behavior.
        Uses deep search if the element might be inside shadow DOM or nested iframes.
        """
        self.human_behavior.wait_before_action()
        element = self._find_element_with_humanization(page, selectors, deep_search=deep_search, timeout=timeout)

        self.human_behavior.click(element, page, force=force)

    def human_select(self, page: Page, selectors: list[str], value: Optional[str] = None, label: Optional[str] = None, deep_search: bool = False, timeout: Optional[int] = None):
        """
        Find and select an option in a dropdown element with human-like behavior.
        Uses deep search if the element might be inside shadow DOM or nested iframes.
        """
        self.human_behavior.wait_before_action()
        element = self._find_element_with_humanization(page, selectors, deep_search=deep_search, timeout=timeout)
        self.human_behavior.select(element, value=value, label=label)
