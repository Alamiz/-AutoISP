# automations/webde/report_not_spam/desktop/handlers.py
"""
State handlers for web.de Desktop Report Not Spam using StatefulFlow.
"""
import logging
from playwright.sync_api import Page
from core.flow_engine.state_handler import StateHandler, HandlerAction
from core.humanization.actions import HumanAction
from core.utils.element_finder import deep_find_elements


class InboxPageHandler(StateHandler):
    """Handle inbox page - navigate to spam folder"""
    
    def __init__(self, human_action: HumanAction, logger=None):
        super().__init__(logger)
        self.human_action = human_action
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            if self.logger:
                self.logger.info("InboxPageHandler: Navigating to Spam folder")
            
            self.human_action.human_click(
                page, selectors=['button.sidebar-folder-icon-spam'], deep_search=True
            )
            page.wait_for_timeout(2000)
            return "continue"
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"InboxPageHandler: Failed - {e}")
            return "retry"


class SpamPageHandler(StateHandler):
    """Handle spam page - report emails as not spam"""
    
    def __init__(self, human_action: HumanAction, search_text: str, automation, logger=None):
        super().__init__(logger)
        self.human_action = human_action
        self.search_text = search_text
        self.automation = automation
        self.reported_email_ids = []
    
    def _search_emails(self, page: Page, keyword: str, search_folder: str):
        """Helper method to search emails"""
        self.human_action.human_fill(
            page, selectors=['input.webmailer-mail-list-search-input__input'],
            text=keyword, deep_search=True
        )

        if search_folder:
            self.human_action.human_click(
                page, selectors=['button.webmailer-mail-list-search-options__button'], deep_search=True
            )
            self.human_action.human_select(
                page, selectors=['select[name="searchParamFolderId"]'],
                value=search_folder, deep_search=True
            )        
            self.human_action.human_click(
                page, selectors=['div.webmailer-mail-list-search-options__container div.lux-button-container--end button[type="submit"]'],
                deep_search=True
            )
        else:
            self.human_action.human_click(
                page, selectors=['button.webmailer-mail-list-search-input__button--submit'], deep_search=True
            )
        
        page.wait_for_timeout(2000)
    
    def handle(self, page: Page) -> HandlerAction:
        try:
            if self.logger:
                self.logger.info(f"SpamPageHandler: Processing emails with text: {self.search_text}")
            
            while True:
                try:
                    self.human_action._find_element_with_humanization(page, ["div.list-mail-list"], deep_search=True)
                except:
                    break
                
                email_items = deep_find_elements(page, "list-mail-item.list-mail-item--root")
                
                if not email_items:
                    break
                
                found_match = False
                
                for item in email_items:
                    try:
                        subject = self.human_action._find_element_with_humanization(item, ["div.list-mail-item__subject"])
                        if self.search_text.lower() not in subject.inner_text().lower():
                            continue
                        
                        found_match = True
                        
                        email_id_attr = item.get_attribute("id")
                        if email_id_attr and email_id_attr.startswith("id"):
                            email_id_number = email_id_attr[2:]
                            self.reported_email_ids.append(email_id_number)
                        
                        self.human_action.human_behavior.click(item)
                        self.human_action.human_behavior.scroll_into_view(item)
                        
                        self.human_action.human_click(
                            page, selectors=['div.list-toolbar__scroll-item section[data-overflow-id="no_spam"] button'],
                            deep_search=True
                        )
                        
                        page.wait_for_timeout(2000)
                        break
                        
                    except Exception as e:
                        continue
                
                if not found_match:
                    break
            
            # Open reported emails in inbox
            if self.reported_email_ids:
                if self.logger:
                    self.logger.info(f"Opening {len(self.reported_email_ids)} reported emails in inbox")
                
                self.human_action.human_click(page, selectors=['button.sidebar-folder-icon-inbox'], deep_search=True)
                page.wait_for_timeout(2000)
                self._search_emails(page, self.search_text, "Posteingang")
                
                for email_id_number in self.reported_email_ids:
                    try:
                        email_items = deep_find_elements(page, "list-mail-item.list-mail-item--root")
                        target_item = None
                        for item in email_items:
                            if item.get_attribute("id") == f"id{email_id_number}":
                                target_item = item
                                break
                        
                        if target_item:
                            self.human_action.human_behavior.click(target_item)
                            page.wait_for_timeout(2000)
                            self.human_action.human_behavior.scroll_into_view(target_item)
                    except Exception as e:
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
            page.goto("https://web.de/")
            return "retry"
        except Exception as e:
            return "abort"
