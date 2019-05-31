import json

from sirbot import SirBot

from pybot.endpoints.slack.utils.action_messages import (
    build_report_message,
    report_dialog,
)
from slack import methods
from slack.actions import Action


async def send_report(action: Action, app: SirBot):
    """
    Called when a user submits the report dialog.  Pulls the original message
    info from the state and posts the details to the moderators channel
    """
    slack_id = action["user"]["id"]
    details = action["submission"]["details"]
    message_details = json.loads(action.action["state"])

    response = build_report_message(slack_id, details, message_details)

    await app["plugins"]["slack"].api.query(methods.CHAT_POST_MESSAGE, response)


async def open_report_dialog(action: Action, app: SirBot):
    """
    Opens the message reporting dialog for the user to provide details.

    Adds the message that they're reporting to the dialog's hidden state
    to be pulled out when submitted.
    """
    trigger_id = action["trigger_id"]
    response = {"trigger_id": trigger_id, "dialog": report_dialog(action)}
    await app.plugins["slack"].api.query(methods.DIALOG_OPEN, response)
