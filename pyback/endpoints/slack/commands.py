import logging

from aiohttp.web_response import Response
from slack import methods

from pyback.endpoints.slack.utils.command_utils import get_slash_here_message, can_here
from pyback.endpoints.slack.utils.slash_lunch import split_params, get_random_lunch, build_response_text

logger = logging.getLogger(__name__)


def create_endpoints(plugin):
    plugin.on_command('/here', slash_here)
    plugin.on_command('/lunch', slash_lunch)


async def slash_here(command, app):
    channel = command['channel_id']
    slack = app["plugins"]["slack"].api

    authorized = await can_here(channel, command['user_id'], app["plugins"]["pg"])
    if not authorized:
        return Response(text="You are not authorized to use that command in this channel")

    message = await get_slash_here_message(channel, slack, command['text'])
    await slack.query(methods.CHAT_POST_MESSAGE, {'channel': channel, 'text': message})


async def slash_lunch(command, app):
    param_dict = split_params(command.get('text'))
    params = (
        ('zip', f'{param_dict["location"]}'),
        ('query', 'lunch'),
        ('radius', f'{param_dict["range"]}'),
    )

    async with app.http_session.get('https://wheelof.com/lunch/yelpProxyJSON.php', params=params) as r:
        r.raise_for_status()
        loc = get_random_lunch(await r.json())
        logger.info(f"location selected for {command['user_name']}: {loc}")
        return build_response_text(loc)
