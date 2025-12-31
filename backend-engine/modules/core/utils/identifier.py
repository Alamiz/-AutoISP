from playwright.sync_api import Page
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import Optional
import re

# Import the flattening function
from .element_finder import flatten_page_to_html


def is_page_english(html_content):
    """
    Determines if a web page is in English by checking multiple indicators.
    
    Args:
        html_content (str): The HTML content of the page to analyze
        
    Returns:
        bool: True if page appears to be in English, False otherwise
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 1. Check HTML lang attribute
    html_tag = soup.find('html')
    if html_tag and html_tag.has_attr('lang'):
        lang_attr = html_tag['lang'].lower()
        if lang_attr.startswith('en'):
            return True
        elif not lang_attr.startswith('en'):
            return False
    
    # 2. Check meta http-equiv language
    meta_lang = soup.find('meta', attrs={'http-equiv': 'content-language'})
    if meta_lang and meta_lang.has_attr('content'):
        if meta_lang['content'].lower().startswith('en'):
            return True
        elif not meta_lang['content'].lower().startswith('en'):
            return False
    
    # 3. Check og:locale meta tag (used by Facebook/OpenGraph)
    og_locale = soup.find('meta', property='og:locale')
    if og_locale and og_locale.has_attr('content'):
        if og_locale['content'].lower().startswith('en'):
            return True
        elif not og_locale['content'].lower().startswith('en'):
            return False
    
    # 4. Analyze visible text for English words
    visible_text = soup.get_text()
    english_word_count = 0
    total_word_count = 0
    
    # Common English words to look for
    common_english_words = {'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'I'}
    
    words = re.findall(r'\b\w+\b', visible_text.lower())
    for word in words:
        if word in common_english_words:
            english_word_count += 1
        total_word_count += 1
    
    # If we have enough text to analyze and most words are English
    if total_word_count > 20 and (english_word_count / total_word_count) > 0.3:
        return True
    
    # 5. Check for English in title
    title = soup.find('title')
    if title:
        title_text = title.get_text().lower()
        if any(word in title_text for word in common_english_words):
            return True
    
    # If none of the above indicators confirm English, assume it's not English
    return False


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
    
    if signatures is None:
        raise ValueError("Signatures must be provided for the current platform")
    
    # Take a FRESH snapshot: flatten entire page into single HTML
    # This includes: main DOM + all iframes + all shadow DOM content
    flattened_html = flatten_page_to_html(page)
    
    # Parse once with BeautifulSoup
    soup = BeautifulSoup(flattened_html, 'html.parser')
    
    page_scores = {}

    for page_name, config in signatures.items():
        # Required sublink check (cheap)
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
            requires_english = check.get("require_english", False)

            if requires_english and not is_page_english(flattened_html):
                continue

            element_exists = False

            try:
                # ALL checks now use BeautifulSoup on the flattened HTML
                # No need for deep_search flag anymore - everything is flattened!
                
                # Note: iframe_selector is now ignored since everything is flattened
                # Just use the css_selector directly
                elements = soup.select(check["css_selector"])
                element_exists = len(elements) >= min_count

                # Text validation
                if element_exists and contains_text:
                    element_exists = any(
                        contains_text.lower() in el.get_text().lower()
                        for el in elements
                    )

            except Exception as e:
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
            page_scores[page_name] = max(0, matched_score) / total_possible

            # Stop search if perfect score (page found!)
            if matched_score / total_possible == 1:
                break
        else:
            page_scores[page_name] = 0

    # Return best match
    if not page_scores:
        return "unknown"

    best_page, score = max(page_scores.items(), key=lambda x: x[1])
    return best_page if score >= 0.7 else "unknown"