from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.support.ui import WebDriverWait


Locator = tuple[str, str]


class BasePage:
    def __init__(self, driver: WebDriver, base_url: str, wait_seconds: float = 10) -> None:
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.wait = WebDriverWait(driver, wait_seconds)

    def open(self, path: str = "") -> None:
        self.driver.get(f"{self.base_url}{path}")

    def visible(self, locator: Locator) -> WebElement:
        return self.wait.until(expected.visibility_of_element_located(locator))

    def clickable(self, locator: Locator) -> WebElement:
        return self.wait.until(expected.element_to_be_clickable(locator))

    def click(self, locator: Locator) -> None:
        self.clickable(locator).click()

    def fill(self, locator: Locator, value: str) -> None:
        element = self.visible(locator)
        element.clear()
        element.send_keys(value)

    def text(self, locator: Locator) -> str:
        return self.visible(locator).text.strip()

