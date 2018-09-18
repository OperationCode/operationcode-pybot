import logging

from slack import methods

from pybot.endpoints.slack.utils.command_utils import get_slash_here_messages, get_slash_repeat_messages
from pybot.endpoints.slack.utils.slash_lunch import LunchCommand
from pybot.endpoints.slack.utils import PYBACK_HOST, PYBACK_PORT, PYBACK_TOKEN
from sirbot.plugins.slack import SlackPlugin

logger = logging.getLogger(__name__)


# TODO: write input-serializer for the input from the slash command. see repeated code in each slash command



# TODO: write test to ensure these functions exist at compile time -unit
# TODO: write test to ensure that the slack api that is being targeted has the slash commands - integration
# TODO: write functionality to automatically add the slash command to slack api - integration
def create_endpoints(plugin: SlackPlugin):
    plugin.on_command('/here', slash_here, wait=False)
    plugin.on_command('/lunch', slash_lunch, wait=False)
    plugin.on_command('/repeat', slash_repeat, wait=False)


async def slash_here(command: dict, app):
    channel_id = command['channel_id']
    slack_id = command['user_id']
    slack = app["plugins"]["slack"].api

    params = {'slack_id': slack_id, 'channel_id': channel_id}
    headers = {'Authorization': f'Token {PYBACK_TOKEN}'}

    logger.debug(f'/here params: {params}, /here headers {headers}')
    async with app.http_session.get(f'http://{PYBACK_HOST}:{PYBACK_PORT}/api/mods/',
                                    params=params, headers=headers) as r:

        logger.debug(f'pyback response status: {r.status}')
        if r.status >= 400:
            return

        response = await r.json()
        logger.debug(f'pyback response: {response}')
        if not len(response):
            return

    message, member_list = await get_slash_here_messages(slack_id, channel_id, slack, command['text'])

    response = await slack.query(methods.CHAT_POST_MESSAGE, {'channel': channel_id, 'text': message})
    timestamp = response['ts']
    await slack.query(methods.CHAT_POST_MESSAGE, {'channel': channel_id, 'text': member_list, 'thread_ts': timestamp})


async def slash_lunch(command: dict, app):
    lunch = LunchCommand(command['channel_id'], command['user_id'], app["plugins"]["slack"].api,
                         command.get('text'), command['user_name'])

    param_dict = lunch.lunch_api_params()

    params = (
        ('zip', f'{param_dict["location"]}'),
        ('query', 'lunch'),
        ('radius', f'{param_dict["range"]}'),
    )

    # TODO: turn this into a yelp plugin and stop using someone elses website
    async with app.http_session.get('https://wheelof.com/lunch/yelpProxyJSON.php', params=params) as r:
        r.raise_for_status()
        message_params = lunch.select_random_lunch(await r.json())

        await slack.query(methods.CHAT_POST_EPHEMERAL, message_params)


async def slash_repeat(command: dict, app):
    channel_id = command['channel_id']
    slack_id = command['user_id']
    slack = app["plugins"]["slack"].api

    method_type, message = get_slash_repeat_messages(slack_id, channel_id, command['text'])
    await slack.query(method_type, message)
