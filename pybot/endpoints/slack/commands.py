import logging

from slack import methods

from pybot.endpoints.slack.utils.command_utils import get_slash_here_message
from pybot.endpoints.slack.utils.slash_lunch import split_params, get_random_lunch, build_response_text
from pybot.endpoints.slack.utils import PYBACK_HOST, PYBACK_PORT, PYBACK_TOKEN

logger = logging.getLogger(__name__)


def create_endpoints(plugin):
    plugin.on_command('/here', slash_here, wait=False)
    plugin.on_command('/lunch', slash_lunch, wait=False)


async def slash_here(command, app):
    channel_id = command['channel_id']
    slack_id = command['user_id']
    slack = app["plugins"]["slack"].api

    params = {'slack_id': slack_id, 'channel_id': channel_id}
    headers = {'Authorization': f'Token {PYBACK_TOKEN}'}
    logger.info(f'headers: {headers}')

    async with app.http_session.get(f'http://{PYBACK_HOST}:{PYBACK_PORT}/api/mods/',
                                    params=params, headers=headers) as r:
        if r.status >= 400:
            return

        response = await r.json()
        if not len(response):
            return

    message = await get_slash_here_message(channel_id, slack, command['text'])
    await slack.query(methods.CHAT_POST_MESSAGE, {'channel': channel_id, 'text': message})


async def slash_lunch(command, app):
    channel_id = command['channel_id']
    user_id = command['user_id']
    slack = app["plugins"]["slack"].api

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
        message = build_response_text(loc)

        await slack.query(methods.CHAT_POST_EPHEMERAL, {'user': user_id, 'channel': channel_id, 'text': message})
