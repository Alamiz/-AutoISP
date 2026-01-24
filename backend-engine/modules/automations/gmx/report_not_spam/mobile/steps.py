from playwright.sync_api import Page
from core.humanization.actions import HumanAction
from core.utils.element_finder import deep_find_elements
from core.flow_engine.step import Step, StepResult, StepStatus
from core.utils.retry_decorators import retry_action
from core.utils.date_utils import parse_german_mail_date


class NavigateToSpamStep(Step):
    """Navigate from folder list to spam folder."""

    @retry_action(max_attempts=3, delay=0.5)
    def _click_spam_folder(self, page):
        self.automation.human_click(
            page,
            selectors=['ul.sidebar__folder-list > li a[data-webdriver*="SPAM"]'],
            deep_search=True
        )

        self.logger.info("Navigated to Spam folder", extra={"account_id": self.account.id})
    
    def run(self, page: Page) -> StepResult:
        try:
            self.logger.info("Navigating to Spam folder", extra={"account_id": self.account.id})
            self._click_spam_folder(page)
            page.wait_for_timeout(2000)
            return StepResult(status=StepStatus.SUCCESS)
        except Exception as e:
            return StepResult(status=StepStatus.RETRY, message=f"Failed to navigate to Spam: {e}")

class ReportSpamEmailsStep(Step):
    def run(self, page: Page) -> StepResult:
        try:
            keyword = getattr(self.automation, "search_text", "").lower()
            start_date = getattr(self.automation, "start_date") 
            end_date = getattr(self.automation, "end_date")     

            current_page = 1
            self.logger.info(
                f"Processing emails with keyword='{keyword}' "
                f"between {start_date} and {end_date}", 
                extra={"account_id": self.account.id}
            )


            while True:
                page.wait_for_selector("div.message-list-panel__content")
                page.wait_for_timeout(1000)
                email_items = page.query_selector_all("li.message-list__item")

                if not email_items:
                    self.logger.info("No emails found on this page", extra={"account_id": self.account.id})
                    break
                
                index = 0
                while index < len(email_items):
                    try:
                        item = email_items[index]
                        
                        # self.logger.info(f"Processing email {index + 1}/{len(email_items)}")
                        # --- Extract date from <list-date-label> ---
                        date_el = item.query_selector("dd.mail-header__date")
                        if not date_el:
                            self.logger.warning("Date element not found", extra={"account_id": self.account.id})
                            index += 1
                            continue
                        
                        date_title = date_el.get_attribute("title")
                        if not date_title:
                            self.logger.warning("Date title not found", extra={"account_id": self.account.id})
                            index += 1
                            continue

                        mail_date = parse_german_mail_date(date_title)

                        # --- Early stop: all next emails are older ---
                        if index == 0 and mail_date < start_date:
                            self.logger.info("First email older than start_date. Stopping pagination.", extra={"account_id": self.account.id})
                            return self._final_result()

                        # --- Skip out-of-range ---
                        if mail_date > end_date:
                            index += 1
                            continue

                        if mail_date < start_date:
                            self.logger.warning(f"mail date: {mail_date} is older than start_datetime: {start_date}, aborting", extra={"account_id": self.account.id})
                            return self._final_result()

                        # --- Keyword check ---
                        subject_el = item.query_selector("dd.mail-header__subject")
                        if not subject_el:
                            self.logger.warning("Subject element not found", extra={"account_id": self.account.id})
                            index += 1
                            continue
                        
                        subject_text = subject_el.inner_text().lower()
                        if keyword not in subject_text:
                            index += 1
                            continue
                        
                        self.logger.info(
                            f"Processing email '{subject_text}' @ {mail_date}", extra={"account_id": self.account.id}
                        )

                        # --- Open email ---
                        self.click_email_item(item)
                        # --- Scroll content ---
                        self.scroll_content(page)

                        # --- Report as not spam ---
                        self.click_not_spam(page)

                        # Re-query after DOM change
                        page.wait_for_selector("div.message-list-panel__content")
                        page.wait_for_timeout(1000)
                        email_items = page.query_selector_all("li.message-list__item")
                        self.logger.info(f"Re-queried email items: {len(email_items)}", extra={"account_id": self.account.id})
                        
                        # DON'T increment index - reprocess same position with new list
                        # continue without index += 1

                    except Exception as e:
                        self.logger.warning(f"Failed processing email: {e}", extra={"account_id": self.account.id})
                        index += 1
                        continue

                # --- Next page ---
                try:
                    next_button = self.automation._find_element_with_humanization(
                        page,
                        ["ul.paging-toolbar li[data-position='right'] > a[href*='messagelist']"]
                    )
                    if next_button:
                        self.automation.human_behavior.click(next_button)
                        current_page += 1
                        continue
                    break
                except Exception as e:
                    self.logger.warning(f"Pagination failed: {e}", extra={"account_id": self.account.id})
                    break

            return self._final_result()

        except Exception as e:
            return StepResult(
                status=StepStatus.RETRY,
                message=f"Failed to report emails: {e}"
            )
    
    @retry_action()
    def click_email_item(self, item):
        try:
            self.automation.human_behavior.click(item)
            self.logger.info("Clicked email item", extra={"account_id": self.account.id})
        except Exception as e:
            self.logger.warning(f"Failed to click email item: {e}", extra={"account_id": self.account.id})

    @retry_action()
    def mark_email_unread(self, item, page):
        try:
            self.automation.human_behavior.hover(item)
            self.automation.human_click(
                page,
                selectors=["button.list-mail-item__read"],
                deep_search=True
            )
            self.logger.info("Marked email unread", extra={"account_id": self.account.id})
        except Exception as e:
            self.logger.warning(f"Failed to mark email unread: {e}", extra={"account_id": self.account.id})
    
    @retry_action()
    def scroll_content(self, page: Page):
        try:
            iframe = self.automation._find_element_with_humanization(
                page,
                selectors=['iframe#bodyIFrame']
            )
            frame = iframe.content_frame()
            body = self.automation._find_element_with_humanization(
                frame, ["body"]
            )
            self.automation.human_behavior.scroll_into_view(body)
            self.logger.info("Scrolled content", extra={"account_id": self.account.id})
        except Exception as e:
            self.logger.warning(f"Failed to scroll content: {e}", extra={"account_id": self.account.id})
    
    @retry_action()
    def click_not_spam(self, page: Page):
        try:
            self.automation.human_click(
                page,
                selectors=[
                    'a[href*="mailactions"]'
                ]
            )
            page.wait_for_timeout(750)

            self.automation.human_click(
                page,
                selectors=[
                    'a[href*="noSpam"]'
                ]
            )
            self.logger.info("Clicked not spam", extra={"account_id": self.account.id})
        except Exception as e:
            self.logger.warning(f"Failed to click not spam: {e}", extra={"account_id": self.account.id})
    
    def _final_result(self) -> StepResult:
        if getattr(self.automation, "reported_email_ids", []):
            return StepResult(
                status=StepStatus.SUCCESS,
                message="Emails reported within date range"
            )

        return StepResult(
            status=StepStatus.SKIP,
            message="No emails found within date range"
        )


class OpenReportedEmailsStep(Step):
    def run(self, page: Page) -> StepResult:
        try:
            keyword = getattr(self.automation, "search_text", "").lower()
            start_dt = getattr(self.automation, "start_date")
            end_dt = getattr(self.automation, "end_date")

            self.logger.info(
                f"Opening emails with keyword='{keyword}' "
                f"between {start_dt} and {end_dt}",
                extra={"account_id": self.account.id}
            )

            # Navigate to inbox
            self._navigate_to_inbox(page)

            found_any = False
            current_page = 1

            while True:
                page.wait_for_selector("div.message-list-panel__content")
                page.wait_for_timeout(1000)
                email_items = page.query_selector_all("li.message-list__item")

                if not email_items:
                    self.logger.warning("No emails found on this page", extra={"account_id": self.account.id})
                    break
                
                index = 0
                while index < len(email_items):
                    try:
                        item = email_items[index]

                        index += 1
                        
                        email_subject = item.query_selector("dd.mail-header__subject")
                        
                        if not email_subject:
                            continue
                        email_subject = email_subject.text_content().strip().lower()

                        # --- Extract date from date element title ---
                        date_el = item.query_selector("dd.mail-header__date")
                        if not date_el:
                            continue

                        date_title = date_el.get_attribute("title")
                        if not date_title:
                            continue

                        mail_date = parse_german_mail_date(date_title)
                        if not mail_date:
                            continue

                        # --- Early stop: everything else is older ---
                        if index == 0 and mail_date < start_dt:
                            self.logger.info(
                                "First email older than start_datetime. Stopping.",
                                extra={"account_id": self.account.id}
                            )
                            return self._final(found_any)

                        # --- Range filter ---
                        if mail_date > end_dt:
                            continue

                        if mail_date < start_dt:
                            self.logger.warning(f"mail date: {mail_date} is older than start_datetime: {start_dt}, aborting", extra={"account_id": self.account.id})
                            return self._final(found_any)

                        if keyword not in email_subject:
                            continue

                        found_any = True
                        self.logger.info(
                            f"Processing email '{email_subject}' @ {mail_date}",
                            extra={"account_id": self.account.id}
                        )

                        # Open email
                        self._click_email_item(item, page)

                        # Scroll content
                        frame = self._scroll_content(page)

                        # Click link or image
                        self._click_link_or_image(frame, page)

                        # Click back button
                        self._click_back_button(page)

                        self.logger.info("Email processed successfully", extra={"account_id": self.account.id})

                        # Re-query after DOM change
                        page.wait_for_selector("div.message-list-panel__content")
                        page.wait_for_timeout(1000)
                        email_items = page.query_selector_all("li.message-list__item")
                        self.logger.info(f"Re-queried {len(email_items)} emails", extra={"account_id": self.account.id})

                    except Exception as e:
                        self.logger.warning(
                            f"Failed processing email: {e}", extra={"account_id": self.account.id}
                        )
                        index += 1
                        continue


                # --- Pagination ---
                try:
                    next_button = self.automation._find_element_with_humanization(
                        page,
                        ["ul.paging-toolbar li[data-position='right'] > a[href*='messagelist']"]
                    )
                    if next_button:
                        self.automation.human_behavior.click(next_button)
                        current_page += 1
                        continue
                    break
                except Exception as e:
                    self.logger.warning(f"Pagination failed: {e}", extra={"account_id": self.account.id})
                    break

            return self._final(found_any)

        except Exception as e:
            return StepResult(
                status=StepStatus.RETRY,
                message=f"Failed to open reported emails: {e}"
            )

    @retry_action()
    def _navigate_to_inbox(self, page):
        try:
            self.automation.human_click(
                page,
                selectors=["a[href*='folderlist']"],
            )
            page.wait_for_timeout(2000)

            self.automation.human_click(
                page,
                selectors=["ul.sidebar__folder-list li.sidebar__folder-list-item:nth-of-type(1)"],
            )
            page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.warning(
                f"Failed to navigate to inbox: {e}", extra={"account_id": self.account.id}
            )

    @retry_action()
    def _fill_search_input(self, page):
        try:
            search_input = deep_find_elements(
                page,
                css_selector="input.webmailer-mail-list-search-input__input",
            )
            if search_input:
                search_input[0].fill(keyword)
        except Exception as e:
            self.logger.warning(
                f"Failed to fill search input: {e}", extra={"account_id": self.account.id}
            )
    
    @retry_action()
    def open_search_options(self, page):
        try:
            self.automation.human_click(
                page,
                selectors=["button.webmailer-mail-list-search-options__button"],
                deep_search=True
            )
        except Exception as e:
            self.logger.warning(
                f"Failed to open search options: {e}", extra={"account_id": self.account.id}
            )
    
    @retry_action()
    def select_inbox_and_submit(self, page):
        try:
            # Select inbox
            self.automation.human_select(
                page,
                selectors=[
                    "div.webmailer-mail-list-search-options__container select#folderSelect"
                ],
                label="Posteingang",
                deep_search=True
            )

            # Submit search
            self.automation.human_click(
                page,
                selectors=[
                    "div.webmailer-mail-list-search-options__container button[type='submit']"
                ],
                deep_search=True
            )
        except Exception as e:
            self.logger.warning(
                f"Failed to select inbox and submit search: {e}", extra={"account_id": self.account.id}
            )

    @retry_action()
    def _click_email_item(self, item, page):
        try:
            self.automation.human_behavior.click(item)
            page.wait_for_timeout(2000)
            self.logger.info("Clicked email item", extra={"account_id": self.account.id})
        except Exception as e:
            self.logger.warning(
                f"Click inside email failed: {e}", extra={"account_id": self.account.id}
            )

    @retry_action()
    def _scroll_content(self, page):
        try:
            iframe = self.automation._find_element_with_humanization(
                page,
                selectors=["iframe#bodyIFrame"]
            )
            frame = iframe.content_frame()
            body = self.automation._find_element_with_humanization(
                frame, ["body"]
            )
            self.automation.human_behavior.scroll_into_view(body)

            self.logger.info("Scrolled content", extra={"account_id": self.account.id})
            return frame
        except Exception as e:
            self.logger.warning(
                f"Scroll content failed: {e}", extra={"account_id": self.account.id}
            )
    
    @retry_action()
    def _add_to_favorites(self):
        try:
            self.automation.human_click(
                page,
                selectors=[
                    "button.detail-favorite-marker__unselected"
                ],
                deep_search=True,
                timeout=5000
            )
            self.logger.info("Added to favorites", extra={"account_id": self.account.id})
        except Exception:
            pass
    
    @retry_action()
    def _click_link_or_image(self, frame, page):
        try:
            if frame:
                links = frame.query_selector_all("a")
                if links:
                    self.automation.human_behavior.click(links[0])
                    page.wait_for_timeout(3000)
                else:
                    imgs = frame.query_selector_all("img")
                    if imgs:
                        self.automation.human_behavior.click(imgs[0])
                        page.wait_for_timeout(3000)
            self.logger.info("Clicked link or image", extra={"account_id": self.account.id})
        except Exception as e:
            self.logger.warning(
                f"Click inside email failed: {e}", extra={"account_id": self.account.id}
            )
    
    @retry_action()
    def _click_back_button(self, page):
        try:
            self.automation.human_click(
                page,
                selectors=[
                    "a[href*='messagelist']"
                ]
            )
            self.logger.info("Clicked back button", extra={"account_id": self.account.id})
        except Exception as e:
            self.logger.warning(
                f"Click back button failed: {e}", extra={"account_id": self.account.id}
            )

    def _final(self, found: bool) -> StepResult:
        if found:
            return StepResult(
                status=StepStatus.SUCCESS,
                message="All matching emails in datetime range processed."
            )
        return StepResult(
            status=StepStatus.SKIP,
            message="No matching emails found in datetime range."
        )
