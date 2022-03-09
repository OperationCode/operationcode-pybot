import os
import logging
from datetime import datetime
from pathlib import Path
from re import sub
from functools import lru_cache
from pyairtable import Table
from slack_bolt.app import App
from slack_sdk.models.blocks import SectionBlock, MarkdownTextObject
from slack_sdk.web.async_client import AsyncWebClient
from dotenv import load_dotenv

from modules.models.greeting_models import UserInfo
from modules.models.slack_models.shared_models import (
    SlackConversationInfo,
    SlackTeamInfo,
    SlackTeam,
)

logger = logging.getLogger(__name__)


def snake_case(s: str) -> str:
    """Snake cases a string using regex - from
    https://www.w3resource.com/python-exercises/string/python-data-type-string-exercise-97.php

    :param s: string to be snake cased
    :type s: str
    :return: snake cased string
    :rtype: str
    """
    return "_".join(
        sub(
            "([A-Z][a-z]+)", r" \1", sub("([A-Z]+)", r" \1", s.replace("-", " "))
        ).split()
    ).lower()


@lru_cache
def get_team_info() -> SlackTeam:
    logger.info("STAGE: Retrieving team information...")
    try:
        synchronous_app = App(
            token=os.environ.get("SLACK_BOT_TOKEN"),
            signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
        )
        team_info = synchronous_app.client.team_info()
        conversations = synchronous_app.client.conversations_list(
            exclude_archived=True, types=["public_channel", "private_channel"]
        )
        slack_team_response = SlackTeam(
            SlackTeamInfo(
                id=team_info["team"]["id"],
                name=team_info["team"]["name"],
                conversations=[
                    SlackConversationInfo(**conversation)
                    for conversation in conversations.data["channels"]
                ],
            )
        )
        del synchronous_app
        return slack_team_response
    except Exception as e:
        raise e


async def get_slack_user_from_email(client: AsyncWebClient, email: str) -> UserInfo:
    slack_user = await client.users_lookupByEmail(email=email)
    return UserInfo(
        **slack_user.data["user"], email=slack_user.data["user"]["profile"]["email"]
    )


async def get_slack_user_by_id(client: AsyncWebClient, user_id: str) -> UserInfo:
    slack_user = await client.users_info(user=user_id)
    print(slack_user)
    return UserInfo(
        **slack_user.data["user"], email=slack_user.data["user"]["profile"]["email"]
    )


async def log_to_thread(
    client: AsyncWebClient,
    channel_id: str,
    message_ts: str,
    username: str,
    action_ts: str,
    claim: bool,
) -> None:
    await client.chat_postMessage(
        channel=channel_id,
        thread_ts=message_ts,
        text="Logging to greeting thread...",
        blocks=[threaded_action_logging(username, action_ts, claim)],
    )


def threaded_action_logging(username: str, timestamp: str, claim: bool) -> SectionBlock:
    """Returns a block that is used to log a claim or reset to a thread

    :param username: username of the user performing the action
    :type username: str
    :param timestamp: string timestamp of the action in Unix Epoch Time
    :type timestamp: str
    :param claim: whether it's a claim action or not
    :type claim: bool
    :return: a section block to be threaded on the original message
    :rtype: SectionBlock
    """
    if claim:
        text = MarkdownTextObject(
            text=f"Claimed by {username} at {datetime.utcfromtimestamp(float(timestamp)).strftime('%Y-%m-%d %H:%M:%S')} UTC!"
        )
    else:
        text = MarkdownTextObject(
            text=f"Reset by {username} at {datetime.utcfromtimestamp(float(timestamp)).strftime('%Y-%m-%d %H:%M:%S')} UTC!"
        )
    return SectionBlock(block_id="greeting_log_reply", text=text)


def table_fields(table: Table) -> list[str]:
    """Returns snake cased columns (fields in Airtable parlance) on the table
    Because we don't have access to the Airtable metadata API, we must set up a view on every table with every column
    filled in since as the Airtable API says - "Returned records do not include any fields with "empty" values, e.g. "", [], or false."

    :return: list of fields
    :rtype: list[str]
    """
    try:
        first_record = table.first(view="Fields")
        return [snake_case(field) for field in first_record["fields"].keys()]
    except Exception as e:
        raise e


load_dotenv(dotenv_path=f"{str(Path(__file__).parent.parent.parent)}/.env")

slack_team = get_team_info()
