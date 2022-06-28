import requests
import requests.utils
from requests.cookies import RequestsCookieJar
import datetime
import json
from dotenv import load_dotenv
import os
import pickle
from bs4 import BeautifulSoup


class UserSession(requests.Session):

    def _get_csrf_token(self, url: str, *args, **kwargs) -> str:
        """Generates a new csrf token for `url`"""
        # Create error message to display in event of failure
        error_message = f'Failed to generate csrf token for "{url}".'
        try:
            return self.get(url, *args, **kwargs).cookies['csrftoken']
        except KeyError as error:
            print(error_message)
            print("Session does not have a valid csrf token")
            print(f"Error: {error}")
        except AttributeError as error:
            print(error_message)
            print(f"Error: {error}")

    def _save_cookies(self, session, filename: str = "cookies") -> None:
        """Saves the cookies for the current session"""
        with open(filename, 'wb') as f:
            pickle.dump(session.cookies, f)

    def _load_cookies(self, filename: str = "cookies", fresh: bool = False) -> bool:
        """
        Loads any existing cookies files to the session

        Checks that there is a cookies file, and if not it will return
        `False`.

        Args:
            filename: filename where the cookies are stored
            fresh: Set to `True` to delete any existing session cookies
                and existing cookies file.
                Set to `False` to check for existing cookies files.

        Returns:
            `True` if the cookies successfully load to the session,
            or `False` if it fails to load them.
        """
        if not fresh:
            try:
                with open(filename, 'rb') as f:
                    print(f'"{filename}" file successfully loaded.')
                    # Load cookies from file
                    cookies = pickle.load(f)
                    if cookies:
                        # If cookies are found in the file
                        self.cookies = cookies
                        # Display the values for the cookies
                        self.expand_cookies(self.cookies)

                        print()  # Spacer for text
                        print("Cookies successfully added to session!")
                        return True
                    else:
                        # If no cookies are present in the file
                        print(f"No cookies were found!")
                        return False
            except FileNotFoundError:
                # If there is no existing cookies file
                print(f'"{filename}" file was not found!')
                return False
        else:
            # Remove cookies file if `fresh` is set to True
            self.clear_cookies()
            return False

    def expand_cookies(self, cookies: RequestsCookieJar) -> None:
        """Prints out cookie-related info about `cookies`"""
        try:
            # Print out info about the cookies
            print("Cookies found:")

            # List all domains for all cookies in the file
            print("\tDomains:")
            for site in cookies.list_domains():
                print(f"\t\t{site}")

            # List all paths for all cookies in the file
            print("\tPaths:")
            for path in cookies.list_paths():
                print(f"\t\t{path}")

            # List all cookie values for all cookies in the file
            print("\tCookies:")
            for cookie_name, cookie_value in cookies.items():
                print(f"\t\t{cookie_name}: {cookie_value}")

        except AttributeError:
            print("Invalid cookie object provided. Please provide a valid one.")
            print(f"Cookies provided: {cookies}")

    def clear_cookies(self, filename: str = "cookies"):
        """Deletes `filename` and clears session cookies"""
        try:
            os.remove(os.path.abspath(filename))
            print(f'"{filename}" file successfully deleted.')
        except FileNotFoundError:
            print(f'"{filename}" file does not exist.')

        self.cookies.clear()

    def get(self, *args, **kwargs):
        """Set a default timeout for all get requests."""
        return super().get(*args, **kwargs, timeout=10)

    @staticmethod
    def list_codes():
        """Prints out most HTTP codes and their corresponding keys."""
        for name, code in requests.codes.__dict__.items():
            print(f"{name}: {code}")


class InstagramSession(UserSession):

    def __init__(self):
        # Load .env file
        load_dotenv()

        # Create base url routes
        with open("urls.json", encoding="utf-8") as file:
            self.URLS = json.load(file)

        super().__init__()

        # Get your user-agent from:
        # https://www.whatismybrowser.com/detect/what-http-headers-is-my-browser-sending
        # Create the needed headers without the csrf_token
        self._insta_headers = {
            "referer": self.URLS['HOME'],
            # "user-agent": os.getenv('USER-AGENT'),
            # "user-agent": "Applebot",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0",
            "x-requested-with": 'XMLHttpRequest',
            "x-csrftoken": "",

            ### HEADERS BEING TESTED ###
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9",
            # "content-length": "322",
            # "content-type": "application/x-www-form-urlencoded",
            # "origin": "https://www.instagram.com",
            # "sec-fetch-dest": "empty",
            # "sec-fetch-mode": "cors",
            # "sec-fetch-site": "same-origin",
            # "sec-gpc": "1",
            "upgrade-insecure-requests": "1",
            # "x-asbd-id": "198387",
            # "x-instagram-ajax": "3f73a432a3a5",
            # "x-ig-www-claim": "0",
        }

        # Form data to be posted to login page. Password added in `login`.
        self._insta_payload = {
            "username": os.getenv('INSTA_USERNAME'),
            "password": "",
            "queryParams": {},
            "optIntoOneTap": "false",
        }

    def _update_csrf_token(self, token: str = None) -> None:
        """
        Binds a new csrf token to `x-csrftoken` for session headers.

        If `token` is specified, then it will bind this one. Else it
        will create a new one.

        Args:
            token: Csrf token to bind to headers.
        """
        self._insta_headers['x-csrftoken'] = token or self._get_csrf_token(self.URLS['LOGIN'])
        self.headers.update(self._insta_headers)

    def _update_payload(self) -> None:
        """
        Updates payload with a fresh timestamp.

        Binds the current timestamp to the `enc_password` key for the
        payload to be sent via `data` for the session login.
        """
        # Add fresh timestamp to password key
        self._insta_payload["enc_password"] = f"#PWD_INSTAGRAM_BROWSER:0:" \
                                              f"{datetime.datetime.now().timestamp()}:" \
                                              f"{os.getenv('INSTA_PASSWORD')}"

    def check_if_logged_in(self) -> bool:
        """
        Checks to see if the session is logged in correctly.

        Will open the account edit url and then check for redirects.
        If there are any redirects, then the account is not logged in.

        Returns:
            `True` if the session is logged in, or `False` if the
            session is not logged in.
        """
        response = self.get(self.URLS['ACCOUNT_EDIT'])
        if response.history:
            return False
        else:
            return True

    def login(self, fresh: bool = False) -> bool:
        """
        Logs in with either existing cookie or a newly made one.

        Will search for a cookie file. If it's not found, it will
        create a new one `requests.models.Response` object and attempt
        to log in. If log in is successful, it will save the new cookie.

        Args:
            fresh: Set to `True` to delete any existing cookies file,
                else it will load the existing cookies file.

        Returns:
            `True` on successful login, or `False` on failure to login.
        """
        if not self._load_cookies(fresh=fresh):
            # If cookies fail to load
            print("New cookie will be created after successful login...")
            # Makes sure that the timestamp and csrf_token are current
            self._update_csrf_token()
            self._update_payload()

            # Log in to the server
            print("Attempting to log in...")
            response = self.post(self.URLS['LOGIN_BACKEND'],
                                 # headers=self._insta_headers,
                                 data=self._insta_payload)

            # Check that login was successful
            json_data = response.json()
            try:
                authentication_status = json_data["authenticated"]
            except KeyError:
                print("Login failed.")
                for key, value in json_data.items():
                    print(f"{key}: {value}")

                print()  # Spacer for text
                return False
            else:
                if authentication_status:
                    # If login succeeds
                    print("Login successful.")
                    print("New cookie has been created and saved")
                    self._update_csrf_token(response.cookies['csrftoken'])
                    self._save_cookies(response)
                    return True
                else:
                    # If the authentication status is False
                    print("Login failed. Please check:")
                    print("\t• Headers\n\t• Payload\n\t• Username\n\t• Password")
                    return False
        else:
            # If a cookie is being used for the session
            if self.check_if_logged_in():
                print("Login successful.")
                return True
            else:
                # If the session is not logged in with the current cookies,
                # clear cookies and log in with fresh ones.
                self.login(fresh=True)


if __name__ == "__main__":
    apple = InstagramSession()
    apple.login()

    retval = apple.get("https://www.instagram.com/explore/tags/realestatephotography/")  # TODO FOR DEBUGGING
    soup = BeautifulSoup(retval.text, features="html.parser")
    # print(soup.prettify())
    with open("sample_file_1.html", "w", encoding="utf-8") as file:
        file.write(soup.prettify())

    print(soup.find("meta").get("name"))

    #  TODO Update session with bs4 to detect when account has been IP Banned due to too many logins
