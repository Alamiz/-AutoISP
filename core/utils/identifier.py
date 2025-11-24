from automations.gmx.signatures import PAGE_SIGNATURES
from playwright.sync_api import Page
from typing import Optional
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import logging

# def get_signatures_dict():
#     """
#     Convert database signatures to identification-compatible dictionary
#     Returns:
#         {
#             'page_name': {
#                 'required_sublink': '...',
#                 'checks': [
#                     {
#                         'css_selector': '...',
#                         'contains_text': '...',
#                         'min_count': int,
#                         'require_english': bool,
#                         'weight': float,
#                         'is_required': bool
#                     },
#                     ...
#                 ]
#             },
#             ...
#         }
#     """
#     from django.db.models import Prefetch
    
#     # Optimized query with prefetch
#     signatures = PageSignature.objects.prefetch_related(
#         Prefetch(
#             'signaturecheckmembership_set',
#             queryset=SignatureCheckMembership.objects.select_related('page_check')
#             .order_by('-weight')
#         )
#     ).all()
    
#     result = {}
    
#     for sig in signatures:
#         sig_data = {
#             'required_sublink': sig.required_sublink,
#             'checks': []
#         }
        
#         for membership in sig.signaturecheckmembership_set.all():
#             check = membership.page_check
#             check_data = {
#                 'css_selector': check.css_selector,
#                 'weight': abs(membership.weight),  # Always positive
#                 'is_required': membership.is_required,
#                 'min_count': check.min_count
#             }
            
#             # Only include non-default values
#             if check.contains_text:
#                 check_data['contains_text'] = check.contains_text
#             if check.require_english:
#                 check_data['require_english'] = True
            
#             sig_data['checks'].append(check_data)
        
#         result[sig.name] = sig_data
    
#     return result

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

def identify_page(page: Page, current_url: Optional[str] = None) -> str:
    html_content = page.content()
    soup = BeautifulSoup(html_content, 'html.parser')

    page_scores = {}

    for page_name, config in PAGE_SIGNATURES.items():
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

            if requires_english and not is_page_english(html_content):
                continue

            # Lookup method
            element_exists = False

            try:
                # ------------------------------------------------------------------
                # 1) FAST mode (default)
                # ------------------------------------------------------------------
                if not check.get("deep_search", False):

                    if "iframe_selector" in check:
                        # fast iframe search
                        elements = get_iframe_elements(
                            page,
                            check["iframe_selector"],
                            check["css_selector"]
                        )
                        element_exists = len(elements) >= min_count

                        # text validation
                        if element_exists and contains_text:
                            element_exists = any(
                                contains_text.lower() in (page.evaluate("(e) => e.innerText", el) or "").lower()
                                for el in elements
                            )

                    else:
                        # BeautifulSoup (fastest)
                        elements = soup.select(check["css_selector"])
                        element_exists = len(elements) >= min_count

                        if element_exists and contains_text:
                            element_exists = any(
                                contains_text.lower() in el.get_text().lower()
                                for el in elements
                            )

                # ------------------------------------------------------------------
                # 2) DEEP SEARCH mode
                # ------------------------------------------------------------------
                else:
                    elements = deep_find_elements(page, check["css_selector"])
                    element_exists = len(elements) >= min_count

                    if element_exists and contains_text:
                        element_exists = any(
                            contains_text.lower() in page.evaluate("(e) => e.innerText", el).lower()
                            for el in elements
                        )

            except Exception as e:
                continue

            # scoring
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

            # Stop search if score is 1 (page found !)
            if matched_score / total_possible == 1:
                break
        else:
            page_scores[page_name] = 0

    # best match
    if not page_scores:
        return "unknown"

    best_page, score = max(page_scores.items(), key=lambda x: x[1])
    return best_page if score >= 0.7 else "unknown"

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
