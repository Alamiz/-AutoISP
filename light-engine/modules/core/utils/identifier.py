from playwright.sync_api import Page
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import Optional
import time
import logging

logger = logging.getLogger(__name__)

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
    
    logger.info("=" * 60)
    logger.info("Starting page identification")
    logger.info("=" * 60)
    
    # ========================================
    # STEP 1: Build HTML ONCE (expensive operation)
    # ========================================
    step_start = time.time()
    flattened_html = flatten_page_to_html(page)
    flatten_time = time.time() - step_start
    logger.info(f"✓ Flattened HTML: {flatten_time*1000:.2f}ms ({len(flattened_html):,} chars)")
    
    # ========================================
    # STEP 2: Parse with BeautifulSoup ONCE
    # ========================================
    step_start = time.time()
    soup = BeautifulSoup(flattened_html, 'html.parser')
    parse_time = time.time() - step_start
    logger.info(f"✓ Parsed with BeautifulSoup: {parse_time*1000:.2f}ms")
    
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
    logger.info(f"Checking {len(signatures)} page signatures...")
    
    page_scores = {}
    signature_times = {}
    total_checks = 0
    cache_hits = 0

    for page_name, config in signatures.items():
        sig_start = time.time()
        
        # Required sublink check (cheap, do first)
        if "required_sublink" in config:
            if not has_required_sublink(current_url, config["required_sublink"]):
                logger.debug(f"  {page_name}: Skipped (sublink mismatch)")
                continue

        total_possible = 0
        matched_score = 0
        checks_performed = 0

        for check in config["checks"]:
            weight = check.get("weight", 1)
            should_exist = check.get("should_exist", True)
            min_count = check.get("min_count", 1)
            contains_text = check.get("contains_text")

            element_exists = False
            total_checks += 1

            try:
                # Use cached selector results
                css_selector = check["css_selector"]
                
                # Track cache hits
                was_cached = css_selector in selector_cache
                elements = get_elements(css_selector)
                if was_cached:
                    cache_hits += 1
                
                element_exists = len(elements) >= min_count

                # Text validation
                if element_exists and contains_text:
                    element_exists = any(
                        contains_text.lower() in el.get_text().lower()
                        for el in elements
                    )

            except Exception as e:
                logger.debug(f"  {page_name}: Check failed - {e}")
                continue

            checks_performed += 1
            
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

        sig_time = time.time() - sig_start
        signature_times[page_name] = sig_time
        
        if total_possible > 0:
            score = max(0, matched_score) / total_possible
            page_scores[page_name] = score
            
            logger.debug(f"  {page_name}: {score:.2%} ({checks_performed} checks, {sig_time*1000:.2f}ms)")

            # Early exit: perfect score found
            if matched_score / total_possible == 1:
                logger.info(f"✓ Perfect match found: {page_name}")
                break
        else:
            page_scores[page_name] = 0

    # ========================================
    # STEP 5: Results
    # ========================================
    total_time = time.time() - total_start
    
    logger.info("-" * 60)
    logger.info("Performance Summary:")
    logger.info(f"  HTML Flattening:     {flatten_time*1000:>8.2f}ms")
    logger.info(f"  BeautifulSoup Parse: {parse_time*1000:>8.2f}ms")
    logger.info(f"  Signature Checks:    {sum(signature_times.values())*1000:>8.2f}ms")
    logger.info(f"  Total Time:          {total_time*1000:>8.2f}ms")
    logger.info("-" * 60)
    logger.info(f"Cache Stats:")
    logger.info(f"  Total selector queries: {total_checks}")
    logger.info(f"  Cache hits:             {cache_hits} ({cache_hits/total_checks*100:.1f}%)" if total_checks > 0 else "  No queries")
    logger.info(f"  Unique selectors:       {len(selector_cache)}")
    logger.info("-" * 60)
    
    # Return best match
    if not page_scores:
        logger.warning("No matching pages found")
        logger.info("=" * 60)
        return "unknown"

    best_page, score = max(page_scores.items(), key=lambda x: x[1])
    
    # Show top 3 matches
    top_matches = sorted(page_scores.items(), key=lambda x: x[1], reverse=True)[:3]
    logger.info("Top matches:")
    for idx, (name, sc) in enumerate(top_matches, 1):
        logger.info(f"  {idx}. {name}: {sc:.2%}")
    
    logger.info("-" * 60)
    
    if score >= 0.7:
        logger.info(f"✓ Identified page: {best_page} (confidence: {score:.2%})")
    else:
        logger.warning(f"Low confidence match: {best_page} ({score:.2%}) - returning 'unknown'")
        best_page = "unknown"
    
    logger.info("=" * 60)
    
    return best_page