import logging

from sirbot import SirBot
from slack.events import Message
from slack import methods

from .message_templates.tech import TechTerms

logger = logging.getLogger(__name__)


def create_endpoints(plugin):
    plugin.on_message(".*", message_changed, subtype="message_changed")
    plugin.on_message(".*", message_deleted, subtype="message_deleted")
    plugin.on_message(".*\!tech", tech_tips)
    plugin.on_message(".*\<\!here\>", here_bad)
    plugin.on_message(".*\<\!channel\>", here_bad)
    plugin.on_message(".*@here", here_bad)
    plugin.on_message(".*@channel", here_bad)
    plugin.on_message(".*\!pybot", advertise_pybot)


def not_bot_message(event: Message):
    return 'message' not in event or 'subtype' not in event['message'] or event['message']['subtype'] != 'bot_message'


def not_bot_delete(event: Message):
    return 'previous_message' not in event or 'bot_id' not in event['previous_message']


async def advertise_pybot(event: Message, app: SirBot):
    BOT_URL = 'https://github.com/OperationCode/operationcode-pybot'
    response = {'channel': event['channel'],
                'text': f'OC-Community-Bot is a community led project'
                        f'\n <{BOT_URL}|source> '}
    await app.plugins["slack"].api.query(methods.CHAT_POST_MESSAGE, data=response)


async def here_bad(event: Message, app: SirBot):
    response = {'channel': event['channel'],
                'text': f'<@{event["user"]}> - you are a very bad person for using that command'}
    await app.plugins["slack"].api.query(methods.CHAT_POST_MESSAGE, data=response)


async def tech_tips(event: Message, app: SirBot):
    if not_bot_message(event):
        logger.info(
            f'tech logging: {event}')
        try:
            tech_terms: dict = await TechTerms(event['channel'], event['user'],
                                               event.get('text'), app).grab_values()

            await app.plugins["slack"].api.query(methods.CHAT_POST_MESSAGE, tech_terms['message'])
        except Exception as E:
            logger.exception(E)


async def message_changed(event: Message, app: SirBot):
    """
    Logs all message edits not made by a bot.
    """
    if not_bot_message(event):
        try:
            logger.info(
                f'CHANGE_LOGGING: edited: {event["ts"]} for user: {event["previous_message"]["user"]}\n{event}')

        except Exception as E:
            logger.exception(E)
            logger.debug(event)


async def message_deleted(event: Message, app: SirBot):
    """
    Logs all message deletions not made by a bot.
    """
    if not_bot_delete(event):
        try:
            logger.info(
                f'CHANGE_LOGGING: deleted: {event["ts"]} for user: {event["previous_message"]["user"]}\n{event}')

        except Exception as E:
            logger.exception(E)
            logger.debug(event)
