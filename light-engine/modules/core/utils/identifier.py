from playwright.sync_api import Page
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import Optional
import time
import logging

logger = logging.getLogger("autoisp")

# Import the flattening function
from .element_finder import flatten_page_to_html


def has_required_sublink(current_url: str, required_sublink: str) -> bool:
    """Check if current URL contains the required sublink"""
    try:
        parsed_current = urlparse(current_url)
        parsed_required = urlparse(
            required_sublink if '://' in required_sublink 
            else f'https://{required_sublink}'
        )
        return (
            parsed_current.netloc.endswith(parsed_required.netloc) and
            parsed_current.path.startswith(parsed_required.path)
        )
    except:
        return False


def identify_page(page: Page, current_url: Optional[str] = None, signatures=None) -> str:
    """
    Optimized page identification using flattened HTML snapshot.
    
    This function:
    1. Takes a fresh snapshot of the entire page (main DOM + iframes + shadow DOM)
    2. Flattens everything into a single HTML string
    3. Uses BeautifulSoup for ALL checks (fast!)
    
    Args:
        page: Playwright page object
        current_url: Current page URL
        signatures: Page signature configuration
    
    Returns:
        Identified page name or "unknown"
    """
    
    total_start = time.time()
    
    if signatures is None:
        raise ValueError("Signatures must be provided for the current platform")
    
    logger.debug("Starting page identification")
    
    # ========================================
    # STEP 1: Build HTML ONCE (expensive operation)
    # ========================================
    flattened_html = flatten_page_to_html(page)
    
    # ========================================
    # STEP 2: Parse with BeautifulSoup ONCE
    # ========================================
    soup = BeautifulSoup(flattened_html, 'html.parser')
    
    # ========================================
    # STEP 3: Setup selector caching
    # ========================================
    selector_cache = {}
    
    def get_elements(css_selector):
        """Cache selector results"""
        if css_selector not in selector_cache:
            selector_cache[css_selector] = soup.select(css_selector)
        return selector_cache[css_selector]
    
    # ========================================
    # STEP 4: Score all pages
    # ========================================
    page_scores = {}

    for page_name, config in signatures.items():
        # Required sublink check (cheap, do first)
        if "required_sublink" in config:
            if not has_required_sublink(current_url, config["required_sublink"]):
                continue

        total_possible = 0
        matched_score = 0

        for check in config["checks"]:
            weight = check.get("weight", 1)
            should_exist = check.get("should_exist", True)
            min_count = check.get("min_count", 1)
            contains_text = check.get("contains_text")

            element_exists = False

            try:
                # Use cached selector results
                css_selector = check["css_selector"]
                elements = get_elements(css_selector)
                element_exists = len(elements) >= min_count

                # Text validation
                if element_exists and contains_text:
                    element_exists = any(
                        contains_text.lower() in el.get_text().lower()
                        for el in elements
                    )

            except:
                continue
            
            # Scoring logic
            total_possible += weight

            if should_exist:
                if element_exists:
                    matched_score += weight
                else:
                    matched_score -= weight
            else:
                if not element_exists:
                    matched_score += weight
                else:
                    matched_score -= weight

        if total_possible > 0:
            score = max(0, matched_score) / total_possible
            page_scores[page_name] = score

            # Early exit: perfect score found
            if matched_score / total_possible == 1:
                break
        else:
            page_scores[page_name] = 0

    # ========================================
    # STEP 5: Results
    # ========================================
    total_time = time.time() - total_start
    
    # Return best match
    if not page_scores:
        logger.info(f"Page identified with unknown: {total_time:.2f}s")
        return "unknown"

    best_page, score = max(page_scores.items(), key=lambda x: x[1])
    
    if score < 0.7:
        best_page = "unknown"
    
    logger.info(f"Page identified with {best_page} and time took {total_time:.2f}s")
    
    return best_page