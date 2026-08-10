from selenium.webdriver.common.by import By

from framework.pages.base_page import BasePage


class LoginPage(BasePage):
    HEADING = (By.CSS_SELECTOR, "main h1")
    DISPLAY_NAME = (By.CSS_SELECTOR, '[data-testid="display-name"]')
    EMAIL = (By.CSS_SELECTOR, '[data-testid="email"]')
    PASSWORD = (By.CSS_SELECTOR, '[data-testid="password"]')
    SUBMIT = (By.CSS_SELECTOR, '[data-testid="auth-submit"]')
    TOGGLE_MODE = (By.CSS_SELECTOR, '[data-testid="toggle-auth-mode"]')
    FEEDBACK = (By.CSS_SELECTOR, '[data-testid="feedback"]')

    def load(self) -> "LoginPage":
        self.open()
        self.visible(self.EMAIL)
        return self

    def wait_until_loaded(self) -> "LoginPage":
        self.visible(self.EMAIL)
        return self

    def switch_to_registration(self) -> None:
        if self.heading != "Create your account":
            self.click(self.TOGGLE_MODE)
            self.wait.until(lambda _: self.heading == "Create your account")

    def switch_to_sign_in(self) -> None:
        if self.heading != "Welcome back":
            self.click(self.TOGGLE_MODE)
            self.wait.until(lambda _: self.heading == "Welcome back")

    def register(self, display_name: str, email: str, password: str) -> None:
        self.switch_to_registration()
        self.fill(self.DISPLAY_NAME, display_name)
        self.fill(self.EMAIL, email)
        self.fill(self.PASSWORD, password)
        self.click(self.SUBMIT)

    def sign_in(self, email: str, password: str) -> None:
        self.switch_to_sign_in()
        self.fill(self.EMAIL, email)
        self.fill(self.PASSWORD, password)
        self.click(self.SUBMIT)

    def wait_for_feedback(self, message: str) -> None:
        self.wait.until(lambda _: self.text(self.FEEDBACK) == message)

    @property
    def heading(self) -> str:
        return self.text(self.HEADING)
