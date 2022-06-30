import csv

import requests
import os
from dotenv import load_dotenv
import json
from bs4 import BeautifulSoup


class UserAgents:

    def __init__(self):
        load_dotenv()
        self._API_KEY = os.getenv('USER_AGENT_API_KEY')
        with open("urls.json", encoding='utf-8') as file:
            self._URLS = json.load(file)["user-agent"]

        self._headers = {
            "X-API-KEY": self._API_KEY
        }

        self._params = {}
        self.filename = "user_agents"

        if not os.path.isdir(self.filename):
            self.get_query_options_data()

    def _get_user_agents(self, *args, **kwargs):
        """Returns specified user-agents from whatismybrowser database."""
        return requests.get(self._URLS["base"] + self._URLS["data-search"],
                            headers=self._headers,
                            params=self._params,
                            *args,
                            **kwargs)

    def get_chrome_windows_users(self):
        """Returns chrome/windows user-agents."""
        self._params.update(
            {
                "software_name": "Chrome",
                "operating_system_name": "Windows",
                "software_type": "Web Browser",
                "hardware_type": "Computer",
                "limit": "3",

            }
        )
        return self._get_user_agents()

    def _get_query_options_data(self, category_name: str, link: str) -> None:
        """
        Pulls and stores all query-type information from `link`.

        Will pull all info and related agents in `link`,
        and store it using `category_name` in the filename.

        Args:
            category_name: Filename to specify the category for the
                info being pulled.
            link: https://developers.whatismybrowser.com/useragents/explore/ url
                to pull info from.
        """
        # Retrieve info and convert to soup
        response = requests.get(link, timeout=10)
        soup = BeautifulSoup(response.text, features='lxml')

        # Find all entries using css selectors
        table = soup.select("table tbody tr")

        # Cycle through all entries and append to csv file
        with open(f"{self.filename}/{self.filename}_{category_name}_query_params.csv",
                  "w",
                  encoding='utf-8',
                  newline='') as csv_file:
            csv_file.write(f"{category_name}|Related User Agents\n")
            # Cycle through names and their related user agents
            for tag in table:
                name, user_agents = tag.stripped_strings
                csv_file.write(f"{name}|{user_agents}\n")

    def get_query_options_data(self, selection: str = "") -> None:
        """
        Pulls all whatismybrowser query-type info, or a specific one.

        By default, all info will be pulled and saved into csv files. If
        `selection` is specified, then only that one set of data will be
        pulled.

        Args:
            selection: Set of data to pull. Do not specify if you want
                to pull all data.
        """
        # Create directory if it doesn't already exist
        try:
            os.mkdir(os.path.abspath(self.filename))
        except FileExistsError:
            pass

        # If only one type is being requested to be pulled
        if selection:
            try:
                link = self._URLS["query-types"][selection]
            except KeyError:
                print("Invalid category name selection for query-type urls.")
                print(f"Selected type: {selection}")
            else:
                # Retrieve the requested type
                print(f"Attempting to retrieve info for: {selection}")
                self._get_query_options_data(selection, link)
                filepath = os.path.realpath(f"{self.filename}/{self.filename}_{selection}_query_params.csv")
                print(f"File successfully created in:\n{filepath}")
        else:
            # Cycle through each link
            for category_name, link in self._URLS["query-types"].items():
                print(f"Attempting to retrieve info for: {category_name}")
                self._get_query_options_data(category_name, link)
                filepath = os.path.realpath(f"{self.filename}/{self.filename}_{category_name}_query_params.csv")
                print(f"File successfully created in:\n{filepath}")

        print("All files have been created successfully")

    def list_query_options(self, category: int = -1) -> None:
        """
        Lists valid query parameters for whatismybrowser database.

        `category` is used for recursion and should be left blank at all
        times.

        Prints out a menu of available search query categories to list.
        If one is not available, it will be retrieved.

        Args:
            category: Used for recursion. When a selected option is not
                found, the file will be created and this method will be
                run again with `category` being the user choice.
        """
        # Create a choice menu of the different query types
        urls = {index: category_name for index, category_name in enumerate(self._URLS["query-types"])}

        if category >= 0:
            # Method was run via recursion, so no input is required
            choice = category
        else:
            # Print out choice menu
            for index, category_name in urls.items():
                print(f"{index + 1}. {category_name}")

            # Get user choice
            choice = int(input("Please input the number of the type you'd like to list: ")) - 1

        # Check that the choice is valid
        try:
            filepath = f"{self.filename}/{self.filename}_{urls[choice]}_query_params.csv"
        except KeyError:
            print("Invalid number selection")
        else:
            try:
                # Open file selected and list all lines in it
                with open(filepath, encoding='utf-8') as file:
                    print()  # Spacer for text
                    print("Retrieving info:")
                    # Display category and format
                    print("*" * 20, urls[choice], "*" * 20)
                    print("Format: Valid Param | Related User-Agents")
                    # Skip Headers
                    file.readline()
                    for line in file:
                        # Strip the '\n' off each line, so it prints correctly.
                        name, user_agents = line.rstrip('\n').split('|')
                        print(f"{name}: {user_agents}")

            except FileNotFoundError:
                # If file is not found, pull only that file
                print("File not found. Creating required files...")
                self.get_query_options_data(selection=urls[choice])
                self.list_query_options(category=choice)


class Proxies:

    def __init__(self):
        self.filename = "proxies.csv"
        with open("urls.json", encoding='utf-8') as file:
            self._URLS = json.load(file)["proxies"]

        self.proxies = self.get_proxies()

    def _generate_simple_proxies_file(self, proxy_list: list) -> None:
        """Saves a csv file of only proxies/ports"""
        with open(f"simple_{self.filename}", "w", encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            # Will create a single row of all proxies/ports combinations
            writer.writerow(proxy_list)

    def _generate_proxies_file(self, proxy_list: list) -> None:
        """Saves a csv file of the most recent proxies and their info."""
        with open(self.filename, "w", encoding='utf-8', newline='') as file:
            # Create field names for csv file
            field_names = ["IP Address", "Port", "Code",
                           "Country", "Anonymity", "Google",
                           "Https", "Last Checked"]
            writer = csv.writer(file)
            # Create headers in file
            writer.writerow(field_names)
            for proxy in proxy_list:
                # Get list of info about each proxy and write it to csv
                writer.writerow(proxy.get_details())

    def get_proxies(self, simple: bool = False, save: bool = False) -> list:
        """
        Creates a list of new proxies to use.

        Will generate the newest list from https://free-proxy-list.net/
        and will return a `list` object.

        Is capable of saving the proxies generated into a file if `save`
        is set to `True`.

        Args:
            simple: `bool` that determines if only proxies and their
                ports are used, or if more detailed info is
                used per proxy.
            save: `bool` that determines whether to save the proxies
                into a file.

        Returns:
            If `simple` is set to `True`, returns a `list` of `Proxy`
            objects with only the `ip` and `port` attributes.
            If `simple` is set to `False`, returns a `list` of `Proxy`
            objects with all attributes filled in.
        """
        response = requests.get(self._URLS["base"])
        soup = BeautifulSoup(response.text, features="lxml")
        # If only proxies and their ports are being used
        if simple:
            # Parse list of proxies/ports
            proxies_raw = soup.select_one("textarea.form-control").string.split("\n")[3:-1]
            proxies = []
            for proxy in proxies_raw:
                ip, port = proxy.split(':')
                proxies.append(Proxy(ip=ip, port=port))
            # Save proxies into a file if it's enabled
            if save:
                self._generate_simple_proxies_file(proxies_raw)
        else:
            # If more detailed info is desired about each proxy
            proxies = []
            table = soup.select("#list tbody tr")
            # Create list of proxies
            for (ip, port, code, country, anonymity, google, https, last_checked) in table:
                proxy = Proxy(
                    ip=ip.string,
                    port=port.string,
                    code=code.string,
                    country=country.string,
                    anonymity=anonymity.string,
                    google=google.string,
                    https=https.string,
                    last_checked=last_checked.string
                )
                # Add to country and code dicts so that proxies can be
                # looked up by either their country or country code.
                proxies.append(proxy)

            # Save proxies into a file if it's enabled
            if save:
                self._generate_proxies_file(proxies)

        return proxies

    @staticmethod
    def group_by(proxy_list: list, attribute: str):
        """
        Returns a proxies `list` sorted by `attribute`

        Proxy lists are sorted by `last_checked` attribute by default.

        Args:
            proxy_list: `list` of `Proxy` objects
            attribute: Valid `Proxy` attribute

        Returns:
            `list` sorted by `attribute` if it's a valid `Proxy`
            attribute.
        """

        def sort_key(proxy):
            # For sorting the list
            return proxy.__getattribute__(attribute)

        return sorted(proxy_list, key=sort_key)

    # def get_random_proxy(self, country: str = "") -> str:


class Proxy:

    def __init__(self,
                 ip: str,
                 port: str,
                 code: str = "",
                 country: str = "",
                 anonymity: str = "",
                 google: str = "",
                 https: str = "",
                 last_checked: str = "",
                 ):
        self.ip = ip
        self.port = port
        self.proxy = f"{self.ip}:{self.port}"
        self.code = code
        self.country = country
        self.anonymity = anonymity
        self.google = google
        self.https = https
        self.last_checked = last_checked

    def __str__(self):
        """View all attributes of the proxy object"""
        return f"{self.proxy}\n" \
               f"Proxy: {self.ip}\n" \
               f"Port: {self.port}\n" \
               f"Country Code: {self.code}\n" \
               f"Country: {self.country}\n" \
               f"Anonymity: {self.anonymity}\n" \
               f"Google: {self.google}\n" \
               f"Https: {self.https}\n" \
               f"Last Checked: {self.last_checked}"

    def get_details(self):
        """Get all attributes of the proxy object"""
        return [
            self.ip,
            self.port,
            self.code,
            self.country,
            self.anonymity,
            self.google,
            self.https,
            self.last_checked,
        ]

    def sorter(self, sort_attr):
        return self.__getattribute__(sort_attr)


if __name__ == "__main__":
    a = Proxies()
    # print(a.get_proxies(save=True))
    proxies = a.get_proxies()
    new_proxies = Proxies.group_by(proxies, "anonymity")
    for item in new_proxies:
        print(item.get_details())
        print()
