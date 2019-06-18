from sirbot import SirBot
from slack import methods
from slack.actions import Action

from pybot.endpoints.slack.utils import COMMUNITY_CHANNEL
from pybot.endpoints.slack.utils.action_messages import (
    HELP_MENU_RESPONSES,
    base_response,
    greeted_attachment,
    new_suggestion_text,
    not_greeted_attachment,
    reset_greet_message,
    suggestion_dialog,
)


async def resource_buttons(action: Action, app: SirBot):
    """
    Edits the resource message with the clicked on resource
    """
    name = action["actions"][0]["name"]

    response = base_response(action)
    response["text"] = HELP_MENU_RESPONSES[name]

    await app.plugins["slack"].api.query(methods.CHAT_UPDATE, response)


async def open_suggestion(action: Action, app: SirBot):
    """
    Opens the suggestion modal when the user clicks on the "Are we missing something?" button
    """
    trigger_id = action["trigger_id"]
    response = {"trigger_id": trigger_id, "dialog": suggestion_dialog(trigger_id)}

    await app.plugins["slack"].api.query(methods.DIALOG_OPEN, response)


async def post_suggestion(action: Action, app: SirBot):
    """
    Posts a suggestion supplied by the suggestion modal to the community channel
    """
    suggesting_user = action["user"]["id"]
    suggestion = action["submission"]["suggestion"]

    response = {
        "text": new_suggestion_text(suggesting_user, suggestion),
        "channel": COMMUNITY_CHANNEL,
    }

    await app.plugins["slack"].api.query(methods.CHAT_POST_MESSAGE, response)


async def member_greeted(action: Action, app: SirBot):
    """
    Called when a community member clicks the button saying they greeted the new member
    """
    response = base_response(action)
    user_id = action["user"]["id"]
    response["attachments"] = greeted_attachment(user_id)

    await app.plugins["slack"].api.query(methods.CHAT_UPDATE, response)


async def reset_greet(action: Action, app: SirBot):
    """
    Resets the claim greet button back to its initial state and appends the user that hit reset and the time
    """
    response = base_response(action)
    response["attachments"] = not_greeted_attachment()
    response["attachments"][0]["text"] = reset_greet_message(action["user"]["id"])

    await app.plugins["slack"].api.query(methods.CHAT_UPDATE, response)
