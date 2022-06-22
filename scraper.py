# Selenium Driver setup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
import selenium.webdriver.support.expected_conditions as conditions

# Selenium config setup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Environment variables
from dotenv import load_dotenv
import os

import functools
import time


class Scraper(webdriver.Chrome):

    def __init__(self):
        # Configure webdriver to use Brave Browser
        self._options = webdriver.ChromeOptions()
        self._options.binary_location = os.getenv('BRAVE_PATH')

        # Create Service
        self._service = Service(ChromeDriverManager().install())

        # Create Driver
        super().__init__(service=self._service, options=self._options)

        # Webdriver Explicit Wait (timeout is in seconds)
        self.driver_wait = WebDriverWait(self, timeout=10)

    def wait(self,
             by=By.CSS_SELECTOR,
             value="",
             condition=conditions.element_to_be_clickable,
             ):
        try:
            return self.driver_wait.until(condition((by, value)))
        except TimeoutError:
            by_method = input("Timed out attempting to locate. "
                              "Please provide a new search method: ")
            value = input("Please enter a new value: ")
            return self.wait(by_method, value)

    def close(self):
        time.sleep(20)
        super().close()


class InstagramScraper(Scraper):

    def __init__(self):
        self._USERNAME = os.getenv('INSTA_USERNAME')
        self._PASSWORD = os.getenv('INSTA_PASSWORD')
        super().__init__()

    def home_page(self):
        self.get("https://www.instagram.com")

    def login(self):
        # Find username and password fields
        username_field = self.wait(By.NAME, "username")
        password_field = self.wait(By.NAME, "password")

        # Log in
        username_field.send_keys(self._USERNAME)
        password_field.send_keys(self._PASSWORD)
        password_field.send_keys(Keys.ENTER)


if __name__ == "__main__":
    load_dotenv()
    driver = InstagramScraper()
    driver.home_page()
    driver.login()
    time.sleep(5)

    driver.close()
