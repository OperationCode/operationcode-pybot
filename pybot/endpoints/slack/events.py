import asyncio
import logging
from pybot.endpoints.slack.utils.event_utils import build_messages, send_user_greetings, send_community_notification

logger = logging.getLogger(__name__)


def create_endpoints(plugin):
    plugin.on_event("team_join", team_join, wait=False)
    plugin.on_message(".*", messages, subtype="message_change")
    plugin.on_message(".*", messages, subtype="message_deleted")


async def team_join(event, app):
    slack_api = app.plugins["slack"].api

    *user_messages, community_message = build_messages(event['user']['id'])
    futures = [send_user_greetings(user_messages, slack_api),
               send_community_notification(community_message, slack_api)]

    await asyncio.sleep(30)
    await asyncio.wait(futures)

async def messages(event, app):
    try:
        logger.info(
            f'user_id: {event["message"]["edited"]["user"]} has performed {event["subtype"]} on  message: {event["ts"]} for user: {event["message"]["user"]}')
        logger.info(event)

    except Exception as E:
        logger.exception(E)
        logger.debug(event)
