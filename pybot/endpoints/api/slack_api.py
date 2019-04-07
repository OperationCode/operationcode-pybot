import logging
from sirbot import SirBot
from slack import ROOT_URL
from slack.exceptions import SlackAPIError
from aiohttp.web_request import Request

from pybot.endpoints.api.utils import _slack_info_from_email

logger = logging.getLogger(__name__)


def create_endpoints(plugin):
    plugin.on_get("verify", verify, wait=True)
    plugin.on_get("invite", invite, wait=True)


async def verify(request: Request, app: SirBot) -> any:
    """
    Verifies whether a user exists in the configured slack group with
    the given email

    :return: The user's slack id and displayName if they exist
    """
    slack = app.plugins["slack"].api
    email = request.query["email"]

    user = await _slack_info_from_email(email, slack)
    if user:
        return {"exists": True, "id": user["id"], "displayName": user["name"]}
    return {"exists": False}


async def invite(request: Request, app: SirBot):
    """
    Pulls an email out of the querystring and sends it an invite
    to the slack team

    :return: The request response from slack
    """
    try:
        slack = app.plugins["admin_slack"].api
        email = request.query["email"]

        response = await slack.query(
            url=ROOT_URL + "users.admin.invite", data={"email": email}
        )
        # logger.info("Response from slack: ", response)
        return response

    except SlackAPIError as e:
        logger.info(e)
        return e.data
