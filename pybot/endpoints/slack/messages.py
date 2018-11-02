import logging
from pprint import pformat

logger = logging.getLogger(__name__)


def create_endpoints(plugin):
    plugin.on_message(".*", message_changed, subtype="message_changed")
    plugin.on_message(".*", message_deleted, subtype="message_deleted")



def not_bot_message(event):
    return 'message' not in event or 'subtype' not in event['message'] or event['message']['subtype'] != 'bot_message'


async def message_changed(event, app):
    if not_bot_message(event):
        try:
            logger.info(
                f'CHANGE_LOGGING: edited: {event["ts"]} for user: {event["previous_message"]["user"]}\n{event}')

        except Exception as E:
            logger.exception(E)
            logger.debug(event)


async def message_deleted(event, app):
    if not_bot_message(event):
        try:
            logger.info(
                f'CHANGE_LOGGING: deleted: {event["ts"]} for user: {event["previous_message"]["user"]}\n{event}')

        except Exception as E:
            logger.exception(E)
            logger.debug(event)
