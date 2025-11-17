import time
import functools
import logging

from playwright.sync_api import Page, TimeoutError

# Setup basic logger
logging.basicConfig(level=logging.INFO)

class RequiredActionFailed(Exception):
    """Raised when a required automation action fails after all retries."""
    pass

def retry(max_retries=3, required=True, delay=1):
    """
    Decorator to retry a function multiple times.
    
    :param max_retries: number of retries
    :param required: if True, failure stops the flow
    :param delay: seconds to wait between retries
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    logging.warning(f"[{func.__name__}] Attempt {attempts}/{max_retries} failed: {e}")
                    if attempts >= max_retries:
                        if required:
                            logging.error(f"[{func.__name__}] Required action failed after {max_retries} retries. Stopping automation.")
                            raise RequiredActionFailed(f"{func.__name__} failed after {max_retries} retries.") from e
                        else:
                            logging.warning(f"[{func.__name__}] Optional action failed after {max_retries} retries. Continuing automation.")
                            return None
                    time.sleep(delay)
        return wrapper
    return decorator

import logging
from PySide6.QtWidgets import QTextEdit

class QTextEditLogger(logging.Handler):
    def __init__(self, text_edit: QTextEdit):
        super().__init__()
        self.text_edit = text_edit

    def emit(self, record):
        msg = self.format(record)

        self.text_edit.append(msg)
    
        self.text_edit.verticalScrollBar().setValue(
            self.text_edit.verticalScrollBar().maximum()
        )


class ElementNotFound(Exception):
    """Raised when none of the provided selectors match an element."""
    pass

def find_element_in_frame(page: Page, selectors: list[str], frame_selector: str = None, timeout: int = 5000):
    """
    Try each selector in the list and return the first matching element.
    
    :param page: Playwright Page object
    :param selectors: List of CSS/XPath selectors
    :param timeout: Timeout for each selector in ms
    :return: Playwright element handle
    :raises: ElementNotFound if no selector matches
    """

    if not frame_selector:
        raise ValueError("frame_selector is required")

    frame_element = page.wait_for_selector(frame_selector, timeout=timeout)
    frame = frame_element.content_frame()

    for selector in selectors:
        try:
            element = frame.wait_for_selector(selector, timeout=timeout)
            if element:
                return element
        except TimeoutError:
            continue  # try next selector

    # If we get here, no selector matched
    raise ElementNotFound(f"No element found for selectors: {selectors}")

def find_element(page: Page, selectors: list[str], timeout: int = 5000):
    """
    Try each selector in the list and return the first matching element.
    
    :param page: Playwright Page object
    :param selectors: List of CSS/XPath selectors
    :param timeout: Timeout for each selector in ms
    :return: Playwright element handle
    :raises: ElementNotFound if no selector matches
    """
    for selector in selectors:
        try:
            element = page.wait_for_selector(selector, timeout=timeout)
            if element:
                return element
        except TimeoutError:
            continue  # try next selector

    # If we get here, no selector matched
    raise ElementNotFound(f"No element found for selectors: {selectors}")
