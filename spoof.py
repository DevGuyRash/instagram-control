import requests
import os
from dotenv import load_dotenv
import json
from bs4 import BeautifulSoup


class UserAgents:

    def __init__(self):
        load_dotenv()
        self.API_KEY = os.getenv('USER_AGENT_API_KEY')
        with open("urls.json", encoding='utf-8') as file:
            self.URLS = json.load(file)["user-agent"]

        self.headers = {
            "X-API-KEY": self.API_KEY
        }

        self.params = {}
        self.filename = "user_agents"

    def pull_users(self, *args, **kwargs):
        return requests.get(self.URLS["base"] + self.URLS["data-search"],
                            headers=self.headers,
                            params=self.params,
                            *args,
                            **kwargs)

    def _pull_search_info(self, category_name: str, link: str) -> None:
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
        with open(f"{self.filename}/{self.filename}_{category_name}.csv",
                  "w",
                  encoding='utf-8',
                  newline='') as csv_file:
            csv_file.write(f"{category_name}|Related User Agents\n")
            # Cycle through names and their related user agents
            for tag in table:
                name, user_agents = tag.stripped_strings
                csv_file.write(f"{name}|{user_agents}\n")

    def pull_search_types(self, selection: str = "") -> None:
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
                link = self.URLS["query-types"][selection]
            except KeyError:
                print("Invalid category name selection for query-type urls.")
                print(f"Selected type: {selection}")
            else:
                # Retrieve the requested type
                print(f"Attempting to retrieve info for: {selection}")
                self._pull_search_info(selection, link)
                filepath = os.path.realpath(f"{self.filename}/{self.filename}_{selection}.csv")
                print(f"File successfully created in:\n{filepath}")
        else:
            # Cycle through each link
            for category_name, link in self.URLS["query-types"].items():
                print(f"Attempting to retrieve info for: {category_name}")
                self._pull_search_info(category_name, link)
                filepath = os.path.realpath(f"{self.filename}/{self.filename}_{category_name}.csv")
                print(f"File successfully created in:\n{filepath}")

        print("All files have been created successfully")

    def list_search_types(self, category: int = -1) -> None:
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
        urls = {index: category_name for index, category_name in enumerate(self.URLS["query-types"])}

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
            filepath = f"{self.filename}/{self.filename}_{urls[choice]}.csv"
        except KeyError:
            print("Invalid number selection")
        else:
            try:
                # Open file selected and list all lines in it
                with open(filepath, encoding='utf-8') as file:
                    print()  # Spacer for text
                    print("Retrieving info:")
                    # Skip the headers
                    file.readline()
                    for line in file:
                        # Strip the '\n' off each line, so it prints correctly.
                        name, user_agents = line.rstrip('\n').split('|')
                        print(f"{name}: {user_agents}")

            except FileNotFoundError:
                # If file is not found, pull only that file
                print("File not found. Creating required files...")
                self.pull_search_types(selection=urls[choice])
                self.list_search_types(category=choice)


if __name__ == "__main__":
    test = UserAgents()

    # test.pull_search_types()
    test.list_search_types()

