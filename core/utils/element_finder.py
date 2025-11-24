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

def deep_find_elements(page: Page, css_selector: str):
    """
    Recursively search for elements across:
    - main DOM
    - all iframes (nested)
    - all shadow roots (nested)
    """
    results = []

    def search_frame(frame):
        nonlocal results

        # 1) normal query
        try:
            els = frame.query_selector_all(css_selector)
            results.extend(els)
        except:
            pass

        # 2) shadow DOM search
        try:
            shadow_js = """
                (selector) => {
                    const results = [];

                    function scan(node) {
                        if (!node) return;

                        if (node.shadowRoot) {
                            const matches = node.shadowRoot.querySelectorAll(selector);
                            results.push(...matches);

                            node.shadowRoot.querySelectorAll("*").forEach(scan);
                        }
                    }

                    document.querySelectorAll("*").forEach(scan);
                    return results;
                }
            """

            handle = frame.evaluate_handle(shadow_js, css_selector)
            length = frame.evaluate("x => x.length", handle)

            for i in range(length):
                item = handle.get_property(str(i))
                el = item.as_element()
                if el:
                    results.append(el)

        except:
            pass

        # 3) recurse into iframes
        try:
            for child in frame.child_frames:
                search_frame(child)
        except:
            pass

    search_frame(page.main_frame)
    return results

def get_iframe_elements(page: Page, iframe_selector: str, element_selector: str):
    try:
        iframe_element = page.query_selector(iframe_selector)
        if not iframe_element:
            return []

        content_frame = iframe_element.content_frame()
        if not content_frame:
            return []

        els = content_frame.query_selector_all(element_selector)
        return els
    except:
        return []
