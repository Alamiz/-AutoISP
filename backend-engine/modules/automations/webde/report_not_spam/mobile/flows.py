import logging
from playwright.sync_api import Page
from core.humanization.actions import HumanAction
from core.utils.element_finder import deep_find_elements

class ReportNotSpamFlowHandler():
    """Handles different WebDE mobile page flows for Report Not Spam"""
    
    def __init__(self, automation, email: str, password: str, search_text: str):
        self.automation = automation
        self.email = email
        self.password = password
        self.search_text = search_text
        self.logger = logging.getLogger("autoisp")
        # Use automation's human_action/behavior if available
        self.human_action = automation if isinstance(automation, HumanAction) else HumanAction()

    def handle_folder_list_page(self, page: Page) -> str:
        """
        Handle folder list page - navigate to spam folder
        """
        self.logger.info("Detected folder list page - navigating to Spam folder")
        
        self.human_action.human_click(
            page,
            selectors=['ul.sidebar__folder-list > li a[data-webdriver*="SPAM"]'],
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
        
        # Keep processing emails until no more matches are found
        while True:
            # Wait for message list to load
            try:
                self.human_action._find_element_with_humanization(
                    page, 
                    ["div.message-list-panel__content"], 
                    deep_search=True
                )
            except:
                self.logger.warning("Message list not found, might be empty or loading issue")
            
            # Find all email items (fresh scan each time)
            email_items = deep_find_elements(page, "div.message-list-panel__content > li")
            
            found_match = False
            
            for item in email_items:
                # Check text in subject
                # Selector: a > span
                subject_span = item.query_selector("a > span")
                
                if subject_span:
                    text = subject_span.inner_text()
                    if self.search_text.lower() in text.lower():
                        self.logger.info(f"Found matching email: {text}")
                        
                        # Click to open the email
                        email_link = item.query_selector("a")
                        if email_link:
                            self.human_action.human_behavior.click(email_link)
                            page.wait_for_timeout(1500)
                            
                            # Simulate reading by scrolling
                            self.logger.info("Simulating reading...")
                            self.human_action.human_behavior.scroll_page_by(page, 300)
                            
                            # Click mail actions button
                            self.logger.info("Clicking mail actions button")
                            self.human_action.human_click(
                                page,
                                selectors=['ul.toolbar__icon[data-position="left"] > li > a[href*="mailactions"]'],
                                deep_search=True
                            )
                            
                            page.wait_for_timeout(1000)
                            
                            # Click "Not Spam" button
                            self.logger.info("Clicking 'Not Spam' button")
                            self.human_action.human_click(
                                page,
                                selectors=['div.base-page__content div.action-list:nth-child(3) ul li > a[href*="noSpam"]'],
                                deep_search=True
                            )
                            
                            self.logger.info("Reported as not spam")
                            found_match = True
                            
                            # Wait for action to complete
                            page.wait_for_timeout(2000)
                            break  # Exit inner loop to re-scan
            
            # If no match found in this scan, we're done
            if not found_match:
                self.logger.info("No more matching emails found")
                self.automation.action_completed = True
                return "task_completed"
            
            # Otherwise, loop continues to re-scan

    def handle_unknown_page(self, page: Page) -> str:
        """
        Handle unknown page - try to navigate back
        """
        self.logger.warning("Unknown page detected")
        page.goto("https://lightmailer-bs.web.de/")
        return "webde_folder_list_page"
