import logging
import time
from playwright.sync_api import Page

logger = logging.getLogger("autoisp")

def get_mailcheck_extension_id(page: Page) -> str:
    """
    Detect the runtime extension ID for MailCheck/GMX MailCheck.
    Navigates to chrome://extensions to find it.
    """
    try:
        logger.info("Detecting MailCheck extension ID...")
        # Navigate to extensions page
        page.goto("chrome://extensions")
        page.wait_for_load_state("domcontentloaded")
        
        # Evaluate script to find extension by name
        # We need to pierce shadow DOM
        extension_id = page.evaluate("""() => {
            const manager = document.querySelector('extensions-manager');
            const itemList = manager.shadowRoot.querySelector('extensions-item-list');
            const items = itemList.shadowRoot.querySelectorAll('extensions-item');
            
            for (const item of items) {
                const shadow = item.shadowRoot;
                const nameEl = shadow.querySelector('#name');
                if (nameEl && (nameEl.textContent.includes('MailCheck') || nameEl.textContent.includes('GMX MailCheck') || nameEl.textContent.includes('WEB.DE MailCheck'))) {
                    return item.getAttribute('id');
                }
            }
            return null;
        }""")
        
        if extension_id:
            logger.info(f"Found MailCheck extension ID: {extension_id}")
            return extension_id
            
        logger.warning("MailCheck extension not found in chrome://extensions")
        return None
        
    except Exception as e:
        logger.error(f"Failed to detect extension ID: {e}")
        return None

def get_mailcheck_options_url(page: Page) -> str:
    """Get the options URL for the MailCheck extension"""
    ext_id = get_mailcheck_extension_id(page)
    if ext_id:
        return f"chrome-extension://{ext_id}/pages/options.html"
    return None

def get_mailcheck_mail_panel_url(page: Page) -> str:
    """Get the mail panel URL for the MailCheck extension"""
    ext_id = get_mailcheck_extension_id(page)
    if ext_id:
        return f"chrome-extension://{ext_id}/pages/mail-panel.html"
    return None

def get_rektcaptcha_extension_id(page: Page) -> str:
    """
    Detect the runtime extension ID for rektCaptcha.
    Navigates to chrome://extensions to find it.
    """
    try:
        logger.info("Detecting rektCaptcha extension ID...")
        # Navigate to extensions page
        page.goto("chrome://extensions")
        page.wait_for_load_state("domcontentloaded")
        
        # Evaluate script to find extension by name
        extension_id = page.evaluate("""() => {
            const manager = document.querySelector('extensions-manager');
            const itemList = manager.shadowRoot.querySelector('extensions-item-list');
            const items = itemList.shadowRoot.querySelectorAll('extensions-item');
            
            for (const item of items) {
                const shadow = item.shadowRoot;
                const nameEl = shadow.querySelector('#name');
                if (nameEl && nameEl.textContent.includes('rektCaptcha')) {
                    return item.getAttribute('id');
                }
            }
            return null;
        }""")
        
        if extension_id:
            logger.info(f"Found rektCaptcha extension ID: {extension_id}")
            return extension_id
            
        logger.warning("rektCaptcha extension not found in chrome://extensions")
        return None
        
    except Exception as e:
        logger.error(f"Failed to detect rektCaptcha extension ID: {e}")
        return None

def get_rektcaptcha_popup_url(page: Page) -> str:
    """Get the popup URL for the rektCaptcha extension"""
    ext_id = get_rektcaptcha_extension_id(page)
    if ext_id:
        return f"chrome-extension://{ext_id}/popup.html"
    return None
