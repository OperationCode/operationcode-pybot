import logging
from typing import Dict, List, Tuple

from aiohttp import ClientSession
from slack import methods
from slack.events import Message
from slack.io.abc import SlackAPI

from pybot.endpoints.slack.utils import (
    BACKEND_PASS,
    BACKEND_URL,
    BACKEND_USERNAME,
    COMMUNITY_CHANNEL,
)
from pybot.endpoints.slack.utils.action_messages import (
    not_direct_messaged_attachment,
    not_greeted_attachment,
)
from pybot.endpoints.slack.utils.event_messages import (
    base_resources,
    external_button_attachments,
    second_team_join_message,
    team_join_initial_message,
)

logger = logging.getLogger(__name__)


def base_user_message(user_id: str) -> Message:
    message = Message()
    message["channel"] = user_id
    message["as_user"] = True
    return message


def build_messages(user_id) -> Tuple[Message, Message, Message, Message, Message]:
    initial_message = base_user_message(user_id)
    initial_message["text"] = team_join_initial_message(user_id)

    second_message = base_user_message(user_id)
    second_message["text"] = second_team_join_message()
    second_message["attachments"] = external_button_attachments()

    action_menu = base_user_message(user_id)
    action_menu["text"] = "We recommend the following resources."
    action_menu["attachments"] = base_resources()

    community_message = Message()
    community_message["text"] = f":tada: <@{user_id}> has joined! :tada:"
    community_message["attachments"] = not_greeted_attachment()
    community_message["channel"] = COMMUNITY_CHANNEL

    outreach_team_message = Message()
    outreach_team_message["text"] = (
        f":spiral_note_pad: Outreach Team: Please reach out to <@{user_id}> via DM"
        f":spiral_note_pad: "
    )
    outreach_team_message["attachments"] = not_direct_messaged_attachment()
    outreach_team_message["channel"] = COMMUNITY_CHANNEL

    return (
        initial_message,
        second_message,
        action_menu,
        community_message,
        outreach_team_message,
    )

def build_delayed_messages(user_id) -> Tuple[Message]:
    social_media_message = base_user_message(user_id)
    social_media_message["text"] = (
        f"Welcome to Operation Code's Slack Community, we're glad you're here! "
        f"Please share with us in #general what brings you to Operation Code, "
        f"and how we can assist you. Also, consider adding to your Operation Code "
        f"profile the links to your LinkedIn and GitHub accounts. "
        f"Lastly, consider connecting with us on our social media accounts: "
        f"<a href='https://www.facebook.com/operationcode.org/'>Facebook</a>, "
        f"<a href='https://twitter.com/operation_code'>Twitter</a>, "
        f"<a href='https://business.linkedin.com/marketing-solutions/higher-education'>LinkedIn</a>, "
        f"<a href='https://www.instagram.com/operation_code/?hl=en'>Instagram</a> and "
        f"<a href='https://www.youtube.com/channel/UCAoJt4a_KEBmgXfoQUrNbSA/featured?view_as=public'>YouTube</a>"
        f", and contribute to our open source platform on "
        f"<a href='https://github.com/OperationCode'>GitHub</a>. If you have any immediate needs, "
        f"please tag our @outreach-team in any public channel. "
    )

    return (
        social_media_message,
    )

async def send_user_greetings(
    user_messages: List[Message], slack_api: SlackAPI
) -> None:
    for message in user_messages:
        await slack_api.query(url=methods.CHAT_POST_MESSAGE, data=message)


async def send_community_notification(
    community_message: Message, slack_api: SlackAPI
) -> dict:
    return await slack_api.query(url=methods.CHAT_POST_MESSAGE, data=community_message)

async def send_social_cta(
   social_media_messages: List[Message], slack_api: SlackAPI
) -> None:
    for message in social_media_messages:
        await slack_api.query(url=methods.CHAT_POST_MESSAGE, data=message)

async def link_backend_user(
    slack_id: str,
    auth_header: Dict[str, str],
    slack_api: SlackAPI,
    session: ClientSession,
) -> None:
    """
    Updates the slack user with their profile in the backend
    """

    user_info = await slack_api.query(methods.USERS_INFO, {"user": slack_id})
    email = user_info["user"]["profile"]["email"]

    async with session.patch(
        f"{BACKEND_URL}/auth/profile/admin/",
        headers=auth_header,
        params={"email": email},
        json={"slackId": slack_id},
    ) as response:
        data = await response.json()
        logger.info(f"Backend response from user linking: {data}")


async def get_backend_auth_headers(session: ClientSession) -> Dict[str, str]:
    """
    Authenticates with the OC Backend server

    :return:  Authorization header containing the returned JWT
    """
    async with session.post(
        f"{BACKEND_URL}/auth/login/",
        json={"email": BACKEND_USERNAME, "password": BACKEND_PASS},
    ) as response:
        if 400 <= response.status:
            logger.exception("Failed to authenticate with backend")
            return {}
        response.raise_for_status()
        data = await response.json()
        headers = {"Authorization": f"Bearer {data['token']}"}
    return headers
