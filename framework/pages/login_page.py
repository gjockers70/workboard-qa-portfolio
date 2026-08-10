from selenium.webdriver.common.by import By

from framework.pages.base_page import BasePage


class LoginPage(BasePage):
    HEADING = (By.CSS_SELECTOR, "main h1")
    EMAIL = (By.CSS_SELECTOR, '[data-testid="email"]')
    PASSWORD = (By.CSS_SELECTOR, '[data-testid="password"]')
    SUBMIT = (By.CSS_SELECTOR, '[data-testid="auth-submit"]')

    def load(self) -> "LoginPage":
        self.open()
        self.visible(self.EMAIL)
        return self

    def sign_in(self, email: str, password: str) -> None:
        self.fill(self.EMAIL, email)
        self.fill(self.PASSWORD, password)
        self.click(self.SUBMIT)

    @property
    def heading(self) -> str:
        return self.text(self.HEADING)

