from sirbot import SirBot
from slack import methods
from slack.actions import Action

from pybot.endpoints.slack.utils.action_messages import *
from pybot.endpoints.slack.utils import COMMUNITY_CHANNEL


def create_endpoints(plugin):
    plugin.on_action("resource_buttons", resource_buttons, wait=False)
    plugin.on_action("greeted", member_greeted, name='greeted', wait=False)
    plugin.on_action("greeted", reset_greet, name='reset_greet', wait=False)
    plugin.on_action("suggestion", open_suggestion, wait=False)
    plugin.on_action("suggestion_modal", post_suggestion, wait=False)
    plugin.on_action("claim_mentee", claim_mentee, wait=False)
    plugin.on_action("reset_claim_mentee", claim_mentee, wait=False)
    plugin.on_action("claimed", claimed, name='claimed', wait=False)
    plugin.on_action("claimed", reset_claim, name='reset_claim', wait=False)


async def resource_buttons(action: Action, app: SirBot):
    """
    Edits the resource message with the clicked on resource
    """
    name = action['actions'][0]['name']

    response = base_response(action)
    response['text'] = HELP_MENU_RESPONSES[name]

    await app.plugins["slack"].api.query(methods.CHAT_UPDATE, response)


async def open_suggestion(action: Action, app: SirBot):
    """
    Opens the suggestion modal when the user clicks on the "Are we missing something?" button
    """
    trigger_id = action['trigger_id']
    response = {
        'trigger_id': trigger_id,
        'dialog': suggestion_dialog(trigger_id)
    }

    await app.plugins["slack"].api.query(methods.DIALOG_OPEN, response)


async def post_suggestion(action: Action, app: SirBot):
    """
    Posts a suggestion supplied by the suggestion modal to the community channel
    """
    suggesting_user = action['user']['id']
    suggestion = action['submission']['suggestion']

    response = {
        'text': new_suggestion_text(suggesting_user, suggestion),
        'channel': COMMUNITY_CHANNEL
    }

    await app.plugins["slack"].api.query(methods.CHAT_POST_MESSAGE, response)


async def member_greeted(action: Action, app: SirBot):
    """
    Called when a community member clicks the button saying they greeted the new member
    """
    response = base_response(action)
    user_id = action['user']['id']
    response['attachments'] = greeted_attachment(user_id)

    await app.plugins["slack"].api.query(methods.CHAT_UPDATE, response)


async def reset_greet(action: Action, app: SirBot):
    """
    Resets the claim greet button back to its initial state and appends the user that hit reset and the time
    """
    response = base_response(action)
    response['attachments'] = not_greeted_attachment()
    response['attachments'][0]['text'] = reset_greet_message(action['user']['id'])

    await app.plugins["slack"].api.query(methods.CHAT_UPDATE, response)


async def claimed(action: Action, app: SirBot):
    """
    Provides basic "claim" functionality for use-cases that don't have any other effects.

    Simply updates the button to allow resets and displays the user and time it was clicked.
    """
    response = base_response(action)
    user_id = action['user']['id']
    response['attachments'] = claimed_attachment(user_id)

    await app.plugins['slack'].api.query(methods.CHAT_UPDATE, response)


async def reset_claim(action: Action, app: SirBot):
    """
    Provides basic "unclaim" functionality for use-cases that don't have any other effects.

    Updates the button back to its initial state
    """
    response = base_response(action)
    response['attachments'] = not_claimed_attachment()
    await app.plugins['slack'].api.query(methods.CHAT_UPDATE, response)


async def claim_mentee(action: Action, app: SirBot):
    """
    Called when a mentor clicks on the button to claim a mentor request.

    Attempts to update airtable with the new request status and updates the claim
    button allowing it to be reset if needed.
    """
    update_airtable = True
    clicker_id = action['user']['id']
    request_record = action['actions'][0]['name']
    click_type = action['actions'][0]['value']

    response = base_response(action)

    user_info = await app.plugins['slack'].api.query(methods.USERS_INFO, dict(user=clicker_id))
    clicker_email = user_info['user']['profile']['email']

    if click_type == 'mentee_claimed':
        mentor_id = await app.plugins['airtable'].api.mentor_id_from_slack_email(clicker_email)
        if mentor_id:
            attachment = mentee_claimed_attachment(clicker_id, request_record)
        else:
            update_airtable = False
            attachment = action['original_message']['attachments']
            attachment[0]['text'] = f":warning: <@{clicker_id}>'s slack Email not found in Mentor table. :warning:"
    else:
        mentor_id = ''
        attachment = mentee_unclaimed_attachment(clicker_id, request_record)

    response['attachments'] = attachment

    await app.plugins['slack'].api.query(methods.CHAT_UPDATE, response)
    if update_airtable:
        await app.plugins['airtable'].api.update_request(request_record, mentor_id)
