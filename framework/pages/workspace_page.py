from selenium.webdriver.common.by import By

from framework.pages.base_page import BasePage


class WorkspacePage(BasePage):
    HEADING = (By.CSS_SELECTOR, ".app-shell > header h1")
    PROFILE_SUMMARY = (By.CSS_SELECTOR, ".app-shell > header .profile span")
    SIGN_OUT = (By.XPATH, '//button[normalize-space()="Sign out"]')

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

