import logging
from random import randint

from zipcodes import is_real

from pybot.endpoints.slack.utils import YELP_TOKEN

logger = logging.getLogger(__name__)


class LunchCommand:
    DEFAULT_LUNCH_DISTANCE = 20
    MIN_LUNCH_RANGE = 1
    AUTH_HEADER = {"Authorization": f"Bearer {YELP_TOKEN}"}

    def __init__(self, channel: str, user: str, input_text: str, user_name: str):
        self.channel_id = channel
        self.user_id = user
        self.input_text = input_text
        self.user_name = user_name

        self.lunch_api_params = self._parse_input()

    def get_yelp_request(self):
        return {
            "url": "https://api.yelp.com/v3/businesses/search",
            "params": self.lunch_api_params,
            "headers": self.AUTH_HEADER,
        }

    def select_random_lunch(self, lunch_response: dict) -> dict:
        location_count = len(lunch_response["businesses"])

        selected_location = randint(0, location_count - 1)
        location = lunch_response["businesses"][selected_location]

        logger.info(f"location selected for {self.user_name}: {location}")

        return self._build_response_text(location)

    # TODO: add test cases for various inputs
    # TODO: allow user to set defaults
    def _parse_input(self) -> dict:
        if not self.input_text:
            return {
                "location": self._random_zip(),
                "range": self._convert_to_meters(self.DEFAULT_LUNCH_DISTANCE),
                "term": "lunch",
            }

        else:
            split_items = self.input_text.split()
            zipcode = self._get_zipcode(split_items[0])
            distance = self._get_distance(split_items)
            return {"location": zipcode, "range": distance, "term": "lunch"}

    def _get_distance(self, split_items: list[str]):
        distance_index = min(len(split_items), 2) - 1

        str_distance = split_items[distance_index]
        distance = self._convert_max_distance(str_distance)

        if not self._within_lunch_range(distance):
            distance = self.DEFAULT_LUNCH_DISTANCE

        return self._convert_to_meters(distance)

    def _build_response_text(self, loc_dict: dict) -> dict:
        return {
            "user": self.user_id,
            "channel": self.channel_id,
            "text": (
                f"The Wheel of Lunch has selected {loc_dict['name']} "
                + f"at {' '.join(loc_dict['location']['display_address'])}"
            ),
        }

    @classmethod
    def _get_zipcode(cls, zipcode: str) -> int:
        try:
            if is_real(zipcode):
                return int(zipcode)
        except TypeError:
            pass

        return cls._random_zip()

    @staticmethod
    def _random_zip() -> int:
        """
        Because what doesn't matter is close food but good food
        :return: zip_code
        :rtype: str
        """
        random_zip = 0
        while not is_real(str(random_zip)):
            range_start = 10**4
            range_end = (10**5) - 1
            random_zip = randint(range_start, range_end)

        return random_zip

    def _within_lunch_range(self, input_number: int) -> bool:
        return input_number <= self.DEFAULT_LUNCH_DISTANCE

    def _convert_max_distance(self, user_param: str) -> int:
        try:
            distance = int(user_param)

            if distance < 0:
                distance = abs(distance)

            return max(distance, self.MIN_LUNCH_RANGE)

        except ValueError:
            return self.DEFAULT_LUNCH_DISTANCE

    @classmethod
    def _convert_to_meters(cls, distance):
        return int(distance * 1609.34)
