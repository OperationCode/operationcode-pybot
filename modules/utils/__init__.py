"""Utility functions for the Slack app."""
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from re import sub

from dotenv import load_dotenv
from pyairtable import Table
from slack_bolt.app import App
from slack_sdk.models.blocks import MarkdownTextObject, SectionBlock
from slack_sdk.web.async_client import AsyncWebClient

from modules.models.greeting_models import UserInfo
from modules.models.slack_models.shared_models import (
    SlackConversationInfo,
    SlackTeam,
    SlackTeamInfo,
)

logger = logging.getLogger(__name__)
load_dotenv(dotenv_path=str(Path(__file__).parent.parent.parent) + "/.env")


def snake_case(string_to_snakecase: str) -> str:
    """Snake case a string using regex.

    from https://www.w3resource.com/python-exercises/string/python-data-type-string-exercise-97.php.

    :param string_to_snakecase: The string to be snake-cased.
    :return: The snake-cased string.
    """
    return "_".join(
        sub(
            "([A-Z][a-z]+)",
            r" \1",
            sub("([A-Z]+)", r" \1", string_to_snakecase.replace("-", " ")),
        ).split(),
    ).lower()


def get_team_info() -> SlackTeam:
    """Get the team information from Slack.

    Uses a new synchronous Slack app to retrieve the details, so this can happen before the async app is initialized.

    :return: The SlackTeam object.
    """
    logger.info("STAGE: Retrieving team information...")
    try:
        synchronous_app = App(
            token=os.environ.get("SLACK_BOT_TOKEN"),
            signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
        )
        team_info = synchronous_app.client.team_info()
        conversations = synchronous_app.client.conversations_list(
            exclude_archived=True,
            types=["public_channel", "private_channel"],
            limit=1000,
        )
        return SlackTeam(
            SlackTeamInfo(
                id=team_info["team"]["id"],
                name=team_info["team"]["name"],
                conversations=[
                    SlackConversationInfo(**conversation) for conversation in conversations.data["channels"]
                ],
            ),
        )
    except Exception:
        logger.exception("Failed to retrieve team information.")
        raise
    finally:
        del synchronous_app


async def get_slack_user_from_email(client: AsyncWebClient, email: str) -> UserInfo:
    """Retrieve a Slack user from Slack using email.

    :param client: The Slack client.
    :param email: The email address of the user.
    :return: The UserInfo object.
    """
    slack_user = await client.users_lookupByEmail(email=email)
    return UserInfo(
        **slack_user.data["user"],
        email=slack_user.data["user"]["profile"]["email"],
    )


async def get_slack_user_by_id(client: AsyncWebClient, user_id: str) -> UserInfo:
    """Retrieve a Slack user from Slack using the Slack user ID.

    :param client: The Slack client.
    :param user_id: The Slack user ID.
    :return: The UserInfo object.
    """
    slack_user = await client.users_info(user=user_id)
    return UserInfo(
        **slack_user.data["user"],
        email=slack_user.data["user"]["profile"]["email"],
    )


async def log_to_thread(  # noqa: PLR0913 - too many arguments
    client: AsyncWebClient,
    channel_id: str,
    message_ts: str,
    username: str,
    action_ts: str,
    claim: bool,  # noqa: FBT001
) -> None:
    """Log a claim or reset to a thread.

    :param client: The Slack client.
    :param channel_id: The channel ID of the message.
    :param message_ts: The timestamp of the message.
    :param username: The username of the user performing the action.
    :param action_ts: The timestamp of the action.
    :param claim: Whether it's a claim or reset action.
    """
    await client.chat_postMessage(
        channel=channel_id,
        thread_ts=message_ts,
        text="Logging to greeting thread...",
        blocks=[threaded_action_logging(username, action_ts, claim)],
    )


def threaded_action_logging(username: str, timestamp: str, claim: bool) -> SectionBlock:  # noqa: FBT001
    """Return a block that is used to log a claim or reset to a thread.

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
            text=f"Claimed by {username} at "
            f"{datetime.fromtimestamp(float(timestamp), tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC!",
        )
    else:
        text = MarkdownTextObject(
            text=f"Reset by {username} at "
            f"{datetime.fromtimestamp(float(timestamp), tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC!",
        )
    return SectionBlock(block_id="greeting_log_reply", text=text)


def table_fields(table: Table) -> list[str]:
    """Return snake cased columns (fields in Airtable parlance) on the table.

    Because we don't have access to the Airtable metadata API, we must set up a view on every table with every column
    filled in since as the Airtable API says - "Returned records do not include any fields with "empty"
    values, e.g. "", [], or false.".

    :return: List of fields on the table.
    """
    try:
        first_record = table.first(view="Fields")
        return [snake_case(field) for field in first_record["fields"]]
    except Exception:
        logger.exception("Unable to retrieve fields from Airtable.")
        raise


slack_team = get_team_info()
