import requests
import os
import json
from dotenv import load_dotenv


class Location:
    """Class containing specific info about an address."""

    def __init__(self, json_data):
        properties = json_data['features'][0]['properties']
        self.house_number = properties['housenumber']
        self.street = properties['street']
        self.suburb = properties.get('suburb')
        self.city = properties['city']
        self.county = properties['county']
        self.state_code = properties['state_code']
        # Your distance in meters from the given coordinates
        self.distance = properties['distance']
        self.country_code = properties['country_code']
        self.longitude = properties['lon']
        self.latitude = properties['lat']
        self.zip_code = properties['postcode']
        self.state = properties['state']
        self.type = properties['result_type']
        self.full_address = properties['formatted']
        self.address1 = properties['address_line1']
        self.address2 = properties['address_line2']

    def __str__(self):
        return f"{self.full_address}\n" \
               f"Latitude: {self.latitude}\n" \
               f"Longitude: {self.longitude}\n"


class Geography:
    """
    Class for obtaining information about geographical locations.

    Attributes:
        URLS (dict): Geoapify api endpoint urls.
        api_key (str): Geoapify api key.
        headers (dict): Required headers for all geoapify api endpoints.
        parameters (dict): Parameters to send in `GET` request.
    """

    def __init__(self):
        load_dotenv()
        with open("urls.json", encoding='utf-8') as file:
            self.URLS = json.load(file)['geoapify']

        self.api_key = os.getenv("GEOAPIFY_KEY")
        # Headers should not be changed
        self.headers = {
            "Accept": "application/json",
        }
        # Create url query self.parameters
        self.parameters = {
            "apiKey": self.api_key,
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
                refer to geoapify documentation to get the full list.

        Returns:
            Json data containing geographical location based off the
            address given, or `False` if none is given.
        """
        # Set base url to use for all outcomes
        url = self.URLS['base'] + self.URLS['geocode']
        # Get the rest of the keyword args from the site.
        self.parameters.update(**kwargs)

        if text:
            # Full address is being used, such as 123 house st, madison, CA 12345
            self.parameters["text"] = text
        elif name:
            self.parameters.update({
                "name": name,
                "housenumber": house_number,
                "street": street,
                "postcode": post_code,
                "city": city,
                "state": state,
                "country": country,
            })
        else:
            # All parameters are empty
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
            geoapify documentation for reverse geocode to get the full
            list.
        """
        url = self.URLS['base'] + self.URLS['reverse-geocode']
        parameters = {
            "lat": latitude,
            "lon": longitude,
            "limit": limit,
            **kwargs
        }
        self.parameters.update(parameters)
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
        url = self.URLS['base'] + self.URLS['ip-info']
        if ip:
            self.parameters['ip'] = ip

        # Get data and check it's good
        response = requests.get(url, params=self.parameters, headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return False

    def _get_location_info(self, url) -> [Location, bool]:
        """Gets location info for `url`."""
        # Get data and check it's good
        response = requests.get(url, params=self.parameters, headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            location = Location(data)
            return location
        else:
            return False


if __name__ == "__main__":
    pass
