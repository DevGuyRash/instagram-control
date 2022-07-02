from sessions import InstagramSession
from spoof import Proxies, Proxy
from bs4 import BeautifulSoup
import requests
import json
import os


class InstagramBot:

    def __init__(self):
        with open("urls.json", encoding='utf-8') as f:
            self.URLS = json.load(f)["instagram"]

        self.session = InstagramSession()
        self.proxies = Proxies()
        self.session.login()

    def fetch_tag_info(self,
                       proxy: bool = False,
                       save: bool = False,
                       *args,
                       **kwargs) -> dict:
        """Get json data of any instagram tag"""
        # Get user tag to look up
        tag = input("Please enter a tag to research: ").casefold()
        # Create url params
        query = {"tag_name": tag}
        response = self.get(url=self.URLS['tag-info'],
                            proxy=proxy,
                            params=query,
                            *args,
                            **kwargs)

        soup = BeautifulSoup(response.text, features='lxml')
        json_data = soup.find('p').string
        if save:
            try:
                os.mkdir(os.path.abspath('json'))
            except FileExistsError:
                pass

            # Save html file if True
            with open(f"json/{tag}.json", 'w', encoding='utf-8') as f:
                f.write(json_data)

        return json.loads(json_data)

    def get(self,
            url: str,
            proxy: bool = False,
            *args,
            **kwargs) -> requests.models.Response:
        """
        Applies proxies and user-agent randomization to a requests GET.

        If `proxy` is `True`, then the user will select either a random
        proxy, or attributes to look for in a proxy. A random proxy
        from a list of proxies that meet the criteria will be selected
        and applied to the session request.

        If `user_agent` is `True`, then a random user-agent will be
        applied to the request.

        If the proxy is bad, then a timeout error will be raised. Try
        to use a newer or more elite proxy if this happens.

        Args:
            url: Url to send the GET to.
            proxy: Whether to add a proxy to the request.
            *args: Any additional arguments to add to the request.
            **kwargs: Any additional arguments to add to the request.

        Returns:
            A requests `Response` object if successful.
        """
        if proxy:
            # Have user choose what type of proxy they want
            print("1: Random")
            print("2: Specific")
            print("For your proxy (1 or 2): ", end='')
            choice = self.get_input({"1", "2"})
            if choice == "1":
                # If user wants a random one
                proxy = self.proxies.get_proxies(single=True)
                print("Your generated proxy:")
                print(proxy)
                # Set up proxies dict to apply to session request.
                proxies = {
                    "https": proxy.proxy,
                    "http": proxy,
                }
            else:

                # Get valid proxy
                while True:
                    proxy = self.get_user_proxy()
                    if proxy:
                        break
                    else:
                        # If no proxies were found
                        print("Resetting selection...")
                        print()  # Spacer for text

                print("Your generated proxy:")
                print(proxy)
                # Set up proxies dict to apply to session request.
                proxies = {
                    "https": proxy.proxy,
                    "http": proxy.proxy,
                }

            print("If you receive a timeout error, then the proxy is no "
                  "longer good. Please try a different one.")
        else:

            proxies = {}

        return self.session.get(url, proxies=proxies, *args, **kwargs)

    def get_user_proxy(self):
        """Get a proxy that meets user defined standards and return it."""
        proxy_extract_settings = self.proxies.get_usr_proxy_settings()
        proxy = Proxies.extract_by_type(self.proxies.get_proxies(),
                                        proxy_extract_settings,
                                        single=True)

        return proxy

    def get_input(self, valid_options: set):
        user_input = input()
        if user_input not in valid_options:
            print("Invalid selection! Please try again: ", end='')
            return self.get_input(valid_options)

        return user_input


if __name__ == "__main__":
    drive = InstagramBot()
    retval = drive.fetch_tag_info()
    print(retval.keys())
