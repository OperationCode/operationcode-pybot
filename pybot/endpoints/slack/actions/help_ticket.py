from sirbot import SirBot
from slack import methods
from slack.actions import Action

from pybot.endpoints.slack.utils import TICKET_CHANNEL
from pybot.endpoints.slack.utils.action_messages import (
    ticket_attachments,
    updated_ticket_status,
    update_ticket_message,
)


async def ticket_status(action: Action, app: SirBot):
    """
    Updates the ticket status dropdown. (I don't know why we need to manually
    update the message for this..)
    """
    slack = app.plugins["slack"].api

    response, selected_option = updated_ticket_status(action)
    update_message = update_ticket_message(action, selected_option["text"])

    await slack.query(methods.CHAT_UPDATE, response)
    await slack.query(methods.CHAT_POST_MESSAGE, update_message)


async def open_ticket(action: Action, app: SirBot):
    """
    Called when a user submits the ticket dialog.  Parses the submission and posts
    the new ticket details to the required channel
    """
    attachments = ticket_attachments(action)
    response = {
        "channel": TICKET_CHANNEL,
        "attachments": attachments,
        "text": "New Ticket Submission",
    }

    await app["plugins"]["slack"].api.query(methods.CHAT_POST_MESSAGE, response)
