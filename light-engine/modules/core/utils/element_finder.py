from playwright.sync_api import Page, Frame, ElementHandle
from typing import List
import logging
import time

logger = logging.getLogger(__name__)

class ElementNotFound(Exception):
    """Raised when none of the provided selectors match an element."""


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


def deep_find_elements(root, css_selector: str, timeout_ms: int = 15000):
    """
    Optimized element finder - skips inaccessible frames intelligently.
    """
    from playwright.sync_api import Page, Error as PlaywrightError

    start_time = time.time()
    if timeout_ms is None:
        timeout_ms = 15000
    timeout_seconds = timeout_ms / 1000
    poll_interval = 0.5

    page = root if isinstance(root, Page) else root.page
    
    logger.debug(f"Searching for '{css_selector}' (timeout: {timeout_ms}ms)")
    poll_count = 0
    checked_frames = set()  # Track which frame URLs we've successfully checked

    while (time.time() - start_time) < timeout_seconds:
        poll_count += 1
        
        accessible_count = 0
        found_new_frames = False
        
        for frame in page.frames:
            frame_url = frame.url
            
            try:
                # Skip if frame is detached
                if frame.is_detached():
                    continue
                
                # Quick accessibility test - try to get frame name
                try:
                    _ = frame.name  # Just accessing name will fail if frame is inaccessible
                except:
                    continue  # Frame not accessible, skip silently
                
                # Mark this frame as checked
                if frame_url not in checked_frames:
                    checked_frames.add(frame_url)
                    found_new_frames = True
                
                accessible_count += 1
                
                # Try regular selector
                visible = frame.locator(css_selector).locator("visible=true")
                if visible.count() > 0:
                    logger.debug(f"✓ Found {visible.count()} visible elements after {poll_count} polls")
                    return visible.all()
                
                # Try shadow selector
                shadow_visible = frame.locator(f"pierce/{css_selector}").locator("visible=true")
                if shadow_visible.count() > 0:
                    logger.debug(f"✓ Found {shadow_visible.count()} shadow elements after {poll_count} polls")
                    return shadow_visible.all()
                    
            except PlaywrightError:
                continue  # Skip inaccessible frames
            except Exception:
                continue
        
        elapsed = time.time() - start_time
        
        # Log progress
        if found_new_frames or poll_count % 10 == 0:
            logger.debug(f"Poll #{poll_count}: {accessible_count} accessible frames checked ({elapsed:.1f}s)")
        
        if (time.time() - start_time) >= timeout_seconds:
            break
            
        time.sleep(min(poll_interval, max(0, timeout_seconds - elapsed)))

    logger.debug(f"Element not found after {poll_count} polls ({timeout_seconds}s, checked {len(checked_frames)} unique frames)")
    return []