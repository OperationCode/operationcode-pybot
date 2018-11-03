import logging

from sirbot import SirBot
from slack.events import Message

logger = logging.getLogger(__name__)


def create_endpoints(plugin):
    plugin.on_message(".*", message_changed, subtype="message_changed")
    plugin.on_message(".*", message_deleted, subtype="message_deleted")


def not_bot_message(event: Message):
    return 'message' not in event or 'subtype' not in event['message'] or event['message']['subtype'] != 'bot_message'


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
    if not_bot_message(event):
        try:
            logger.info(
                f'CHANGE_LOGGING: deleted: {event["ts"]} for user: {event["previous_message"]["user"]}\n{event}')

        except Exception as E:
            logger.exception(E)
            logger.debug(event)
