from sessions import InstagramSession
from spoof import Proxies
from bs4 import BeautifulSoup
import requests
import random


class InstagramBot:

    def __init__(self):
        self.session = InstagramSession()
        self.proxies = Proxies()

        # self.session.login()

    def get_test_link(self):
        proxy = Proxies.extract_by_type(self.proxies.proxies,
                                        {
                                            "code": "US",
                                            "https": "yes",
                                            "last_checked": "50000",
                                        })
        for item in proxy:
            print(item)
            print()
        # URL = "https://www.instagram.com/"
        # try:
        #     response = requests.get(URL,
        #                             headers=self.session.headers,
        #                             cookies=self.session.cookies,
        #                             proxies={
        #                                 "https": proxy.proxy,
        #                                 "http": proxy.proxy,
        #                                 "last_checked": "60",
        #                             }
        #                             )
        # except requests.exceptions.ProxyError:
        #     print("Proxy error")
        # else:
        #     return [response, BeautifulSoup(response.text, "html.parser")]


if __name__ == "__main__":
    drive = InstagramBot()
    drive.get_test_link()

