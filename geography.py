from dotenv import load_dotenv
from user_input import UserInput
import requests
import os
import json


class Location:
    """Class containing specific info about an address."""

    def __init__(self, json_data):
        properties = json_data['features'][0]['properties']
        self.house_number = properties.get('housenumber')
        self.street = properties.get('street')
        self.suburb = properties.get('suburb')
        self.city = properties.get('city')
        self.county = properties.get('county')
        self.state_code = properties.get('state_code')
        # Your distance in meters from the given coordinates
        self.distance = properties.get('distance')
        self.country_code = properties.get('country_code')
        self.longitude = properties.get('lon')
        self.latitude = properties.get('lat')
        self.zip_code = properties.get('postcode')
        self.state = properties.get('state')
        self.type = properties.get('result_type')
        self.full_address = properties.get('formatted')
        self.address1 = properties.get('address_line1')
        self.address2 = properties.get('address_line2')

    def __str__(self):
        return f"{self.full_address}\n" \
               f"Latitude: {self.latitude}\n" \
               f"Longitude: {self.longitude}\n"


class Geography:
    """
    Class for obtaining information about geographical locations.

    Attributes:
        _URLS (dict): Geoapify and Countriesnow api endpoint urls.
        _geoapify (dict): Api endpoints specific to geoapify
        _countriesnow (dict): Api endpoints specific to countriesnow
        _api_key (str): Geoapify api key.
        _headers (dict): Required headers for all _geoapify api endpoints.
        _parameters (dict): Parameters to send in `GET` request.
    """

    def __init__(self):
        load_dotenv()
        with open("urls.json", encoding='utf-8') as file:
            self._URLS = json.load(file)['geolocation']
            self._geoapify = self._URLS['geoapify']
            self._countriesnow = self._URLS['countriesnow']

        self._api_key = os.getenv("GEOAPIFY_KEY")
        # Headers should not be changed
        self._headers = {
            "Accept": "application/json",
        }
        # Create url query self._parameters
        self._parameters = {
            "apiKey": self._api_key,
        }

    def geocode_search(self,
                       text: str = "",
                       name: str = "",
                       house_number: str = "",
                       street: str = "",
                       post_code: str = "",
                       city: str = "",
                       state: str = "",
                       country: str = "",
                       **kwargs
                       ) -> [Location, bool]:
        """
        Get geographical information about an address.

        Uses either a simple address search in `text` or a structured
        address search where all the other named attributes must be
        filled.

        Examples:
            geocode_search("123 address st, Maine, CA 12345")

        Args:
            text: Simple address search such as
                "123 address st, Maine, CA 12345"
            name: Name of location.
            house_number: House, Suite, or Apartment number of location.
            street: Street address of location.
            post_code: Postal code of location.
            city: City of location.
            state: State of location.
            country: Country of location. Can be the 2 letter code.
            **kwargs: Additional keyword arguments to include. Please
                refer to _geoapify documentation to get the full list.

        Returns:
            Json data containing geographical location based off the
            address given, or `False` if none is given.
        """
        # Set base url to use for all outcomes
        url = self._geoapify['base'] + self._geoapify['geocode']
        # Get the rest of the keyword args from the site.
        self._parameters.update(**kwargs)

        if text:
            # Full address is being used, such as 123 house st, madison, CA 12345
            self._parameters["text"] = text
        elif name:
            self._parameters.update({
                "name": name,
                "housenumber": house_number,
                "street": street,
                "postcode": post_code,
                "city": city,
                "state": state,
                "country": country,
            })
        else:
            # All _parameters are empty
            return False

        return self._get_location_info(url)

    def reverse_geocode_search(self,
                               latitude: str,
                               longitude: str,
                               limit: str = "1",
                               **kwargs
                               ) -> [Location, bool]:
        """
        Get information about a location by its lat & long values.

        Reverse geocode search and get either all or specific info
        about a location by its latitude and longitude.

        Examples:
            reverse_geocode_search(10.0, 10.0, type_="postcode")

        Args:
            latitude: Latitude of location to search.
            longitude: Longitude of location to search.
            limit: Maximum number of results to return.
            **kwargs:

        Returns:
            Additional keyword arguments to include. Please refer to
            _geoapify documentation for reverse geocode to get the full
            list.
        """
        url = self._geoapify['base'] + self._geoapify['reverse-geocode']
        parameters = {
            "lat": latitude,
            "lon": longitude,
            "limit": limit,
            **kwargs
        }
        self._parameters.update(parameters)
        return self._get_location_info(url)

    def ip_search(self, ip: str = "") -> [requests.models.Response, bool]:
        """
        Get the geographical information of an ip address.

        If `ip` is provided, then that ip will be searched. If not, the
        user's ip address will be used instead. Do not use this if it's
        not necessary, as it hasn't been built out fully.

        Args:
            ip: IP address to search if desired. Will search user's by
                default.

        Returns:
            `Location` containing geographical information about where
            `ip` or user's IP is located.
        """
        url = self._geoapify['base'] + self._geoapify['ip-info']
        if ip:
            self._parameters['ip'] = ip

        # Get data and check it's good
        response = requests.get(url, params=self._parameters, headers=self._headers)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return False

    def get_city_population(self, city: str) -> dict:
        """Gets the population data for a single city."""
        url = self._countriesnow['base'] + self._countriesnow['pop-in-city']
        data = {
            "city": city.title()
        }
        return self._post_for_location_info(url, data)

    def get_country_population(self, country: str) -> dict:
        """Gets the population data for a single country."""
        url = self._countriesnow['base'] + self._countriesnow['pop-in-country']
        return self._get_country_data(url, country)

    def filter_countries_population(self,
                                    year: int,
                                    limit: int = 10,
                                    less_than: int = 999999999,
                                    greater_than: int = 999999,
                                    order: str = "dsc",
                                    order_by: str = "name",
                                    ) -> dict:
        """
        Gets and filters population data for up to `limit` countries.

        The population data for up to `limit` countries during the year
        of `year` will be pulled.

        Args:
            year: Pull the cities that existed during this year, in all
                countries.
            limit: Total amount of results to display.
            less_than: Only display results that had a population less
                than this amount.
            greater_than: Only display results that had a population
                greater than this amount.
            order: Ascending `asc` or Descending `dsc`.
            order_by: Decides the order to display the results in.

        Returns:
            Population data for up to `limit` countries during the year
            of `year, filtered based off of the other parameters.
        """
        url = self._countriesnow['base'] + self._countriesnow['pop-in-countries-filter']
        data = {
            "year": year,
            "limit": limit,
            "lt": less_than,
            "gt": greater_than,
            "orderBy": order_by,
            "order": order
        }
        return self._post_for_location_info(url, data)

    def filter_cities_population(self,
                                 country: str,
                                 limit: int = 10,
                                 order: str = "dsc",
                                 order_by: str = "name"
                                 ) -> dict:
        """
        Gets and filters the population data for multiple cities.

        All cities in `country` will be collected and filtered.

        Args:
            country: Country to get the cities from.
            limit: Total amount of results to display.
            order: Ascending `asc` or Descending `dsc`.
            order_by: Decides the order to display the results in.

        Returns:
            Population data for up to `limit` cities.
        """
        url = self._countriesnow['base'] + self._countriesnow['pop-in-cities-filter']
        data = {
            "limit": limit,
            "order": order,
            "orderBy": order_by,
            "country": country,
        }
        return self._post_for_location_info(url, data)

    def get_cities_in_state(self, country: str, state: str) -> dict:
        """Gets all cities in `state`. Must provide `country` as well."""
        url = self._countriesnow['base'] + self._countriesnow['cities-in-state']
        return self._get_state_data(url, country, state)

    def get_cities_in_country(self, country: str) -> dict:
        """Gets all cities in `country`."""
        url = self._countriesnow['base'] + self._countriesnow['cities-in-country']
        return self._get_country_data(url, country)

    def get_states_in_country(self, country: str) -> dict:
        """Gets all states in `country`."""
        url = self._countriesnow['base'] + self._countriesnow['states-in-country']
        return self._get_country_data(url, country)

    def get_dial_codes_in_country(self, country: str) -> dict:
        """Gets all dial codes in `country`."""
        url = self._countriesnow['base'] + self._countriesnow['states-in-country']
        return self._get_country_data(url, country)

    def _get_country_data(self, url, country) -> dict:
        """Gets information for `country` from `url`."""
        data = {
            "country": country.title()
        }
        return self._post_for_location_info(url, data)

    def _get_state_data(self, url, country, state) -> dict:
        """Gets information for `state` from `url`."""
        data = {
            "country": country.title(),
            "state": state.title(),
        }
        return self._post_for_location_info(url, data)

    def _post_for_location_info(self, url, data) -> dict:
        """Gets countriesnow location info for `url` endpoint."""
        response = requests.post(url, data=data)
        new_data = response.json()

        if new_data['error']:
            print(new_data['msg'])
            return {}
        else:
            return new_data['data']

    def _get_location_info(self, url) -> [Location, bool]:
        """Gets geoapify location info for `url` endpoint."""
        # Get data and check it's good
        response = requests.get(url, params=self._parameters, headers=self._headers)

        if response.status_code == 200:
            data = response.json()
            location = Location(data)
            return location
        else:
            print("Failed to find the given location.")
            print(f"Error: {response.json()['message']}")
            return False

    def get_united_states(self) -> list:
        """Returns all States and their codes as `tuple`s in a `list`."""
        united_states = []
        for state in self.get_states_in_country("United States")['states']:
            united_states.append((state['name'], state['state_code']))

        return united_states

    def user_defined_data(self) -> [list, dict]:
        """
        Prints out methods as options for user, and runs selected one.

        User chooses which method they want, inputs the required
        parameters, then receives the data from the method.

        This method is deprecated.

        Returns:
            Information about the requested city, state, or country
            using the selected method.
        """
        options = {
            "City population": (["city"], self.get_city_population),
            "Cites in a country": (["country"], self.get_cities_in_country),
            "Country population": (["country"], self.get_country_population),
            "States in a country": (["country"], self.get_states_in_country),
            "Cites in a state": (["country", "state"], self.get_cities_in_state),
            "Dial codes in a country": (["country"], self.get_dial_codes_in_country),
            "All states in United States": ([], self.get_united_states),
        }
        user_choice = UserInput.create_menu(options, exit_=True)
        if user_choice == "exit":
            return None

        selected_function = options[user_choice]

        # Cycle through all parameters and get user input for them
        parameters = {}
        for parameter in selected_function[0]:
            parameters[parameter] = (input(f"Please input a {parameter}: "))
            
        return selected_function[1](**parameters)


if __name__ == "__main__":
    test = Geography()
    print(test.get_cities_in_state("United States", "California"))

