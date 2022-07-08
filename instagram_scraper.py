from sessions import InstagramSession
from instagram_data import User, Post
from spoof import Proxies
from bs4 import BeautifulSoup
import requests
import json
import os
import re


class InstagramBot:

    def __init__(self):
        with open("urls.json", encoding='utf-8') as f:
            self.URLS = json.load(f)["instagram"]

        self.session = InstagramSession()
        self.proxies = Proxies()
        self.session.login()
        self.users = []
        self.posts = []

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
        """Get user input, that must be an option in `valid_options`."""
        user_input = input()
        if user_input not in valid_options:
            print("Invalid selection! Please try again: ", end='')
            return self.get_input(valid_options)

        return user_input

    def create_users(self, *args, **kwargs) -> None:
        """
        Searches up usernames given by the user, on Instagram.

        Will retrieve the json data per user given, and create a `User`
        object for each. All users will be appended to `users`
        attribute in a list.

        Args:
            *args: Any additional arguments to apply to the session GET.
            **kwargs: Any additional arguments to apply to the session
                GET.
        """
        # List of usernames to research
        usernames = []
        # List where User objects will be stored, and return value
        list_of_users = []
        print("Please input usernames to pull.")
        print("Type 'e' when you are finished entering usernames.")
        while True:
            # Get user input
            username = "".join(input(">").casefold().split())

            # Break out of loop if user wants to
            if username == "e":
                break

            usernames.append(username)

        # Pull each username in the above list
        for user in usernames:
            params = {
                "username": user,
            }

            # Get username info
            response = self.get(self.URLS["user-profile"], params=params, *args, **kwargs)
            # If the user is found
            if response.status_code == 200:
                data = response.json()

                # Create User
                new_user = User(username=user, json_data=data)
                list_of_users.append(new_user)

                print(f"'{user} has been found!")
            else:
                # If the username does not exist
                print(f"Username '{user}` not found!")

        print("Account search complete.")

        self.users = list_of_users

    def get_user_posts(self, *args, **kwargs):
        """Retrieves the data for the posts the user provides."""
        print(f"Input instagram post url codes, or full URLs "
              f"(format: {self.URLS['user-post']}[URL_CODE]/)")
        print("When you're finished inputting Posts to get, type 'e'")
        posts_to_get = []
        posts = []
        while True:
            # Create list of posts to inspect from userinput
            user_post = "".join(input(">").split())
            # If user is finished adding posts
            if user_post == "e":
                break

            posts_to_get.append(user_post)

        for user_post in posts_to_get:
            # Only take the last part of the url, the actual post code.
            url_code = re.search('/*([a-zA-Z0-9-_]+)/*$', user_post)
            if url_code:
                url_code = url_code.group(1)
                posts.append(Post(self.get_post_data(url_code, *args, **kwargs)))

        self.posts = posts

    def get_post_data(self, url_code: str, *args, **kwargs) -> dict:
        """
        Gets the `json` data from an instagram post.

        Will accept any instagram post url code, which is normally
        random letters and numbers:
            https://www.instagram.com/p/[URL_CODE]/

        Args:
            url_code: Unique shortcode for the instagram post, usually
                located near the end of the URL.
            *args: Any additional arguments to apply to the session GET.
            **kwargs: Any additional arguments to apply to the session
                GET.

        Returns:
            `dict` containing all information about the instagram post.
        """
        # Get the html of the post page to ge the media_id
        response = self.get(f"{self.URLS['user-post']}{url_code}", *args, **kwargs)
        # Get media id from html
        media_id = self.extract_id_from_post(response.text)

        # Return info about the post
        return self.get(f"{self.URLS['user-post-api']}"
                        f"{media_id}/"
                        f"{self.URLS['user-post-api-end']}",
                        *args,
                        **kwargs).json()

    @staticmethod
    def extract_id_from_post(post_html: str) -> str:
        """
        Extracts the `media_id` from the html of an instagram post.

        Format of the instagram post url to extract the html from should
        be:
        https://www.instagram.com/p/[POST_CODE]

        Each post will have a shorthand code at the end.

        Args:
            post_html: Html code of the post page itself.

        Returns:
            `media_id` if found, else an empty string.
        """
        soup = BeautifulSoup(post_html, features='lxml')
        media_id = ""
        # The media_id will temporarily load under a script. Find it using
        # regular expressions
        for single_string in [script_strings for script in soup.find_all("script")
                              for script_strings in script.stripped_strings]:
            media_id = re.search('media_id":"(\d+)"', single_string)
            # If the regular expression finds a match
            if media_id:
                # Set media_id to only the numbers in the match
                media_id = media_id.group(1)
                break

        return media_id


if __name__ == "__main__":
    drive = InstagramBot()
    # drive.create_users()
    # for users in drive.users:
    #     print(users.is_private)
    #     print(type(users.id))
    #     print()

    drive.get_user_posts()
    for post in drive.posts:
        print(post)
        print(post.comments)
