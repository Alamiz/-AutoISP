# automations/webde/report_not_spam/mobile/handlers.py
"""
State handlers for web.de Mobile Report Not Spam using StatefulFlow.
"""
import logging
from playwright.sync_api import Page
from core.flow_engine.state_handler import StateHandler, HandlerAction
from core.humanization.actions import HumanAction
from core.utils.element_finder import deep_find_elements


class FolderListPageHandler(StateHandler):
    """Handle folder list page - navigate to spam folder"""
    
    def __init__(self, human_action: HumanAction, logger=None):
        super().__init__(logger)
        self.human_action = human_action
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            if self.logger:
                self.logger.info("FolderListPageHandler: Navigating to Spam folder")
            
            self.human_action.human_click(
                page, selectors=['ul.sidebar__folder-list > li a[data-webdriver*="SPAM"]'],
                deep_search=True
            )
            page.wait_for_timeout(2000)
            return "continue"
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"FolderListPageHandler: Failed - {e}")
            return "retry"


class SpamPageHandler(StateHandler):
    """Handle spam page - report emails as not spam"""
    
    def __init__(self, human_action: HumanAction, search_text: str, automation, logger=None):
        super().__init__(logger)
        self.human_action = human_action
        self.search_text = search_text
        self.automation = automation
        self.reported_email_ids = []
    
    def _search_emails(self, page: Page, keyword: str):
        """Helper method to search emails"""
        self.human_action.human_fill(page, selectors=['form.search-form input'], text=keyword)
        self.human_action.human_click(page, selectors=['form.search-form button[type="submit"]'])
        page.wait_for_timeout(2000)
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            if self.logger:
                self.logger.info(f"SpamPageHandler: Processing emails with text: {self.search_text}")
            
            while True:
                try:
                    self.human_action._find_element_with_humanization(
                        page, ["div.message-list-panel__content"], deep_search=True
                    )
                except:
                    break
                
                email_items = deep_find_elements(page, "div.message-list-panel__content > li")
                
                if not email_items:
                    break

                found_match = False
                
                for item in email_items:
                    subject_span = item.query_selector("a > span")
                    
                    if subject_span and self.search_text.lower() in subject_span.inner_text().lower():
                        found_match = True
                        
                        email_link = item.query_selector("a.message-list__link")
                        email_link_src = email_link.get_attribute("href")
                        if email_link_src and "mailId" in email_link_src:
                            email_id_number = email_link_src.split("mailId=")[1]
                            self.reported_email_ids.append(email_id_number)
                        
                        self.human_action.human_behavior.click(email_link)
                        page.wait_for_timeout(1500)
                        
                        self.human_action.human_behavior.scroll_page_by(page, 300)
                        
                        self.human_action.human_click(
                            page, selectors=['ul.toolbar__icon[data-position="left"] > li > a[href*="mailactions"]'],
                            deep_search=True
                        )
                        page.wait_for_timeout(1000)
                        
                        self.human_action.human_click(
                            page, selectors=['div.base-page__content div.action-list:nth-child(3) ul li > a[href*="noSpam"]'],
                            deep_search=True
                        )
                        
                        page.wait_for_timeout(2000)
                        break
                
                if not found_match:
                    break
            
            # Open reported emails in inbox
            if self.reported_email_ids:
                self.human_action.human_click(
                    page, selectors=['div.message-list-panel__navigation-bar > ul > li[data-position="left"] > a']
                )
                page.wait_for_timeout(500)
                
                self._search_emails(page, self.search_text)
                
                for email_id_number in self.reported_email_ids:
                    try:
                        email_items = deep_find_elements(page, "div.message-list-panel__content > li")
                        target_item = None
                        for item in email_items:
                            item_link = item.query_selector("a.message-list__link")
                            if item_link and email_id_number in item_link.get_attribute("href"):
                                target_item = item
                                break
                        
                        if target_item:
                            self.human_action.human_behavior.click(target_item)
                            page.wait_for_timeout(2000)
                            self.human_action.human_behavior.scroll_into_view(page=page, y_amount=300)
                            
                            self.human_action.human_click(
                                page, selectors=['ul.toolbar__icon[data-position="left"] > li:nth-of-type(1) > a']
                            )
                            page.wait_for_timeout(2000)
                    except Exception:
                        continue
            
            self.automation.action_completed = True
            return "continue"
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"SpamPageHandler: Failed - {e}")
            return "abort"


class UnknownPageHandler(StateHandler):
    """Handle unknown pages"""
    
    def __init__(self, human_action: HumanAction = None, logger=None):
        super().__init__(logger)
        self.human_action = human_action
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            page.goto("https://lightmailer-bs.web.de/")
            return "retry"
        except Exception:
            return "abort"
