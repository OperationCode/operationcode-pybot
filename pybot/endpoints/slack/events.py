import asyncio
import logging

from pybot.endpoints.slack.utils.event_utils import build_messages, send_user_greetings, send_community_notification

logger = logging.getLogger(__name__)


def create_endpoints(plugin):
    plugin.on_event("team_join", team_join, wait=False)
    plugin.on_event("message", messages, wait=False)


async def team_join(event, app):
    slack_api = app.plugins["slack"].api

    *user_messages, community_message = build_messages(event['user']['id'])
    futures = [send_user_greetings(user_messages, slack_api),
               send_community_notification(community_message, slack_api)]

    asyncio.sleep(30)
    await asyncio.wait(futures)


def match_edit_or_delete(message_json):
    subtype = message_json.get('subtype')
    if subtype:
        return any(subtype == desired_match for desired_match in ['message_changed', 'message_deleted'])
    return False


async def messages(event, app):
    if match_edit_or_delete(event):
        logger.info(
            f'user_id: {event["message"]["edited"]["user"]} has performed {event["subtype"]} on  message: {event["ts"]} for user: {event["message"]["user"]}')
        logger.info(event)

