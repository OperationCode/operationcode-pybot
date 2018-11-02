import logging

from sirbot.plugins.slack import SlackPlugin
from slack import methods

from pybot.endpoints.slack.utils import PYBACK_HOST, PYBACK_PORT, PYBACK_TOKEN, REPORT_CHANNEL, YELP_TOKEN
from pybot.endpoints.slack.utils.action_messages import not_claimed_attachment
from pybot.endpoints.slack.utils.command_utils import get_slash_here_messages, get_slash_repeat_messages, response_type
from pybot.endpoints.slack.utils.slash_lunch import LunchCommand
from pybot.endpoints.slack.utils.slash_tech import TechTerms

logger = logging.getLogger(__name__)


# TODO: write input-serializer for the input from the slash command. see repeated code in each slash command


# TODO: write test to ensure these functions exist at compile time -unit
# TODO: write test to ensure that the slack api that is being targeted has the slash commands - integration
# TODO: write functionality to automatically add the slash command to slack api - integration
def create_endpoints(plugin: SlackPlugin):
    plugin.on_command('/here', slash_here, wait=False)
    plugin.on_command('/lunch', slash_lunch, wait=False)
    plugin.on_command('/repeat', slash_repeat, wait=False)
    plugin.on_command('/tech', slash_tech, wait=False)
    plugin.on_command('/report', slash_report, wait=False)


async def slash_report(command: dict, app):
    slack_id = command['user_id']
    text = command['text']

    slack = app["plugins"]["slack"].api

    message = f'<@{slack_id}> sent report: {text}'

    response = {
        'text': message,
        'channel': REPORT_CHANNEL,
        'attachments': not_claimed_attachment(),
    }

    await slack.query(methods.CHAT_POST_MESSAGE, response)



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
    logger.debug(command)
    lunch = LunchCommand(command['channel_id'], command['user_id'],
                         command.get('text'), command['user_name'])

    slack = app["plugins"]["slack"].api

    request = lunch.get_yelp_request()
    async with app.http_session.get(**request) as r:
        r.raise_for_status()
        message_params = lunch.select_random_lunch(await r.json())

        await slack.query(methods.CHAT_POST_EPHEMERAL, message_params)


async def slash_repeat(command: dict, app):
    logger.info(f'repeat command data incoming {command}')
    channel_id = command['channel_id']
    slack_id = command['user_id']
    slack = app["plugins"]["slack"].api

    method_type, message = get_slash_repeat_messages(slack_id, channel_id, command['text'])
    await slack.query(method_type, message)


async def slash_tech(command: dict, app):
    logger.info(f'tech command data incoming {command}')
    channel_id = command['channel_id']
    slack_id = command['user_id']
    slack = app["plugins"]["slack"].api

    tech_terms: dict = TechTerms(command['channel_id'], command['user_id'],
                                 command.get('text'), command['user_name'], app).grab_values()
    method_type = response_type(tech_terms['type'])
    text = tech_terms['message']
    message = {
        'text': text,
        'channel': channel_id,
        'user': slack_id
    }

    await slack.query(method_type, message)
