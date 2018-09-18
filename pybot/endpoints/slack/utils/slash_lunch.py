from random import randint

from zipcodes import is_valid

MAX_LUNCH_RANGE = '30'
DEFAULT_LUNCH_RANGE = '20'
MIN_LUNCH_RANGE = '1'


def random_zip():
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


def within_lunch_range(input_number):
    return int(input_number) <= int(DEFAULT_LUNCH_RANGE)


def fix_param(input: str) -> str:
    try:
        val =  str(max(int(float(input)), int(MIN_LUNCH_RANGE)))
    except ValueError:
        val = DEFAULT_LUNCH_RANGE

    return val


def two_params(first_param, second_param):
    if is_valid(first_param) and within_lunch_range(second_param):
        return {'location': first_param, 'range': second_param}
    else:
        return {'location': random_zip(), 'range': '20'}


# TODO: add test cases for various inputs
def split_params(param_text):
    if not param_text:  # no params, default random zip code, 20 miles
        return {'location': random_zip(), 'range': '20'}

    params = param_text.split()

    if len(params) == 2:
        return two_params(fix_param(params[0]), fix_param(params[1]))

    if len(params) == 1 and is_valid(fix_param(params[0])):
        return {'location': params[0], 'range': DEFAULT_LUNCH_RANGE}

    else:
        return {'location': random_zip(), 'range': DEFAULT_LUNCH_RANGE}


def get_random_lunch(lunch_response):
    number_locs = len(lunch_response['businesses'])

    selected_loc = randint(0, number_locs - 1)
    return lunch_response['businesses'][selected_loc]


def build_response_text(loc_dict):
    return f'The Wheel of Lunch has selected {loc_dict["name"]} at {" ".join(loc_dict["location"]["display_address"])}'


if __name__ == '__main__':
    assert(fix_param('0.5')=='1')
    assert(fix_param('12')=='12')
    assert(fix_param('abc')=='20')
