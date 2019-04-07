from typing import Optional

from slack import ROOT_URL
from slack.exceptions import SlackAPIError
from slack.io.abc import SlackAPI


async def _slack_info_from_email(
    email: str, slack: SlackAPI, fallback: Optional[str] = None
):
    try:
        response = await slack.query(
            url=ROOT_URL + "users.lookupByEmail", data={"email": email}
        )
        return response["user"]
    except SlackAPIError:
        return fallback
