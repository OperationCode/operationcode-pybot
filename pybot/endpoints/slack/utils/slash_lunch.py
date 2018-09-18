from random import randint
import logging
from zipcodes import is_valid

logger = logging.getLogger(__name__)

MAX_LUNCH_RANGE = '30'
DEFAULT_LUNCH_RANGE = '20'
MIN_LUNCH_RANGE = 0.5


def get_random_lunch(lunch_response: dict, user_name: str) -> str:
    number_locs = len(lunch_response['businesses'])

    selected_loc = randint(0, number_locs - 1)
    location = lunch_response['businesses'][selected_loc]

    logger.info(f"location selected for {user_name}: {location}")

    return build_response_text(location)


def build_response_text(loc_dict: dict) -> str:
    return f'The Wheel of Lunch has selected {loc_dict["name"]} at {" ".join(loc_dict["location"]["display_address"])}'


def random_zip() -> str:
    '''
    Because what doesn't matter is close food but good food
    :return: zip_code
    :rtype: str
    '''
    random_zip = 0
    while not is_valid(str(random_zip)):
        range_start = 10 ** (4)
        range_end = (10 ** 5) - 1
        random_zip = randint(range_start, range_end)

    return str(random_zip)


def within_lunch_range(input_number: str) -> bool:
    return int(input_number) <= int(DEFAULT_LUNCH_RANGE)


def fix_param(input: str) -> str:
    try:
        float_val = float(input)

        if float_val < 1:
            float_val = abs(float_val)
        float_val = max(float_val, MIN_LUNCH_RANGE)

        val = str(float_val)

    except ValueError:
        val = DEFAULT_LUNCH_RANGE

    return val


def two_params(first_param: str, second_param: str) -> dict:
    if is_valid(first_param) and within_lunch_range(second_param):
        return {'location': first_param, 'range': second_param}
    else:
        return {'location': random_zip(), 'range': DEFAULT_LUNCH_RANGE}


# TODO: add test cases for various inputs
# TODO: allow user to set defaults
def split_params(param_text: str) -> dict:
    if not param_text:  # no params, default random zip code, 20 miles
        return {'location': random_zip(), 'range': DEFAULT_LUNCH_RANGE}

    params = param_text.split()

    if len(params) == 0:
        return {'location': random_zip(), 'range': DEFAULT_LUNCH_RANGE}

    if len(params) == 2:
        return two_params(fix_param(params[0]), fix_param(params[1]))

    if len(params) == 1 and is_valid(params[0]):
        return {'location': params[0], 'range': DEFAULT_LUNCH_RANGE}

    else:
        return two_params(fix_param(params[0]), fix_param(params[1]))


if __name__ == '__main__':
    assert (fix_param('0.5') == '0.5')
    assert (fix_param('12') == '12.0')
    assert (fix_param('12.0') == '12.0')
    assert (fix_param('abc') == '20')
    assert (fix_param('-1') == '1.0')

