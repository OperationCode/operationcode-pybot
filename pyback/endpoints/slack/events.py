import asyncio
import logging

from slack import methods
from slack.events import Message
from slack.io.abc import SlackAPI

from pyback.endpoints.slack.utils.action_messages import not_greeted_attachment
from pyback.endpoints.slack.utils.event_messages import *
from .utils import COMMUNITY_CHANNEL

LOG = logging.getLogger(__name__)


def create_endpoints(plugin):
    plugin.on_event("team_join", team_join, wait=False)


async def team_join(event, app):
    slack_api = app.plugins["slack"].api

    *user_messages, community_message = _build_messages(event['user']['id'])
    futures = [_send_user_greetings(user_messages, slack_api),
               _send_community_notification(community_message, slack_api)]

    asyncio.sleep(30)
    await asyncio.wait(futures)


def _build_messages(user_id):
    initial_message = _base_user_message(user_id)
    initial_message['text'] = team_join_initial_message(user_id)

    second_message = _base_user_message(user_id)
    second_message['text'] = second_team_join_message()
    second_message['attachments'] = external_button_attachments()

    action_menu = _base_user_message(user_id)
    action_menu['text'] = 'We recommend the following resources.'
    action_menu['attachments'] = base_resources()

    community_message = Message()
    community_message['text'] = f':tada: <@{user_id}> has joined! :tada:'
    community_message['attachments'] = not_greeted_attachment()
    community_message['channel'] = COMMUNITY_CHANNEL

    return initial_message, second_message, action_menu, community_message


async def _send_user_greetings(user_messages: List[Message], slack_api: SlackAPI):
    for message in user_messages:
        await slack_api.query(url=methods.CHAT_POST_MESSAGE, data=message)


async def _send_community_notification(community_message: Message, slack_api: SlackAPI):
    return await slack_api.query(url=methods.CHAT_POST_MESSAGE, data=community_message)


def _base_user_message(user_id):
    message = Message()
    message['channel'] = user_id
    message['as_user'] = True
    return message
