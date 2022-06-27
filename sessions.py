import requests
import datetime
import json
from dotenv import load_dotenv
import os
import pickle


class UserSession(requests.Session):

    def _get_csrf_token(self, url: str) -> str:
        """Generates a new csrf token for `url`"""
        return self.get(url).cookies['csrftoken']

    def _save_cookies(self, filename: str = "cookies") -> None:
        """Saves the cookies for the current session"""
        with open(filename, 'wb') as f:
            pickle.dump(self.cookies._cookies, f)

    def _load_cookies(self, filename: str = "cookies", fresh: bool = False) -> bool:
        """
        Loads any existing cookie files to the session

        Checks that there is a cookie file, and if not it will create
        one as well as a new cookie.

        Args:
            filename: filename where the cookies are stored
            fresh: Set to `True` to delete any existing cookies file,
                else it will load the existing cookies file.

        Returns:
            `True` if the cookies successfully load  to the session,
            or `False` if it fails to load them.
        """
        # Check if there's an existing cookies file
        if os.path.exists(os.path.abspath(filename)):
            if not fresh:
                with open(filename, 'rb') as f:
                    print(f'File: "{filename}" successfully loaded.')
                    # Load cookie from file
                    cookie = pickle.load(f)
                    if cookie:
                        # Check if any cookies are expired
                        if self._check_expirations(cookies=cookie, display=True):
                            print()  # Spacer for text
                            print("Failed to add cookie to session!")
                            return False

                        # Create a valid cookie object from the cookies
                        jar = requests.cookies.RequestsCookieJar()
                        jar._cookies = cookie
                        self.cookies = jar

                        # If no cookies are expired
                        print()  # Spacer for text
                        print("Cookie successfully added to session!")
                        return True
                    else:
                        # If no cookie file is found
                        print(f"No cookies were found!")
                        return False
            else:
                # Remove cookies file if `fresh` is set to True
                self.clear_cookies()
                return False
        else:
            # If no files are found
            print(f"{filename} was not found!")
            return False

    def _check_expirations(self, cookies: dict, display: bool = False) -> bool:
        """
        Return `True` if any cookies in `cookies` are expired.

        Iterates through every cookie in `cookies` and checks their
        expiration timestamps against a current one.

        Args:
            cookies: `dict` containing all cookies to be checked. Can
                often be found in `session.cookies._cookies`.
            display: Set to `True` to display information about each
                cookie found.

        Returns: `False` if all cookies are current and not expired.
            Else returns `True` if any cookies are expired.

        """
        try:
            # Test to see if any cookies exist
            cookies = cookies.items()
        except AttributeError:
            print("This session does not currently have any cookies. "
                  "Try loading or creating one first.")
        else:
            # Get current timestamp
            time_now = datetime.datetime.now().timestamp()
            expired_cookies = []
            print("Cookies found:")
            # Iterate through cookies until it gets to expiration
            for site, site_value in cookies:
                if display:
                    print(f"Website: {site}")
                for path, path_value in site_value.items():
                    if display:
                        print(f"\tPath: {path}")
                    for cookie, cookie_value in path_value.items():
                        if display:
                            print(f"\t\t{cookie}: {cookie_value}")

                        # Save all expired cookies
                        cookie_expiration = cookie_value.expires
                        try:
                            if time_now >= cookie_expiration:
                                expired_cookies.append((cookie, cookie_value))
                        except TypeError:
                            pass

            if expired_cookies:
                # If any cookies from above are expired
                print("The following cookies are expired:")
                for cookie, cookie_value in expired_cookies:
                    print(f"{cookie}: {cookie_value}")

                return True

            # If there are no expired cookies
            return False

    def clear_cookies(self, filename: str = "cookies"):
        """Deletes `filename` cookies file."""
        os.remove(os.path.abspath(filename))


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
        self.insta_headers = {
            "referer": self.URLS['HOME'],
            "user-agent": os.getenv('USER-AGENT'),
            "x-requested-with": 'XMLHttpRequest',
            "x-csrftoken": "",
        }

        # Form data to be posted to login page. Password added in `login`.
        self.insta_payload = {
            "username": os.getenv('INSTA_USERNAME'),
            "password": "",
            "queryParams": {},
            "optIntoOneTap": "false",
        }

    def _update_csrf_token(self) -> None:
        """Binds a new csrf token to `x-csrftoken` for session headers."""
        # Add fresh csrf token to headers
        self.insta_headers['x-csrftoken'] = self._get_csrf_token(self.URLS['HOME'])

    def _update_payload(self) -> None:
        """
        Updates payload with a fresh timestamp.

        Binds the current timestamp to the `enc_password` key for the
        payload to be sent via `data` for the session login.
        """
        # Add fresh timestamp to password key
        self.insta_payload["enc_password"] = f"#PWD_INSTAGRAM_BROWSER:0:" \
                                             f"{datetime.datetime.now().timestamp()}:" \
                                             f"{os.getenv('INSTA_PASSWORD')}"

    def login(self, fresh: bool = False) -> bool:
        """
        Logs in with either existing cookie or a newly made one.

        Will search for a cookie file. If it's not found, it will
        create a new one. The new one will be saved upon successful
        login.

        Args:
            fresh: Set to `True` to delete any existing cookies file,
                else it will load the existing cookies file.

        Returns:
            `True` on successful login, or `False` on failure to login.
        """
        if not self._load_cookies(fresh=fresh):
            print("New cookie will be created after successful login...")
            # Makes sure that the timestamp and csrf_token are current
            self._update_csrf_token()
            self._update_payload()

            # Log in to the server
            response = self.post(self.URLS['LOGIN'],
                                 headers=self.insta_headers,
                                 data=self.insta_payload)
            if response.status_code == 200:
                # If login succeeds
                print("New cookie has been created and saved")
                self._save_cookies()
                print("Login successful")
                return True
            else:
                print("Login failed. Please check:")
                print("Headers\nPayload\nUsername\nPassword")
                return False
        else:
            return True


if __name__ == "__main__":
    apple = InstagramSession()
    apple.login()

