# automations/webde/report_not_spam/desktop/steps.py
import logging
from playwright.sync_api import Page
from core.humanization.actions import HumanAction
from core.utils.element_finder import deep_find_elements
from core.flow_engine.step import Step, StepResult, StepStatus


class NavigateToSpamStep(Step):
    def run(self, page: Page) -> StepResult:
        try:
            self.logger.info("Navigating to Spam folder")
            self.human.human_click(
                page,
                selectors=['button.sidebar-folder-icon-spam'],
                deep_search=True
            )
            page.wait_for_timeout(2000)
            return StepResult(status=StepStatus.SUCCESS, message="Navigated to Spam folder")
        except Exception as e:
            return StepResult(status=StepStatus.RETRY, message=f"Failed to navigate to Spam: {e}")


class ReportSpamEmailsStep(Step):
    def run(self, page: Page) -> StepResult:
        try:
            keyword = getattr(self.human, "search_text", "")
            self.logger.info(f"Reporting emails with keyword: {keyword}")

            if not hasattr(self.human, "reported_email_ids"):
                self.human.reported_email_ids = []

            while True:
                try:
                    self.human._find_element_with_humanization(page, ["div.list-mail-list"], deep_search=True)
                except:
                    self.logger.warning("Mail list not found, might be empty")

                email_items = deep_find_elements(page, "list-mail-item.list-mail-item--root")
                if not email_items:
                    break

                found_match = False
                for item in email_items:
                    try:
                        subject = self.human._find_element_with_humanization(item, ["div.list-mail-item__subject"])
                        if keyword.lower() in subject.inner_text().lower():
                            found_match = True
                            email_id_attr = item.get_attribute("id")
                            if email_id_attr and email_id_attr.startswith("id"):
                                email_id_number = email_id_attr[2:]
                                self.human.reported_email_ids.append(email_id_number)
                                self.logger.info(f"Stored email ID: {email_id_number}")

                            self.human.human_behavior.click(item)
                            self.human.human_behavior.scroll_into_view(item)
                            self.human.human_click(
                                page,
                                selectors=['div.list-toolbar__scroll-item section[data-overflow-id="no_spam"] button'],
                                deep_search=True
                            )
                            page.wait_for_timeout(2000)
                            break
                    except Exception as e:
                        self.logger.warning(f"Error processing item: {e}")
                        continue

                if not found_match:
                    break

            if getattr(self.human, "reported_email_ids", []):
                return StepResult(status=StepStatus.SUCCESS, message="Emails reported")

            return StepResult(status=StepStatus.SKIP, message="No emails reported")

        except Exception as e:
            return StepResult(status=StepStatus.RETRY, message=f"Failed to report emails: {e}")


class OpenReportedEmailsStep(Step):
    def run(self, page: Page) -> StepResult:
        try:
            email_ids = getattr(self.human, "reported_email_ids", [])
            self.logger.info(f"Opening {len(email_ids)} reported emails in inbox")

            # Navigate to inbox
            self.human.human_click(page, selectors=['button.sidebar-folder-icon-inbox'], deep_search=True)
            page.wait_for_timeout(2000)

            # Search for emails
            keyword = getattr(self.human, "search_text", "")
            self.human.human_fill(
                page,
                selectors=['input.webmailer-mail-list-search-input__input'],
                text=keyword,
                deep_search=True
            )
            self.human.human_click(
                page,
                selectors=['button.webmailer-mail-list-search-input__button--submit'],
                deep_search=True
            )
            page.wait_for_timeout(2000)

            for email_id_number in email_ids:
                email_items = deep_find_elements(page, "list-mail-item.list-mail-item--root")
                target_item = next((i for i in email_items if i.get_attribute("id") == f"id{email_id_number}"), None)
                if not target_item:
                    self.logger.warning(f"Email with ID {email_id_number} not found")
                    continue

                self.human.human_behavior.click(target_item)
                page.wait_for_timeout(2000)
                self.human.human_behavior.scroll_into_view(target_item)
                self.logger.info(f"Opened reported email {email_id_number}")

                # Click link or image inside the email body iframe (desktop)
                try:
                    iframes = deep_find_elements(page, 'iframe[name="detail-body-iframe"]')
                    if iframes:
                        content_frame = iframes[0].content_frame()
                        if content_frame:
                            links = content_frame.query_selector_all("a")
                            if links:
                                self.human.human_behavior.click(links[0])
                                self.logger.info("Clicked link inside email")
                                page.wait_for_timeout(3000)
                            else:
                                imgs = content_frame.query_selector_all("img")
                                if imgs:
                                    self.human.human_behavior.click(imgs[0])
                                    self.logger.info("Clicked image inside email")
                                    page.wait_for_timeout(3000)
                except Exception as e:
                    self.logger.warning(f"Could not click link/img in email: {e}")

            return StepResult(status=StepStatus.SUCCESS, message="All reported emails opened")

        except Exception as e:
            return StepResult(status=StepStatus.RETRY, message=f"Failed to open reported emails: {e}")
