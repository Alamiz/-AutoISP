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
    """
    Identify the current page by checking:
    - CSS selectors
    - optional text content
    - optional iframe scope
    - expected presence/absence (should_exist)
    """

    logger = logging.getLogger("autoisp")

    html_content = page.content()
    soup = BeautifulSoup(html_content, 'html.parser')
    page_scores = {}

    for page_name, config in PAGE_SIGNATURES.items():
        # print(f"\n[PAGE] {page_name}")

        # Check required sublink
        if 'required_sublink' in config:
            if not has_required_sublink(current_url, config['required_sublink']):
                # print(f"  ❌ Missing required sublink: {config['required_sublink']}")
                continue

        total_weight = 0
        matched_weight = 0

        for check in config['checks']:
            css = check['css_selector']
            should_exist = check.get('should_exist', True)
            weight = check.get('weight', 1)
            min_count = check.get('min_count', 1)
            text_required = check.get('contains_text')
            iframe_selector = check.get('iframe_selector')

            # print(f"  ➤ Checking '{css}'")

            total_weight += weight
            exists = False

            try:
                # -----------------------
                # 1) BeautifulSoup search
                # -----------------------
                elements = soup.select(css)
                if len(elements) >= min_count:
                    exists = True

                    # Check text if provided
                    if text_required:
                        exists = any(text_required.lower() in el.get_text().lower()
                                     for el in elements)

                # If BeautifulSoup fails → fallback to Playwright
                if not exists:
                    # -----------------------
                    # 2) Playwright search
                    # -----------------------
                    if iframe_selector:
                        frame = page.frame_locator(iframe_selector)
                        locator = frame.locator(css)
                    else:
                        locator = page.locator(css)

                    count = locator.count()

                    if count >= min_count:
                        exists = True

                        # Optional text matching
                        if text_required:
                            txt = locator.all_text_contents()
                            exists = any(text_required.lower() in t.lower() for t in txt)

                # -----------------------
                # Scoring
                # -----------------------
                if should_exist:
                    if exists:
                        matched_weight += weight
                        # print(f"    ✔ FOUND")
                    else:
                        pass
                        # print(f"    ✘ NOT FOUND")
                else:
                    # Should NOT exist
                    if exists:
                        pass
                        # print(f"    ✘ SHOULD NOT EXIST")
                    else:
                        matched_weight += weight
                        # print(f"    ✔ ABSENCE CONFIRMED")

            except Exception as e:
                # print(f"    ⚠ Error: {e}")
                logger.error(f"Error while identifying page: {e}")

        # Calculate page score
        score = matched_weight / total_weight if total_weight else 0
        page_scores[page_name] = score

    # Debug print scores
    # for pn, sc in page_scores.items():
        # print(f"[SCORE] {pn}: {sc}")

    # Best match above threshold
    best_page, best_score = max(page_scores.items(), key=lambda x: x[1]) if page_scores else ('unknown', 0)
    return best_page if best_score >= 0.7 else 'unknown'

