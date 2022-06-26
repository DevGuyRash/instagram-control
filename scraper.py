import requests
import datetime
from bs4 import BeautifulSoup
import json
from dotenv import load_dotenv
import os
import pickle


class InstaScraper:

    def __init__(self):
        # Log in
        self.login()

    def login(self):
        pass


class UserSession(requests.Session):

    def __init__(self):
        # Load .env file
        load_dotenv()
        # Create base url routes
        with open("urls.json", encoding="utf-8") as file:
            self.URLS = json.load(file)

        # Get your user-agent from:
        # https://www.whatismybrowser.com/detect/what-http-headers-is-my-browser-sending
        # Create the needed headers without the csrf_token
        self.insta_headers = {
            "referer": self.URLS['HOME'],
            "user-agent": os.getenv('USER-AGENT'),
            "x-requested-with": 'XMLHttpRequest',
        }

        # Form data to be posted to login page. Password added in `login`.
        self.insta_payload = {
            "username": os.getenv('INSTA_USERNAME'),
            "opIntoOneTap": {},
            "queryParams": {},
        }

        super().__init__()

    def _get_csrf_token(self):
        return self.get(self.URLS['HOME']).cookies['csrftoken']

    def _udpate_headers_payload(self):
        # Add password to payload
        self.insta_payload["enc_password"] = f"#PWD_INSTAGRAM_BROWSER:0:" \
                                             f"{datetime.datetime.now().timestamp()}:" \
                                             f"{os.getenv('INSTA_PASSWORD')}"

        # Add csrf token to headers
        self.insta_headers['x-csrftoken'] = self._get_csrf_token()

    def _save_cookies(self, filename: str = "cookies"):
        with open(filename, 'wb') as f:
            pickle.dump(self.cookies._cookies, f)

    def _load_cookies(self, filename: str = "cookies"):
        """Loads any existing cookie files to the session"""
        if os.path.exists(os.path.abspath(filename)):
            with open(filename, 'rb') as f:
                cookie = pickle.load(f)
                if cookie:
                    print("Cookie found")
                    jar = requests.cookies.RequestsCookieJar()
                    jar._cookies = cookie
                    self.cookies = jar
                    print("Cookie successfully configured")
                    return True
                else:
                    print("Failed to load a cookie")
                    return False
        else:
            print("Cookies file does not exist")
            return False

    def login(self):
        """
        Logs in with either existing cookie or a newly made one.

        Will search for a cookie file, and if one is not found, it will
        create and save a new one.

        Returns:
            `Requests` object of attempted log in if a new
        """
        if not self._load_cookies():
            # Makes sure that the timestamp and csrf_token are current
            self._udpate_headers_payload()
            retval = self.post(self.URLS['LOGIN'],
                               headers=self.headers,
                               data=self.insta_payload)
            if retval.status_code == 200:
                print("Login successful")
            self._save_cookies()
            print("New cookie created")
            return retval
        else:
            retval = requests.get("https://www.instagram.com/explore/tags/realestatephotography/")
            print("Login Successful")
            return retval


if __name__ == "__main__":
    apple = UserSession()
    # apple._udpate_headers_payload()
    # apple.save_cookies()
    print(apple.login())
