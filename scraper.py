from sessions import InstagramSession
from spoof import Proxies, Proxy
from bs4 import BeautifulSoup
import requests
import json


class InstagramBot:

    def __init__(self):
        with open("urls.json", encoding='utf-8') as f:
            self.URLS = json.load(f)["instagram"]

        self.session = InstagramSession()
        self.proxies = Proxies()
        # self.session.login()

    def fetch_tag_info(self):
        pass

    def get(self, url: str, proxy: bool = False, *args, **kwargs):
        if proxy:
            # Have user choose what type of proxy they want
            print("1: Random")
            print("2: Specific")
            print("For your proxy (1 or 2): ", end='')
            # choice = self.get_input({"1", "2"})
            choice = 2  # TODO FOR DEBUGGING
            if choice == "1":
                # If user wants a random one
                proxy = self.proxies.get_proxies(single=True)
                print("Your generated proxy:")
                print(proxy)
                proxies = {
                    "https": proxy.proxy,
                    "http": proxy,
                }
            else:
                proxy = None

                # Get valid proxy
                while True:
                    proxy = self.get_user_proxy()
                    if proxy:
                        break
                    else:
                        print("Resetting selection...")

                print("Your generated proxy:")
                print(proxy)
                proxies = {
                    "https": proxy.proxy,
                    "http": proxy.proxy,
                }

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

    def get_test_link(self):
        URL = "https://i.instagram.com/api/v1/tags/web_info/?tag_name=realestatephotography"
        proxy = Proxies.extract_by_type(self.proxies.get_proxies(),
                                        {
                                            "code": "US",
                                            "https": "yes",
                                            "last_checked": str(60 * 5),
                                        },
                                        single=True)
        # try:
        response = requests.get(URL,
                                headers=self.session.headers,
                                cookies=self.session.cookies,
                                # proxies={
                                #     "https": proxy.proxy,
                                #     "http": proxy.proxy,
                                # }
                                )
        # except requests.exceptions.ProxyError:
        # except:
        #     print("Proxy error, retrying...")
        #     return self.get_test_link()
        # else:
        return [response, BeautifulSoup(response.text, "lxml")]

    def get_input(self, valid_options: set):
        user_input = input()
        if user_input not in valid_options:
            print("Invalid selection! Please try again: ", end='')
            return self.get_input(valid_options)

        return user_input


if __name__ == "__main__":
    drive = InstagramBot()
    drive.get("qaa", proxy=True)

