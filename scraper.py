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

    class Delay:

        def __init__(self, function):
            self._function = function
            self.default_delay = 5

        def __call__(self, *args):
            """
            Decorator that will sleep before executing the function.

            If no argument is specified in the decorator, it will sleep
            for `default_delay` before executing the decorated function.

            If an argument is specified in the decorator, it will sleep
            for that amount of time before executing the decorated
            function.

            Args:
                *args: Function parameters if the decorator parameter
                    is not specified, or the function itself if the
                    decorator parameters are specified.
            """
            # Check that `_function` is a decorator parameter or a function. True if one is set.
            if type(self._function) == int:

                # Set the function to an easy to remember variable
                func = args[0]

                @functools.wraps(func)
                def wrapper(*param_args):
                    # `_function` will be the decorator parameter
                    time.sleep(self._function)
                    # `param_args` are the passed parameters for the function
                    func(*param_args)

                return wrapper
            else:
                # Correct the signature of the function
                functools.update_wrapper(self, self._function)
                # Sleep for the default delay since no decorator param was set
                time.sleep(self.default_delay)
                # Includes `self` due to being used on class methods
                return self._function(self, *args)

    class Wait:
        """
        Args:
            Attributes:
            timeout (int): How long to wait before raising an error
                when locating an element.
            condition (selenium.webdriver.support.expected_conditions):
                Condition that must be met when locating an element.

        Attributes:
            _timeout (int): How long to wait before raising an error
                when locating an element.
            _condition (selenium.webdriver.support.expected_conditions):
                Condition that must be met when locating an element.
        """

        def __init__(self,
                     func,
                     timeout: int = 10,
                     condition=conditions.presence_of_element_located):
            self._func = func
            self._timeout = timeout
            self._condition = condition

        def __call__(self, *func_params, **func_params_kwargs):

            if len(func_params) == 1:
                print(f"I ran with decorators\nfunc_params: {func_params}\nfunc_params_kwargs: {func_params_kwargs}")  # TODO FOR DEBUGGING
                print(f"func: {self._func}\ntimeout: {self._timeout}\ncondition: {self._condition}")  # TODO FOR DEBUGGING

                func = func_params[0]
                self._parent = func.__class__
                print(self._parent)  # TODO FOR DEBUGGING

                # @functools.wraps(func)
                def wrapper(*args, **kwargs):
                    return WebDriverWait(5, timeout=self._func) \
                        .until(self._condition(args), **kwargs)

                return wrapper

            else:
                functools.update_wrapper(self, self._func)
                print(f"I ran without decorators\nfunc_params: {func_params}\nfunc_params_kwargs: {func_params_kwargs}")  # TODO FOR DEBUGGING
                print(f"func: {self._func}\ntimeout: {self._timeout}\ncondition: {self._condition}")  # TODO FOR DEBUGGING
                try:
                    print(self._func.__name__)  # TODO FOR DEBUGGING
                    return WebDriverWait(self._func, timeout=self._timeout) \
                        .until(self._condition(func_params), **func_params_kwargs)
                except:
                    raise

        def __getattr__(self, item):
            return self._parent.get(item)

    @Wait(1)
    def find_element(self, *args, **kwargs):
        super().find_element(*args, **kwargs)


class InstagramScraper(Scraper):

    def __init__(self):
        self._USERNAME = os.getenv('USERNAME')
        self._PASSWORD = os.getenv('PASSWORD')
        super().__init__()

    def home_page(self):
        self.get("https://www.instagram.com")

    def login(self):
        # Find username and password fields
        username_field = self.find_element(By.NAME, "username")
        password_field = self.find_element(By.NAME, "password")

        # Log in
        username_field.send_keys(self._USERNAME)
        password_field.send_keys(self._PASSWORD)
        password_field.send_keys(Keys.ENTER)


if __name__ == "__main__":
    load_dotenv()
    driver = InstagramScraper()
    driver.home_page()
    driver.login()
    # time.sleep(5)

    driver.close()
