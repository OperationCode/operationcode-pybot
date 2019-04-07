from slack.exceptions import SlackAPIError
from slack.methods import Methods
from slack.io.abc import SlackAPI
from slack import ROOT_URL
from typing import Optional

from pybot.endpoints.slack.utils import TICKET_CHANNEL
from pybot.endpoints.slack.utils.action_messages import (
    TICKET_OPTIONS,
    not_claimed_attachment,
)


async def _slack_info_from_email(
    email: str, slack: SlackAPI, fallback: Optional[dict] = None
) -> dict:
    try:
        response = await slack.query(
            url=ROOT_URL + "users.lookupByEmail", data={"email": email}
        )
        return response["user"]
    except SlackAPIError:
        return fallback


def invite_failure_attachments(email: str, error: str) -> list:
    attachments = [
        {
            "text": "",
            "callback_id": "ticket_status",
            "response_type": "in_channel",
            "fallback": "",
            "fields": [
                {"title": "Email", "value": f"{email}", "short": True},
                {"title": "Error", "value": f"{error}", "short": True},
            ],
            "actions": [
                {
                    "name": "status",
                    "text": "Current Status",
                    "type": "select",
                    "selected_options": [
                        {"text": "Not Started", "value": "notStarted"}
                    ],
                    "options": [
                        {"text": text, "value": value}
                        for value, text in TICKET_OPTIONS.items()
                    ],
                }
            ],
        },
        not_claimed_attachment(),
    ]
    return attachments


async def handle_slack_invite_error(email, error, slack):
    if error.error == "already_invited":
        return error.data

    attachments = invite_failure_attachments(email, error)

    if error.error == "already_in_team":
        slack_user = await _slack_info_from_email(email, slack)
        attachments[0]["fields"].append(
            {
                "title": "Slack Username",
                "value": f"<@{slack_user['id']}>",
                "short": True,
            }
        )

    response = {
        "channel": TICKET_CHANNEL,
        "attachments": attachments,
        "text": "User Slack Invite Error",
    }

    return await slack.query(Methods.CHAT_POST_MESSAGE, response)
