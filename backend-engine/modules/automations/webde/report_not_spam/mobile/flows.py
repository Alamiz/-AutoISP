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
        self.reported_email_ids = []


    def _search_emails(self, page: Page, keyword: str, search_folder: str):
        """Helper method to search emails using WebDE search box"""
        self.logger.info(f"Searching for emails with keyword: {keyword}")
        
        # Type in search input
        self.human_action.human_fill(
            page,
            selectors=['form.search-form input'],
            text=keyword,
        )

        # Click search button
        self.human_action.human_click(
            page,
            selectors=['form.search-form button[type="submit"]'],
        )

        page.wait_for_timeout(2000)
        self.logger.info("Search completed")

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
            
            if not email_items or len(email_items) == 0:
                self.logger.info("No more emails found in list")
                break

            found_match = False
            
            for item in email_items:
                # Check text in subject
                # Selector: a > span
                subject_span = item.query_selector("a > span")
                
                if subject_span:
                    text = subject_span.inner_text()
                    if self.search_text.lower() in text.lower():
                        self.logger.info(f"Found matching email: {text}")

                        # Extract email ID (e.g., from href="./messagedetail?folderId=1733619229933229126&mailIndex=1&mailId=1764755051039737362")
                        email_link = item.query_selector("a.message-list__link")
                        email_link_src = email_link.get_attribute("href")
                        if email_link_src and "mailId" in email_link_src:
                            # Extract id part (e.g., "1764755051039737362")
                            email_id_number = email_link_src.split("mailId=")[1]
                            self.reported_email_ids.append(email_id_number)
                            self.logger.info(f"Stored email ID: {email_id_number}")
                        
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
                break
            
            # Otherwise, loop continues to re-scan

        # After all spam processing is done, open reported emails in inbox
        if len(self.reported_email_ids) > 0:
            self.logger.info(f"Opening {len(self.reported_email_ids)} reported emails in inbox")
            
            # Navigate to folder list page
            self.human_action.human_click(page, selectors=['div.message-list-panel__navigation-bar > ul > li[data-position="left"] > a'])
            page.wait_for_timeout(500)
            
            # Use search to filter emails in inbox
            self._search_emails(page, self.search_text, "Posteingang")
            
            # Open each reported email by matching its ID
            for email_id_number in self.reported_email_ids:
                self.logger.info(f"Looking for email with ID: {email_id_number}")
                
                try:
                    # Find all email items
                    email_items = deep_find_elements(page, "div.message-list-panel__content > li")
                    
                    # Find the email with matching ID
                    target_item = None
                    for item in email_items:
                        item_link = item.query_selector("a.message-list__link")
                        item_src = item_link.get_attribute("href")
                        if email_id_number in item_src:
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
                    self.human_action.human_behavior.scroll_into_view(page=page, y_amount=300)
                    
                    # TODO: Click link inside email
                    # Add your specific link-clicking logic here
                    self.logger.info("Simulated reading email")

                    # Click back button
                    self.human_action.human_click(
                        page, 
                        selectors=['ul.toolbar__icon[data-position="left"] > li:nth-of-type(1) > a'],
                    )
                    self.logger.info("Clicked back button")
                    page.wait_for_timeout(2000)

                except Exception as e:
                    self.logger.error(f"Error opening email {email_id_number} in inbox: {e}")
                    continue
            
            self.logger.info(f"Finished processing {len(self.reported_email_ids)} reported emails in inbox")
        
        # Mark as completed
        self.automation.action_completed = True
        return "task_completed"

    def handle_unknown_page(self, page: Page) -> str:
        """
        Handle unknown page - try to navigate back
        """
        self.logger.warning("Unknown page detected")
        page.goto("https://lightmailer-bs.web.de/")
        return "webde_folder_list_page"
