from playwright.sync_api import Page

class ElementNotFound(Exception):
    """Raised when none of the provided selectors match an element."""
    pass

def deep_find_elements(page: Page, css_selector: str):
    """
    Recursively search for elements across:
    - main DOM
    - all iframes (nested)
    - all shadow roots (nested)
    """
    results = []

    def search_frame(frame, depth=0):
        nonlocal results
        
        # 1) normal query
        try:
            els = frame.query_selector_all(css_selector)
            if els:
                results.extend(els)
        except Exception as e:
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

            if length > 0:
                for i in range(length):
                    item = handle.get_property(str(i))
                    el = item.as_element()
                    if el:
                        results.append(el)
        except Exception as e:
            pass

        # 3) Find all iframe elements in this frame and recurse into them
        try:
            iframe_elements = frame.query_selector_all("iframe")
            
            if iframe_elements:
                for idx, iframe_element in enumerate(iframe_elements):
                    try:
                        content_frame = iframe_element.content_frame()
                        if content_frame:
                            search_frame(content_frame, depth + 1)
                    except Exception as e:
                        pass
        except Exception as e:
            pass
        
    search_frame(page.main_frame, depth=0)
    
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
