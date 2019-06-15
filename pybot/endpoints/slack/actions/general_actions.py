from sirbot import SirBot
from slack import methods
from slack.actions import Action

from pybot.endpoints.slack.utils.action_messages import (
    base_response,
    claimed_attachment,
    not_claimed_attachment,
)


async def claimed(action: Action, app: SirBot):
    """
    Provides basic "claim" functionality for use-cases that don't have any other effects.

    Simply updates the button to allow resets and displays the user and time it was clicked.
    """
    response = base_response(action)
    user_id = action["user"]["id"]

    attachments = action["original_message"]["attachments"]

    for index, attachment in enumerate(attachments):
        if "callback_id" in attachment and attachment["callback_id"] == "claimed":
            attachments[index] = claimed_attachment(user_id)
    response["attachments"] = attachments

    await app.plugins["slack"].api.query(methods.CHAT_UPDATE, response)


async def reset_claim(action: Action, app: SirBot):
    """
    Provides basic "unclaim" functionality for use-cases that don't have any other effects.

    Updates the button back to its initial state
    """
    response = base_response(action)

    attachments = action["original_message"]["attachments"]
    for index, attachment in enumerate(attachments):
        if "callback_id" in attachment and attachment["callback_id"] == "claimed":
            attachments[index] = not_claimed_attachment()

    response["attachments"] = attachments
    await app.plugins["slack"].api.query(methods.CHAT_UPDATE, response)


async def delete_message(action: Action, app: SirBot):
    slack = app.plugins["slack"].api
    params = {"ts": action["message"]["ts"], "channel": action["channel"]["id"]}

    await slack.query(methods.CHAT_DELETE, params)
