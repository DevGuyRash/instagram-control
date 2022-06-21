from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import functools
import time


class Scraper:
    BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

    def __init__(self):
        pass
        # # Configure webdriver to use Brave Browser
        # self.options = webdriver.ChromeOptions()
        # self.options.binary_location = self.BRAVE_PATH
        #
        # # Create Service
        # self.service = Service(ChromeDriverManager().install())
        #
        # # Create Driver
        # self.driver = webdriver.Chrome(service=self.service, options=self.options)

    class Delay:

        def __init__(self, function):
            self._function = function
            functools.update_wrapper(self, function)

        def __call__(self, *args, **kwargs):
            time.sleep(2)
            return self._function(self, *args, kwargs)

    @Delay
    def test(self, *args, **kwargs):
        print(*args, **kwargs)


if __name__ == "__main__":
    apple = Scraper()

    apple.test("apple", 1, 2, ban="apple")
