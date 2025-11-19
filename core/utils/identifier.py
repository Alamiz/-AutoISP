from playwright.sync_api import Page
from typing import Optional
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
from test_data.signatures import PAGE_SIGNATURES

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
    Identify page using CSS selectors with conditions:
    - contains_text
    - min_count
    - should_exist (True = reward for presence, False = reward for absence)
    - iframe_selector (to search within iframe content)
    """

    html_content = page.content()
    soup = BeautifulSoup(html_content, 'html.parser')
    page_signatures = PAGE_SIGNATURES
    page_scores = {}

    for page_name, config in page_signatures.items():
        # Check required sublink first
        if 'required_sublink' in config:
            if not has_required_sublink(current_url, config['required_sublink']):
                continue
        
        total_possible = 0
        matched_score = 0
        
        for check in config['checks']:
            # Skip if English is required but page isn't English
            if check.get('require_english') and not is_page_english(html_content):
                continue
                
            weight = check.get('weight', 1)
            should_exist = check.get('should_exist', True)
            
            try:
                # Determine where to search for elements
                if 'iframe_selector' in check:
                    # Search within iframe
                    elements = get_iframe_elements(page, check['iframe_selector'], check['css_selector'])
                else:
                    # Search in main page
                    elements = soup.select(check['css_selector'])
                
                min_count = check.get('min_count', 1)
                
                # Always add to total possible for this check
                total_possible += weight
                
                # Check if element exists with minimum count
                element_exists = len(elements) >= min_count
                
                # If element exists, check additional conditions
                if element_exists and check.get('contains_text'):
                    element_exists = any(
                        check['contains_text'].lower() in el.get_text().lower()
                        for el in elements
                    )
                
                # Score based on should_exist expectation
                if should_exist:
                    # Positive check: reward for presence, penalize for absence
                    if element_exists:
                        matched_score += weight
                else:
                    # Negative check: reward for absence, penalize for presence
                    if element_exists:
                        matched_score -= weight  # Penalize for presence
                    else:
                        matched_score += weight  # Reward for absence
                
            except Exception as e:
                print(f"Error processing check '{check.get('name', 'unnamed')}': {e}")
                continue
        
        # Always store the score, even if 0
        if total_possible > 0:
            page_scores[page_name] = max(0, matched_score) / total_possible
        else:
            page_scores[page_name] = 0

    # Return best match above threshold
    best_match = max(page_scores.items(), key=lambda x: x[1]) if page_scores else None
    return best_match[0] if best_match and best_match[1] >= 0.7 else 'unknown'

def get_iframe_elements(page: Page, iframe_selector: str, element_selector: str):
    """
    Get elements from within an iframe.
    
    Args:
        page: Playwright Page object
        iframe_selector: CSS selector to find the iframe
        element_selector: CSS selector to find elements within the iframe
        
    Returns:
        List of BeautifulSoup elements found within the iframe
    """
    try:
        # Get the first matching frame
        frame_element = page.query_selector(iframe_selector)
        if not frame_element:
            return []
        
        # Get the frame's content frame
        content_frame = frame_element.content_frame()
        if not content_frame:
            return []
        
        # Get iframe's HTML content
        iframe_html = content_frame.content()
        iframe_soup = BeautifulSoup(iframe_html, 'html.parser')
        
        # Find elements within iframe
        return iframe_soup.select(element_selector)
        
    except Exception as e:
        print(f"Error accessing iframe with selector '{iframe_selector}': {e}")
        return []