from core.utils.retry_decorators import retry_action
from playwright.sync_api import Page
from core.utils.element_finder import deep_find_elements
from core.flow_engine.step import Step, StepResult
from modules.core.flow_state import FlowResult
from datetime import datetime
import time

class NavigateToSpamStep(Step):
    def run(self, page: Page) -> StepResult:
        try:
            self.logger.info("Navigating to Spam folder", extra={"account_id": self.account.id})
            self.automation.human_click(
                page,
                selectors=['button.sidebar-folder-icon-spam'],
                deep_search=True
            )
            page.wait_for_timeout(2000)
            return StepResult(status=FlowResult.SUCCESS, message="Navigated to Spam folder")
        except Exception as e:
            return StepResult(status=FlowResult.RETRY, message=f"Failed to navigate to Spam: {e}")

class ReportSpamEmailsStep(Step):
    def run(self, page: Page) -> StepResult:
        try:
            keyword = (getattr(self.automation, "search_text", "") or "").lower()
            start_date = getattr(self.automation, "start_date") 
            end_date = getattr(self.automation, "end_date")     

            current_page = 1
            self.logger.info(
                f"Processing emails with keyword='{keyword}' "
                f"between {start_date} and {end_date}", 
                extra={"account_id": self.account.id}
            )

            if not hasattr(self.automation, "reported_email_ids"):
                self.automation.reported_email_ids = []

            while True:
                self.logger.info(f"Processing page {current_page}", extra={"account_id": self.account.id})

                email_items = deep_find_elements(
                    page, "list-mail-item.list-mail-item--root"
                )

                if not email_items:
                    self.logger.info("No emails found on this page", extra={"account_id": self.account.id})
                    break

                index = 0

                while index < len(email_items):
                    item = email_items[index]

                    try:
                        # --- Extract date ---
                        date_el = item.locator("list-date-label.list-mail-item__date")
                        if date_el.count() == 0:
                            raise Exception("Date element not found")

                        ms = date_el.get_attribute("date-in-ms")
                        if not ms:
                            raise Exception("date-in-ms missing")

                        mail_date = datetime.fromtimestamp(
                            int(ms) / 1000
                        ).date()

                        # --- Early stop: first email already older ---
                        if index == 0 and mail_date < start_date:
                            self.logger.info(
                                "First email older than start_date. Stopping pagination.",
                                extra={"account_id": self.account.id}
                            )
                            return self._final_result()

                        # --- Skip out-of-range ---
                        if mail_date > end_date:
                            index += 1
                            continue

                        if mail_date < start_date:
                            return self._final_result()

                        # --- Keyword check ---
                        subject_el = item.locator("div.list-mail-item__subject")
                        if subject_el.count() == 0:
                            index += 1
                            continue

                        subject_text = (subject_el.inner_text() or "").lower()
                        if keyword not in subject_text:
                            index += 1
                            continue

                        self.logger.info(
                            f"Processing email subject='{subject_text[:15]}', date={mail_date}",
                            extra={"account_id": self.account.id}
                        )

                        # --- Open email ---
                        self.click_email_item(item)

                        # --- Scroll content ---
                        self.scroll_content(page)

                        # --- Report as not spam ---
                        self.click_not_spam(page)

                        # 🔴 DOM CHANGED → re-query + reset index
                        email_items = deep_find_elements(
                            page, "list-mail-item.list-mail-item--root"
                        )
                        index = 0
                        continue

                    except Exception as e:
                        self.logger.warning(
                            f"Failed processing email: {e}",
                            extra={"account_id": self.account.id}
                        )
                        index += 1
                        continue

                # --- Next page ---
                try:
                    next_button = self.automation._find_element_with_humanization(
                        page,
                        ["button.list-paging-footer__page-next"],
                        deep_search=True
                    )
                    if next_button and not next_button.is_disabled():
                        self.automation.human_behavior.click(next_button)
                        current_page += 1
                        continue
                    break
                except Exception as e:
                    self.logger.warning(
                        f"Pagination failed: {e}",
                        extra={"account_id": self.account.id}
                    )
                    break

            return self._final_result()

        except Exception as e:
            return StepResult(
                status=FlowResult.RETRY,
                message=f"Failed to report emails: {e}"
            )
    
    @retry_action()
    def click_email_item(self, item):
        try:
            self.automation.human_behavior.click(item)
        except Exception as e:
            self.logger.warning(
                f"Failed to click email item: {e}",
                extra={"account_id": self.account.id}
            )

    @retry_action()
    def scroll_content(self, page: Page):
        try:
            iframe = self.automation._find_element_with_humanization(
                page,
                selectors=['iframe[name="detail-body-iframe"]'],
                deep_search=True
            )
            # iframe is a Locator, we need ElementHandle to call content_frame()
            frame = iframe.element_handle().content_frame()
            body = self.automation._find_element_with_humanization(
                frame, ["body"]
            )
            self.automation.human_behavior.scroll_into_view(body)
        except Exception as e:
            self.logger.warning(
                f"Failed to scroll content: {e}",
                extra={"account_id": self.account.id}
            )
    
    @retry_action()
    def click_not_spam(self, page: Page):
        try:
            self.automation.human_click(
                page,
                selectors=[
                    'div.list-toolbar__scroll-item '
                    'section[data-overflow-id="no_spam"] button'
                ],
                deep_search=True
            )
        except Exception as e:
            self.logger.warning(
                f"Failed to click not spam: {e}",
                extra={"account_id": self.account.id}
            )
    
    def _final_result(self) -> StepResult:
        if getattr(self.automation, "reported_email_ids", []):
            return StepResult(
                status=FlowResult.SUCCESS,
                message="Emails reported within date range"
            )

        return StepResult(
            status=FlowResult.SKIP,
            message="No emails found within date range"
        )

class OpenReportedEmailsStep(Step):
    def run(self, page: Page) -> StepResult:
        try:
            keyword = (getattr(self.automation, "search_text", "") or "").lower()
            start_dt = getattr(self.automation, "start_date")
            end_dt = getattr(self.automation, "end_date")

            self.logger.info(
                f"Opening emails with keyword='{keyword}' "
                f"between {start_dt} and {end_dt}",
                extra={"account_id": self.account.id}
            )

            # Navigate to inbox
            self._navigate_to_inbox(page)

            # Fill search input
            self._fill_search_input(page, keyword)

            # Open search options
            self.open_search_options(page)
 
            # Select inbox and submit search
            self.select_inbox_and_submit(page)

            if not hasattr(self.automation, "pending_closures"):
                self.automation.pending_closures = []

            found_any = False
            current_page = 1

            while True:
                self.logger.info(f"Processing page {current_page}",extra={"account_id": self.account.id})

                email_items = deep_find_elements(
                    page, "list-mail-item.list-mail-item--root"
                )

                if not email_items:
                    self.logger.warning("No emails found on this page",extra={"account_id": self.account.id})
                    break

                index = 0
                while index < len(email_items):
                    item = email_items[index]

                    try:
                        self._cleanup_pending_pages()
                        email_id = item.get_attribute("id")
                        self.logger.info(f"Processing email {email_id}",extra={"account_id": self.account.id})

                        # --- Extract datetime from date-in-ms ---
                        date_el = item.locator("list-date-label.list-mail-item__date")
                        if date_el.count() == 0:
                            self.logger.warning("No date found on this email",extra={"account_id": self.account.id})
                            index += 1
                            continue

                        ms = date_el.get_attribute("date-in-ms")
                        if not ms:
                            self.logger.warning("No date-in-ms found on this email",extra={"account_id": self.account.id})
                            index += 1
                            continue

                        mail_dt = datetime.fromtimestamp(
                            int(ms) / 1000
                        ).date()

                        # --- Early stop: everything else is older ---
                        if index == 0 and mail_dt < start_dt:
                            self.logger.info("First email older than start_datetime. Stopping.",extra={"account_id": self.account.id})
                            return self._final(found_any)

                        # --- Range filter ---
                        if mail_dt > end_dt:
                            self.logger.warning(f"mail date: {mail_dt} is newer than end_datetime: {end_dt}, skipping",extra={"account_id": self.account.id})
                            index += 1
                            continue

                        if mail_dt < start_dt:
                            self.logger.warning(f"mail date: {mail_dt} is older than start_datetime: {start_dt}, stopping",extra={"account_id": self.account.id})
                            return self._final(found_any)

                        # --- Subject ---
                        subject_el = item.locator("div.list-mail-item__subject")
                        if subject_el.count() == 0:
                            self.logger.warning("No subject found on this email", extra={"account_id": self.account.id})
                            index += 1
                            continue

                        subject_text = (subject_el.get_attribute("title") or "").lower()

                        if keyword not in subject_text:
                            index += 1
                            continue

                        found_any = True
                        self.logger.info(f"Opening email '{subject_text}' @ {mail_dt}",extra={"account_id": self.account.id})

                        # --- Actions ---
                        self._click_email_item(item, page)

                        frame = self._scroll_content(page)

                        self._add_to_favorites(page)

                        self._scroll_to_top(frame)

                        self._click_link_or_image(frame, page)

                        # Re-query for safety (DOM not reordered)
                        email_items = deep_find_elements(
                            page, "list-mail-item.list-mail-item--root"
                        )

                        index += 1
                        continue

                    except Exception as e:
                        self.logger.warning(f"Failed processing email: {e}", extra={"account_id": self.account.id})
                        index += 1
                        continue

                # --- Pagination ---
                try:
                    next_button = self.automation._find_element_with_humanization(
                        page,
                        ["button.list-paging-footer__page-next"],
                        deep_search=True
                    )
                    if next_button and not next_button.is_disabled():
                        self.automation.human_behavior.click(next_button)
                        page.wait_for_timeout(2000)
                        current_page += 1
                        continue
                    break
                except Exception:
                    break

            # Final cleanup (gentle)
            self._cleanup_pending_pages(force=False)

            return self._final(found_any)

        except Exception as e:
            return StepResult(
                status=FlowResult.RETRY,
                message=f"Failed to open reported emails: {e}"
            )

    @retry_action()
    def _navigate_to_inbox(self, page):
        try:
            self.automation.human_click(
                page,
                selectors=["button.sidebar-folder-icon-inbox"],
                deep_search=True
            )
            page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.warning(f"Failed to navigate to inbox: {e}", extra={"account_id": self.account.id})

    @retry_action()
    def _fill_search_input(self, page, keyword):
        try:
            search_input = deep_find_elements(
                page,
                css_selector="input.webmailer-mail-list-search-input__input",
            )
            if search_input:
                search_input[0].fill(keyword)
        except Exception as e:
            self.logger.warning(f"Failed to fill search input: {e}", extra={"account_id": self.account.id})
    
    @retry_action()
    def open_search_options(self, page):
        try:
            self.automation.human_click(
                page,
                selectors=["button.webmailer-mail-list-search-options__button"],
                deep_search=True
            )
        except Exception as e:
            self.logger.warning(f"Failed to open search options: {e}", extra={"account_id": self.account.id})
    
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
            self.logger.warning(f"Failed to select inbox and submit search: {e}", extra={"account_id": self.account.id})

    @retry_action()
    def _click_email_item(self, item, page):
        try:
            self.automation.human_behavior.click(item)
            page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.warning(f"Click inside email failed: {e}", extra={"account_id": self.account.id})

    @retry_action()
    def _scroll_content(self, page):
        try:
            iframe = self.automation._find_element_with_humanization(
                page,
                selectors=["iframe[name='detail-body-iframe']"],
                deep_search=True
            )
            # iframe is a Locator, we need ElementHandle to call content_frame()
            frame = iframe.element_handle().content_frame()
            body = self.automation._find_element_with_humanization(
                frame, ["body"]
            )
            self.automation.human_behavior.scroll_into_view(body)

            return frame
        except Exception as e:
            self.logger.warning(f"Scroll content failed: {e}", extra={"account_id": self.account.id})
    
    def _scroll_to_top(self, frame):
        try:
            body = self.automation._find_element_with_humanization(
                frame, ["body"]
            )
            # Scroll the body to top
            body.evaluate("element => element.scrollTop = 0")
        except Exception as e:
            self.logger.warning(f"Scroll to top failed: {e}", extra={"account_id": self.account.id})
    
    @retry_action()
    def _add_to_favorites(self, page):
        try:
            # Find and click the button
            button = self.automation._find_element_with_humanization(
                page,
                selectors=["button.detail-favorite-marker__unselected"],
                deep_search=True,
                timeout=2000
            )
            button.click()
            
            # Wait a moment for the DOM to update
            page.wait_for_timeout(500)
            
            # Verify the button now has the selected class
            selected_button = self.automation._find_element_with_humanization(
                page,
                selectors=["button.detail-favorite-marker__selected"],
                deep_search=True,
                timeout=2000
            )
            
            if not selected_button:
                raise Exception("Failed to verify favorite was added - selected class not found")
                
        except Exception as e:
            self.logger.warning(f"Failed to add to favorites: {e}", extra={"account_id": self.account.id})
            raise  # Re-raise to trigger retry

    def _find_first_clickable(self, container):
        """Find the first visible and clickable link or image inside a container."""
        if not container:
            return None
        
        # Search for all links and images
        targets = container.query_selector_all("a, img")
        for target in targets:
            try:
                if target.is_visible():
                    box = target.bounding_box()
                    if box and box['width'] > 0 and box['height'] > 0:
                        return target
            except:
                continue
        return None

    def _cleanup_pending_pages(self, force=False):
        """Close pending pages that have been open for >30 seconds, or all if force=True."""
        if not hasattr(self.automation, "pending_closures"):
            return
            
        now = time.time()
        remaining = []
        for p, close_time in self.automation.pending_closures:
            if force or now >= close_time:
                try:
                    p.close()
                    self.logger.info("Pending tab closed successfully (Thread-safe)", extra={"account_id": self.account.id})
                except Exception as e:
                    self.logger.warning(f"Failed to close pending tab: {e}", extra={"account_id": self.account.id})
            else:
                remaining.append((p, close_time))
        self.automation.pending_closures = remaining

    @retry_action()
    def _click_link_or_image(self, frame, page):
        try:
            if frame:
                target = self._find_first_clickable(frame)

                if target:
                    try:
                        with page.context.expect_page(timeout=5000) as new_page_info:
                            # Use a shorter timeout for the click itself to avoid 30s hangs
                            self.automation.human_behavior.click(target, timeout=5000)
                        
                        new_page = new_page_info.value
                        self.logger.info("New tab opened, will close in 30s (Queue-based)", extra={"account_id": self.account.id})
                        
                        if not hasattr(self.automation, "pending_closures"):
                            self.automation.pending_closures = []
                        self.automation.pending_closures.append((new_page, time.time() + 30))
                        
                    except Exception as e:
                        self.logger.warning(f"Failed to open new page from click: {e}", extra={"account_id": self.account.id})
                        # Fallback if no new page is opened (e.g. click failed or same tab navigation)
                        try:
                            self.automation.human_behavior.click(target, timeout=5000)
                            page.wait_for_timeout(3000)
                        except:
                            pass
        except Exception as e:
            self.logger.warning(f"Click inside email failed: {e}", extra={"account_id": self.account.id})

    def _final(self, found: bool) -> StepResult:
        if found:
            return StepResult(
                status=FlowResult.SUCCESS,
                message="All matching emails in datetime range processed."
            )
        return StepResult(
            status=FlowResult.SKIP,
            message="No matching emails found in datetime range."
        )
