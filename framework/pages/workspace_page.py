from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select

from framework.pages.base_page import BasePage


class WorkspacePage(BasePage):
    HEADING = (By.CSS_SELECTOR, ".app-shell > header h1")
    PROFILE_SUMMARY = (By.CSS_SELECTOR, ".app-shell > header .profile span")
    SIGN_OUT = (By.CSS_SELECTOR, '[data-testid="sign-out"]')
    FEEDBACK = (By.CSS_SELECTOR, '[data-testid="feedback"]')
    TASK_TITLE = (By.CSS_SELECTOR, '[data-testid="task-title"]')
    TASK_DESCRIPTION = (By.CSS_SELECTOR, '[data-testid="task-description"]')
    CREATE_TASK = (By.CSS_SELECTOR, '[data-testid="create-task"]')
    TASK_SEARCH = (By.CSS_SELECTOR, '[data-testid="task-search"]')
    TASK_FILTER = (By.CSS_SELECTOR, '[data-testid="task-filter"]')
    TASK_CARDS = (By.CSS_SELECTOR, '[data-testid="task-card"]')
    PROFILE_NAME = (By.CSS_SELECTOR, '[data-testid="profile-name"]')
    SAVE_PROFILE = (By.CSS_SELECTOR, '[data-testid="save-profile"]')
    TEAM_TASKS = (By.CSS_SELECTOR, '[data-testid="team-tasks"]')
    MY_TASKS = (By.CSS_SELECTOR, '[data-testid="my-tasks"]')

    def wait_until_loaded(self) -> "WorkspacePage":
        self.visible(self.HEADING)
        self.clickable(self.SIGN_OUT)
        return self

    @property
    def heading(self) -> str:
        return self.text(self.HEADING)

    @property
    def profile_summary(self) -> str:
        return self.text(self.PROFILE_SUMMARY)

    def wait_for_feedback(self, message: str) -> None:
        self.wait.until(lambda _: self.text(self.FEEDBACK) == message)

    def task_cards(self) -> list[WebElement]:
        return self.driver.find_elements(*self.TASK_CARDS)

    def task_card(self, title: str) -> WebElement:
        def matching_card(_driver) -> WebElement | bool:
            for card in self.task_cards():
                headings = card.find_elements(By.CSS_SELECTOR, '[data-testid="task-title-text"]')
                if headings and headings[0].text.strip() == title:
                    return card
            return False

        return self.wait.until(matching_card)

    def has_task(self, title: str) -> bool:
        try:
            return any(
                heading.text.strip() == title
                for card in self.task_cards()
                for heading in card.find_elements(By.CSS_SELECTOR, '[data-testid="task-title-text"]')
            )
        except StaleElementReferenceException:
            return True

    def task_titles(self) -> set[str]:
        return {
            heading.text.strip()
            for card in self.task_cards()
            for heading in card.find_elements(By.CSS_SELECTOR, '[data-testid="task-title-text"]')
        }

    def wait_for_titles(self, expected_titles: set[str]) -> None:
        def titles_match(_driver) -> bool:
            try:
                return self.task_titles() == expected_titles
            except StaleElementReferenceException:
                return False

        self.wait.until(titles_match)

    def create_task(self, title: str, description: str = "") -> None:
        self.fill(self.TASK_TITLE, title)
        self.fill(self.TASK_DESCRIPTION, description)
        self.click(self.CREATE_TASK)
        self.wait_for_feedback("Task created")
        self.task_card(title)

    def task_description(self, title: str) -> str:
        return self.task_card(title).find_element(By.CSS_SELECTOR, '[data-testid="task-description-text"]').text.strip()

    def task_action_labels(self, title: str) -> set[str]:
        return {button.text.strip() for button in self.task_card(title).find_elements(By.CSS_SELECTOR, ".task-actions button")}

    def toggle_task(self, title: str, expected_message: str) -> None:
        self.task_card(title).find_element(By.CSS_SELECTOR, '[data-testid="task-toggle"]').click()
        self.wait_for_feedback(expected_message)

    def edit_task(self, current_title: str, new_title: str, new_description: str) -> None:
        self.task_card(current_title).find_element(By.CSS_SELECTOR, '[data-testid="task-edit"]').click()
        title_prompt = self.wait.until(lambda driver: driver.switch_to.alert)
        title_prompt.send_keys(new_title)
        title_prompt.accept()
        description_prompt = self.wait.until(lambda driver: driver.switch_to.alert)
        description_prompt.send_keys(new_description)
        description_prompt.accept()
        self.wait_for_feedback("Task updated")
        self.task_card(new_title)

    def cancel_task_deletion(self, title: str) -> None:
        self.task_card(title).find_element(By.CSS_SELECTOR, '[data-testid="task-delete"]').click()
        self.wait.until(lambda driver: driver.switch_to.alert).dismiss()
        self.task_card(title)

    def delete_task(self, title: str) -> None:
        self.task_card(title).find_element(By.CSS_SELECTOR, '[data-testid="task-delete"]').click()
        self.wait.until(lambda driver: driver.switch_to.alert).accept()
        self.wait_for_feedback("Task deleted")
        self.wait.until(lambda _: not self.has_task(title))

    def set_search(self, value: str) -> None:
        self.fill(self.TASK_SEARCH, value)

    def set_filter(self, value: str) -> None:
        Select(self.visible(self.TASK_FILTER)).select_by_value(value)

    def update_profile(self, display_name: str) -> None:
        self.fill(self.PROFILE_NAME, display_name)
        self.click(self.SAVE_PROFILE)
        self.wait_for_feedback("Profile updated")
        self.wait.until(lambda _: display_name in self.profile_summary)

    def open_team_tasks(self) -> None:
        self.click(self.TEAM_TASKS)
        self.wait.until(lambda _: self.heading == "Team tasks")

    def sign_out(self) -> None:
        self.click(self.SIGN_OUT)
