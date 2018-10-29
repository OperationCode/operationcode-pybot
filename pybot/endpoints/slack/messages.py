import logging
from pprint import pformat

logger = logging.getLogger(__name__)


def create_endpoints(plugin):
    plugin.on_message(".*", message_changed, subtype="message_changed")
    plugin.on_message(".*", message_deleted, subtype="message_deleted")


def match_edit_or_delete(message_json):
    subtype = message_json.get('subtype')
    if subtype:
        return any(subtype == desired_match for desired_match in ['message_changed', 'message_deleted'])
    return False


async def message_changed(event, app):
    try:
        logger.debug(f'message changed event data: {pformat(event)}')
        logger.info(
            f'CHANGE_LOGGING: edited: {event["ts"]} for user: {event["previous_message"]["user"]}\n{event}')

    except Exception as E:
        logger.exception(E)
        logger.debug(event)


async def message_deleted(event, app):
    try:
        logger.debug(f'message deleted event data: {pformat(event)}')
        logger.info(
            f'CHANGE_LOGGING: deleted: {event["ts"]} for user: {event["previous_message"]["user"]}\n{event}')

    except Exception as E:
        logger.exception(E)
        logger.debug(event)
