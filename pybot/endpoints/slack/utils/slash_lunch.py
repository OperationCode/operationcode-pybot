from typing import List
import logging
from random import randint
from zipcodes import is_valid

logger = logging.getLogger(__name__)


class LunchCommand:
    DEFAULT_LUNCH_DISTANCE = 20
    MIN_LUNCH_RANGE = 0.5

    def __init__(self, channel: str, user: str, slack: str, input_text: str, user_name: str):

        self.channel_id = channel
        self.user_id = user
        self.slack = slack
        self.input_text = input_text
        self.user_name = user_name

        self.lunch_api_params = self._parse_input()

    def get_lunch_api_params(self):
        return self.lunch_api_params

    def select_random_lunch(self, lunch_response: dict) -> dict:
        location_count = len(lunch_response['businesses'])

        selected_location = randint(0, location_count - 1)
        location = lunch_response['businesses'][selected_location]

        logger.info(f"location selected for {self.user_name}: {location}")

        return self._build_response_text(location)

    # TODO: add test cases for various inputs
    # TODO: allow user to set defaults
    def _parse_input(self) -> dict:
        if not self.input_text:
            return {'location': self._random_zip(), 'range': self.DEFAULT_LUNCH_DISTANCE}

        else:
            split_items: List[str]
            split_items = self.input_text.split()
            zipcode = self._get_zipcode(split_items[0])
            distance = self._get_distance(split_items)
            return {'location': zipcode, 'range': distance}

    def _get_distance(self, split_items: List[str]):
        distance: int

        distance_index = min(len(split_items), 2) - 1

        str_distance = split_items[distance_index]

        distance = self._convert_max_distance(str_distance)

        if self._within_lunch_range(distance):
            return distance
        else:
            return self.DEFAULT_LUNCH_DISTANCE

    def _build_response_text(self, loc_dict: dict) -> dict:
        return {'user': self.user_id, 'channel': self.channel_id,
                'text': (f'The Wheel of Lunch has selected {loc_dict["name"]} ' +
                         f'at {" ".join(loc_dict["location"]["display_address"])}')}

    def _get_zipcode(self, zipcode_val: str) -> int:
        try:

            if is_valid(zipcode_val):
                return int(zipcode_val)
        except TypeError:
            pass

        finally:

            return LunchCommand._random_zip()

    @staticmethod
    def _random_zip() -> int:
        """
        Because what doesn't matter is close food but good food
        :return: zip_code
        :rtype: str
        """
        random_zip = 0
        while not is_valid(str(random_zip)):
            range_start = 10 ** 4
            range_end = (10 ** 5) - 1
            random_zip = randint(range_start, range_end)

        return random_zip

    def _within_lunch_range(self, input_number: int) -> bool:
        return input_number <= self.DEFAULT_LUNCH_DISTANCE

    def _convert_max_distance(self, user_param: str) -> int:

        try:
            float_val = float(user_param)

            if float_val < 0:
                float_val = abs(float_val)

            return max(float_val, self.MIN_LUNCH_RANGE)

        except ValueError:
            return self.DEFAULT_LUNCH_DISTANCE


if __name__ == '__main__':
    channel_id = 'AAAAAAAA'
    user_id = 'BBBBBBB'
    slack = 'CCCCCCCC'
    user_name = 'DDDDDDDD'

    single_valid = '80020'
    single_invalid = '12'
    double_valid = '27051 12'
    double_invalid_zip = '12 12'
    double_invalid_distance = '27545 100000'
    double_invalid_both = '20 1000000'
    double_invalid_both_again = 'abc abc'
    double_invalid_both_again_again = 'abc 01210'
    float_valid = '80020 0.5'
    float_invalid = '80020 0.3'
    lunch = LunchCommand(channel_id, user_id, slack, float_valid, user_name)
