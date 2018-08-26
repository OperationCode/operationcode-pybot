from typing import List

from slack.events import Message
from slack.io.abc import SlackAPI
from slack import methods

from pyback.endpoints.slack.utils import COMMUNITY_CHANNEL
from pyback.endpoints.slack.utils.action_messages import not_greeted_attachment
from pyback.endpoints.slack.utils.event_messages import team_join_initial_message, second_team_join_message, \
    external_button_attachments, base_resources


def build_messages(user_id):
    initial_message = base_user_message(user_id)
    initial_message['text'] = team_join_initial_message(user_id)

    second_message = base_user_message(user_id)
    second_message['text'] = second_team_join_message()
    second_message['attachments'] = external_button_attachments()

    action_menu = base_user_message(user_id)
    action_menu['text'] = 'We recommend the following resources.'
    action_menu['attachments'] = base_resources()

    community_message = Message()
    community_message['text'] = f':tada: <@{user_id}> has joined! :tada:'
    community_message['attachments'] = not_greeted_attachment()
    community_message['channel'] = COMMUNITY_CHANNEL

    return initial_message, second_message, action_menu, community_message


async def send_user_greetings(user_messages: List[Message], slack_api: SlackAPI):
    for message in user_messages:
        await slack_api.query(url=methods.CHAT_POST_MESSAGE, data=message)


async def send_community_notification(community_message: Message, slack_api: SlackAPI):
    return await slack_api.query(url=methods.CHAT_POST_MESSAGE, data=community_message)


def base_user_message(user_id):
    message = Message()
    message['channel'] = user_id
    message['as_user'] = True
    return message
