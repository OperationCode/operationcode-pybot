from random import randint

from aiohttp.web_response import Response
from zipcodes import is_valid


def random_zip():
    random_zip = 0
    while not is_valid(str(random_zip)):
        range_start = 10 ** (4)
        range_end = (10 ** 5) - 1
        random_zip = randint(range_start, range_end)

    return str(random_zip)


def within_lunch_range(input_number):
    return int(input_number) <= 30


def two_params(first_param, second_param):
    if is_valid(first_param) and within_lunch_range(second_param):
        return {'location': first_param, 'range': second_param}
    else:
        return {'location': random_zip(), 'range': '20'}


def split_params(param_text):
    if not param_text:  # no params, default random zip code, 20 miles
        return {'location': random_zip(), 'range': '20'}

    params = param_text.split()

    if len(params) == 2:  # two values
        return two_params(params[0], params[1])

    if len(params) == 1 and is_valid(params[0]):  # one value
        return {'location': params[0], 'range': '20'}

    else:
        return {'location': random_zip(), 'range': '20'}


def get_random_lunch(lunch_response):
    number_locs = len(lunch_response['businesses'])

    selected_loc = randint(0, number_locs - 1)
    return lunch_response['businesses'][selected_loc]


def build_response_text(loc_dict):
    return Response(
        text=f'The Wheel of Lunch has selected {loc_dict["name"]} at {" ".join(loc_dict["location"]["display_address"])}')
