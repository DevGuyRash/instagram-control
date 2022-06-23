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

import json


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
             by=None,
             value=None,
             condition=conditions.element_to_be_clickable,
             ):
        try:
            return self.driver_wait.until(condition((by, value)))
        except TimeoutError:
            # Enable to allow users to enter new data in
            # by_method = input("Timed out attempting to locate. "
            #                   "Please provide a new search method: ")
            # value = input("Please enter a new value: ")
            # return self.wait(by_method, value)
            return None

    def close(self):
        super().close()


class InstagramScraper(Scraper):

    def __init__(self):
        self._USERNAME = os.getenv('INSTA_USERNAME')
        self._PASSWORD = os.getenv('INSTA_PASSWORD')
        with open("urls.json") as file:
            urls = json.load(file)
            self.HOME = urls["general"]["home"]
            self.NOTIFICATIONS = urls["general"]["notifications"]

        super().__init__()

    def home_page(self):

        self.get(self.HOME)

    def login(self):
        # Find username and password fields
        username_field = self.wait(By.NAME, "username")
        password_field = self.wait(By.NAME, "password")

        # Log in
        username_field.send_keys(self._USERNAME)
        password_field.send_keys(self._PASSWORD)
        password_field.send_keys(Keys.ENTER)
        try:
            result = self.driver_wait.until(conditions.url_changes('https://www.instagram.com/'))
            print("Did change")
        except TimeoutError:
            print("Did not change")
        # if self.login_error():
        #     print("You failed")
        #     exit(-1)
        # else:
        #     print("You in!")

    def login_error(self):
        error_message = self.wait(By.CSS_SELECTOR, "p#slfErrorAlert")
        if error_message:
            return True
        else:
            return False

    def decline_notifs(self):
        not_now = self.wait(By.XPATH, '//*[@id="mount_0_0_M7"]/div/div[1]/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div/div[3]/button[2]')
        try:
            not_now.click()
        except AttributeError:
            self.home_page()


if __name__ == "__main__":
    load_dotenv()
    driver = InstagramScraper()
    driver.home_page()
    driver.login()
    time.sleep(5)

    driver.close()
