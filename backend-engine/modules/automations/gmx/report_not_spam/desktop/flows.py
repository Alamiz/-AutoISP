import logging
import re
from playwright.sync_api import Page
from core.humanization.actions import HumanAction
from core.utils.element_finder import deep_find_elements

class ReportNotSpamFlowHandler():
    """Handles different GMX page flows for Report Not Spam"""
    
    def __init__(self, automation, email: str, password: str, search_text: str):
        self.automation = automation
        self.email = email
        self.password = password
        self.search_text = search_text
        self.logger = logging.getLogger("autoisp")
        # Use automation's human_action/behavior if available, or create new
        self.human_action = automation if isinstance(automation, HumanAction) else HumanAction()
        # Track email IDs of emails reported as not spam
        self.reported_email_ids = []

    def handle_inbox_page(self, page: Page) -> str:
        """
        Handle inbox page - navigate to spam folder
        """
        self.logger.info("Detected inbox page - navigating to Spam folder")
        
        self.human_action.human_click(
            page,
            selectors=['button.sidebar-folder-icon-spam'],
            deep_search=True
        )
        
        self.logger.info("Clicked Spam folder")
        page.wait_for_timeout(2000)
        
        return "gmx_spam"

    def _search_emails(self, page: Page, keyword: str):
        """Helper method to search emails using GMX search box"""
        self.logger.info(f"Searching for emails with keyword: {keyword}")
        
        # Type in search input
        self.human_action.human_fill(
            page,
            selectors=['input.webmailer-mail-list-search-input__input'],
            text=keyword,
            deep_search=True
        )
        
        # Click search button
        self.human_action.human_click(
            page,
            selectors=['button.webmailer-mail-list-search-input__button--submit'],
            deep_search=True
        )
        
        page.wait_for_timeout(2000)
        self.logger.info("Search completed")

    def handle_spam_page(self, page: Page) -> str:
        """
        Handle spam page - search for email and report not spam
        """
        self.logger.info(f"Detected spam page - searching for email with text: {self.search_text}")
        
        # Use GMX search to filter emails
        self._search_emails(page, self.search_text)
        
        # Keep processing emails until no more matches are found
        while True:
            # Wait for list to load
            try:
                self.human_action._find_element_with_humanization(page, ["div.list-mail-list"], deep_search=True)
            except:
                self.logger.warning("Mail list not found, might be empty or loading issue")
            
            # Find all email items using deep search (fresh scan each time)
            email_items = deep_find_elements(page, "list-mail-item.list-mail-item--root")
            
            if not email_items or len(email_items) == 0:
                self.logger.info("No more emails found in list")
                break
            
            found_match = False
            
            for item in email_items:
                try:
                    # Extract email ID (e.g., from id="id1764755051039737362")
                    email_id_attr = item.get_attribute("id")
                    if email_id_attr and email_id_attr.startswith("id"):
                        # Extract numeric part (e.g., "1764755051039737362")
                        email_id_number = email_id_attr[2:]  # Remove "id" prefix
                        self.reported_email_ids.append(email_id_number)
                        self.logger.info(f"Stored email ID: {email_id_number}")
                    
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
                    break  # Exit inner loop to re-scan
                    
                except Exception as e:
                    self.logger.warning(f"Error processing item (likely detached): {e}")
                    continue  # Skip to next item
            
            # If no match found in this scan, we're done
            if not found_match:
                self.logger.info("No more matching emails found")
                break
        
        # After all spam processing is done, open reported emails in inbox
        if len(self.reported_email_ids) > 0:
            self.logger.info(f"Opening {len(self.reported_email_ids)} reported emails in inbox")
            
            # Navigate to inbox
            self.human_action.human_click(page, selectors=['button.sidebar-folder-icon-inbox'], deep_search=True)
            page.wait_for_timeout(2000)
            
            # Use search to filter emails in inbox
            self._search_emails(page, self.search_text)
            
            # Open each reported email by matching its ID
            for email_id_number in self.reported_email_ids:
                self.logger.info(f"Looking for email with ID: {email_id_number}")
                
                try:
                    # Find all email items
                    email_items = deep_find_elements(page, "list-mail-item.list-mail-item--root")
                    
                    # Find the email with matching ID
                    target_item = None
                    for item in email_items:
                        item_id = item.get_attribute("id")
                        if item_id == f"id{email_id_number}":
                            target_item = item
                            self.logger.info(f"Found matching email with ID: {email_id_number}")
                            break
                    
                    if not target_item:
                        self.logger.warning(f"Email with ID {email_id_number} not found in inbox")
                        continue
                    
                    # Click the email to open it
                    self.human_action.human_behavior.click(target_item)
                    self.logger.info("Opened email in inbox")
                    page.wait_for_timeout(2000)
                    
                    # Simulate reading
                    self.human_action.human_behavior.scroll_into_view(target_item)
                    page.wait_for_timeout(1500)
                    
                    # TODO: Click link inside email
                    # Add your specific link-clicking logic here
                    self.logger.info("Simulated reading email")
                    
                except Exception as e:
                    self.logger.error(f"Error opening email {email_id_number} in inbox: {e}")
                    continue
            
            self.logger.info(f"Finished processing {len(self.reported_email_ids)} reported emails in inbox")
        
        # Mark as completed
        self.automation.action_completed = True
        return "task_completed"

    def handle_unknown_page(self, page: Page) -> str:
        """
        Handle unknown page - try to go to inbox or login
        """
        self.logger.warning("Unknown page detected")
        # Maybe try to go to inbox?
        page.goto("https://www.gmx.net/mail/client/inbox")
        return "gmx_inbox"