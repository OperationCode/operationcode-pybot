import asyncio
import logging
from pprint import pformat
from pybot.endpoints.slack.utils.event_utils import build_messages, send_user_greetings, send_community_notification

logger = logging.getLogger(__name__)


def create_endpoints(plugin):
    plugin.on_event("team_join", team_join, wait=False)
    plugin.on_message(".*", message_changed, subtype="message_changed")
    plugin.on_message(".*", message_deleted, subtype="message_deleted")


async def team_join(event, app):
    slack_api = app.plugins["slack"].api

    *user_messages, community_message = build_messages(event['user']['id'])
    futures = [send_user_greetings(user_messages, slack_api),
               send_community_notification(community_message, slack_api)]

    asyncio.sleep(30)
    await asyncio.wait(futures)


async def message_changed(event, app):
        try:
            logger.info(f'message changed event data: {pformat(event)}')
            logger.info(
                f'message edited: {event["ts"]} for user: {event["previous_message"]["user"]}')

        except Exception as E:
            logger.exception(E)
            logger.debug(event)


async def message_deleted(event, app):
    try:
        logger.info(f'message deleted event data: {pformat(event)}')
        logger.info(
            f'message deleted: {event["ts"]} for user: {event["previous_message"]["user"]}')

    except Exception as E:
        logger.exception(E)
        logger.debug(event)
