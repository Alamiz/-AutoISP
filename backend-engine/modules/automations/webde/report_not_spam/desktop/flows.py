import logging
from playwright.sync_api import Page
from core.humanization.actions import HumanAction
from core.utils.element_finder import deep_find_elements

class ReportNotSpamFlowHandler():
    """Handles different WebDE page flows for Report Not Spam"""
    
    def __init__(self, automation, email: str, password: str, search_text: str):
        self.automation = automation
        self.email = email
        self.password = password
        self.search_text = search_text
        self.logger = logging.getLogger("autoisp")
        # Use automation's human_action/behavior if available, or create new
        self.human_action = automation if isinstance(automation, HumanAction) else HumanAction()

    def handle_inbox_page(self, page: Page) -> str:
        """
        Handle inbox page - navigate to spam folder
        """
        self.logger.info("Detected inbox page - navigating to Spam folder")
        
        self.human_action.human_click(
            page,
            selectors=['button[data-component-path="navigation_sidebar.spam"]', 'button.sidebar-folder-icon-spam'],
            deep_search=True
        )
        
        self.logger.info("Clicked Spam folder")
        page.wait_for_timeout(2000)
        
        return "webde_spam"

    def handle_spam_page(self, page: Page) -> str:
        """
        Handle spam page - search for email and report not spam
        """
        self.logger.info(f"Detected spam page - searching for email with text: {self.search_text}")
        
        # Wait for list to load
        try:
            self.human_action._find_element_with_humanization(page, ["div.list-mail-list"], deep_search=True)
        except:
            self.logger.warning("Mail list not found, might be empty or loading issue")
        
        # Find all email items using deep search
        email_items = deep_find_elements(page, "list-mail-item.list-mail-item--root")
        
        found_match = False
        
        for item in email_items:
            # Check text in subject/preview
            # Selector: div.list-mail-item__lines-container > div.list-mail-item__second-line > div
            subject_div = item.query_selector("div.list-mail-item__lines-container > div.list-mail-item__second-line > div")
            
            if subject_div:
                text = subject_div.inner_text()
                if self.search_text.lower() in text.lower():
                    self.logger.info(f"Found matching email: {text}")
                    
                    # Click to open (simulate human behavior)
                    self.human_action.human_behavior.click(item)
                    
                    # Simulate reading
                    self.logger.info("Simulating reading...")
                    self.human_action.human_behavior.scroll_into_view(item)
                    
                    # Click "Not Spam" button
                    self.logger.info("Clicking 'Not Spam' button")
                    self.human_action.human_click(
                        page,
                        selectors=['div.list-toolbar__scroll-item section[data-overflow-id="no_spam"] button'],
                        deep_search=True
                    )
                    
                    self.logger.info("Reported as not spam")
                    found_match = True
                    
                    # Wait for action to complete/list to update
                    page.wait_for_timeout(2000)
                    # break # Process one at a time and re-scan
        
        if found_match:
            return "webde_spam" # Re-scan the list
            
        # If no match found on current page, check pagination
        next_buttons = deep_find_elements(page, "div.list-paging-footer__right > button.list-paging-footer__page-next")
        
        if next_buttons:
            next_btn = next_buttons[0]
            # Check if disabled
            is_disabled = next_btn.get_attribute("disabled") is not None or "disabled" in next_btn.get_attribute("class")
            
            if not is_disabled:
                self.logger.info("Clicking next page")
                self.human_behavior.click(next_btn)
                page.wait_for_timeout(2000)
                return "webde_spam"
                
        # No match and no next page (or disabled)
        self.logger.info("No more matching emails found")
        self.automation.action_completed = True
        return "task_completed"

    def handle_unknown_page(self, page: Page) -> str:
        """
        Handle unknown page - try to go to inbox or login
        """
        self.logger.warning("Unknown page detected")
        # Maybe try to go to inbox?
        page.goto("https://web.de/")
        return "webde_inbox"