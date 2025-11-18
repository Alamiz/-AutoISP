from playwright.sync_api import Page, TimeoutError

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
