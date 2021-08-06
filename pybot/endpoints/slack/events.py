import asyncio
import logging

from sirbot import SirBot
from slack.events import Event

from pybot.endpoints.slack.utils.event_utils import (
    build_messages,
    get_backend_auth_headers,
    link_backend_user,
    send_community_notification,
    send_user_greetings,
    build_delayed_messages,
    send_social_cta,
)

logger = logging.getLogger(__name__)


def create_endpoints(plugin):
    plugin.on_event("team_join", team_join, wait=False)
    plugin.on_event("team_join", team_join_delayed, wait=False)


async def team_join(event: Event, app: SirBot) -> None:
    """
    Handler for when the Slack workspace has a new member join.

    After 30 seconds sends the new user a greeting, some resource links, and
    notifies the community channel of the new member.
    """
    slack_api = app.plugins["slack"].api
    user_id = event["user"]["id"]

    *user_messages, community_message, outreach_team_message = build_messages(user_id)
    futures = [
        send_user_greetings(user_messages, slack_api),
        send_community_notification(community_message, slack_api),
        send_community_notification(outreach_team_message, slack_api),
    ]

    logger.info(f"New team join event: {event}")
    await asyncio.sleep(30)
    await asyncio.wait(futures)

    headers = await get_backend_auth_headers(app.http_session)
    if headers:
        await link_backend_user(user_id, headers, slack_api, app.http_session)

async def team_join_delayed(event: Event, app: SirBot) -> None:
    """
    Handler for when the Slack workspace has a new member join.

    After 1 day sends the new user a greeting, a call to action to join social media
    """
    slack_api = app.plugins["slack"].api
    user_id = event["user"]["id"]

    social_media_messages = build_delayed_messages(user_id)
    future = [ send_social_cta(social_media_messages, slack_api) ]

    logger.info(f"Scheduling delayed message")
    await asyncio.sleep(60)
    await asyncio.wait(future)
