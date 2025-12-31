from playwright.sync_api import Page, Frame, ElementHandle
from typing import List

class ElementNotFound(Exception):
    """Raised when none of the provided selectors match an element."""
    pass


def flatten_page_to_html(page: Page) -> str:
    """
    Flatten entire page (iframes + shadow DOM) into single HTML string.
    This allows BeautifulSoup to search everything at once.
    
    Returns:
        Complete HTML with all nested content flattened
    """
    
    def scan_frame(frame, depth=0):
        """Recursively extract HTML from frame and its children"""
        html_parts = []
        
        try:
            # Get main frame HTML with shadow DOM content injected
            main_html = frame.evaluate("""
                () => {
                    // Clone the document to avoid modifying the original
                    const clone = document.documentElement.cloneNode(true);
                    
                    // Function to inject shadow DOM content into the clone
                    function injectShadowContent(originalNode, cloneNode) {
                        if (!originalNode || !cloneNode) return;
                        
                        // If original has shadow root, inject its content
                        if (originalNode.shadowRoot) {
                            const shadowContent = originalNode.shadowRoot.innerHTML;
                            const shadowMarker = document.createElement('div');
                            shadowMarker.setAttribute('data-shadow-root', 'true');
                            shadowMarker.innerHTML = shadowContent;
                            cloneNode.appendChild(shadowMarker);
                            
                            // Recursively process shadow DOM children
                            const shadowChildren = Array.from(originalNode.shadowRoot.children);
                            const cloneChildren = Array.from(shadowMarker.children);
                            
                            for (let i = 0; i < shadowChildren.length; i++) {
                                if (shadowChildren[i] && cloneChildren[i]) {
                                    injectShadowContent(shadowChildren[i], cloneChildren[i]);
                                }
                            }
                        }
                        
                        // Process regular children
                        const originalChildren = Array.from(originalNode.children);
                        const cloneChildren = Array.from(cloneNode.children);
                        
                        for (let i = 0; i < Math.min(originalChildren.length, cloneChildren.length); i++) {
                            injectShadowContent(originalChildren[i], cloneChildren[i]);
                        }
                    }
                    
                    // Start injection from root
                    injectShadowContent(document.documentElement, clone);
                    
                    return clone.outerHTML;
                }
            """)
            
            html_parts.append(main_html)
            
        except Exception as e:
            # Fallback to basic content if script fails
            try:
                html_parts.append(frame.content())
            except:
                pass
        
        # Extract content from all iframes
        try:
            iframe_elements = frame.query_selector_all("iframe")
            
            for idx, iframe_element in enumerate(iframe_elements):
                try:
                    content_frame = iframe_element.content_frame()
                    if content_frame:
                        # Recursively get iframe content
                        iframe_html = scan_frame(content_frame, depth + 1)
                        
                        # Wrap in marker div so we know it came from iframe
                        wrapped = f'<div data-iframe-content="true" data-iframe-index="{idx}">{iframe_html}</div>'
                        html_parts.append(wrapped)
                except Exception as e:
                    pass
        except Exception as e:
            pass
        
        return '\n'.join(html_parts)
    
    # Start from main frame
    return scan_frame(page.main_frame, depth=0)


def get_iframe_elements(page: Page, iframe_selector: str, element_selector: str):
    """
    Legacy function - kept for backward compatibility.
    Gets elements from a specific iframe.
    """
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


import time
from playwright.sync_api import Page, Frame, ElementHandle, TimeoutError

def deep_find_elements(root, css_selector: str, timeout_ms: int = 30000):
    """
    Recursively search for elements across:
    - Page
    - Frame
    - Iframes
    - Shadow DOM

    Supports Page, Frame, or ElementHandle as root.
    Continues searching until timeout is reached or elements are found.
    
    Args:
        root: Page, Frame, or ElementHandle to search from
        css_selector: CSS selector to search for
        timeout_ms: Maximum time to search in milliseconds (default: 30000)
    
    Returns:
        List of found ElementHandles
    """
    results = []
    start_time = time.time()
    timeout_seconds = timeout_ms / 1000
    
    def is_timed_out():
        return (time.time() - start_time) > timeout_seconds

    def search_context(context):
        nonlocal results
        
        if is_timed_out():
            return

        # 1) Normal DOM search
        try:
            els = context.query_selector_all(css_selector)
            if els:
                results.extend(els)
        except Exception:
            pass

        if is_timed_out():
            return

        # 2) Shadow DOM search (Page / Frame only)
        if isinstance(context, (Page, Frame)):
            try:
                shadow_js = """
                    (selector) => {
                        const results = [];

                        function scan(node) {
                            if (!node) return;

                            if (node.shadowRoot) {
                                results.push(...node.shadowRoot.querySelectorAll(selector));
                                node.shadowRoot.querySelectorAll("*").forEach(scan);
                            }
                        }

                        document.querySelectorAll("*").forEach(scan);
                        return results;
                    }
                """
                handle = context.evaluate_handle(shadow_js, css_selector)
                length = context.evaluate("x => x.length", handle)

                for i in range(length):
                    if is_timed_out():
                        return
                    el = handle.get_property(str(i)).as_element()
                    if el:
                        results.append(el)
            except Exception:
                pass

        if is_timed_out():
            return

        # 3) Recurse into iframes (Page / Frame only)
        if isinstance(context, (Page, Frame)):
            try:
                iframe_elements = context.query_selector_all("iframe")
                for iframe in iframe_elements:
                    if is_timed_out():
                        return
                    frame = iframe.content_frame()
                    if frame:
                        search_context(frame)
            except Exception:
                pass

    # ---- Main search loop ----
    poll_interval = 0.5  # Check every 500ms
    
    while not is_timed_out():
        results = []  # Reset results for each iteration
        
        if isinstance(root, Page):
            search_context(root.main_frame)
        else:
            search_context(root)
        
        # If we found elements, return them
        if results:
            return results
        
        # If timed out, break
        if is_timed_out():
            break
            
        # Wait before next poll (but don't exceed timeout)
        remaining_time = timeout_seconds - (time.time() - start_time)
        time.sleep(min(poll_interval, max(0, remaining_time)))
    
    return results