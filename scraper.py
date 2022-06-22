from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from os import getenv
import functools
import time


class Scraper:
    BRAVE_PATH = getenv("BRAVE_PATH")

    def __init__(self):
        pass
        # Configure webdriver to use Brave Browser
        self.options = webdriver.ChromeOptions()
        self.options.binary_location = self.BRAVE_PATH

        # Create Service
        self.service = Service(ChromeDriverManager().install())

        # Create Driver
        self.driver = webdriver.Chrome(service=self.service, options=self.options)

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

    @Delay
    def test(self, *args, **kwargs):
        print(*args, **kwargs)


if __name__ == "__main__":
    apple = Scraper()

