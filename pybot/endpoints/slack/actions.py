from slack import methods

from pybot.endpoints.slack.utils.action_messages import *
from pybot.endpoints.slack.utils import COMMUNITY_CHANNEL


def create_endpoints(plugin):
    plugin.on_action("resource_buttons", resource_buttons_python, wait=False)
    plugin.on_action("greeted", member_greeted, name='greeted', wait=False)
    plugin.on_action("greeted", reset_greet, name='reset_greet', wait=False)
    plugin.on_action("suggestion", open_suggestion, wait=False)
    plugin.on_action("suggestion_modal", post_suggestion, wait=False)
    plugin.on_action("claim_mentee", claim_mentee, wait=False)
    plugin.on_action("reset_claim_mentee", claim_mentee, wait=False)
    plugin.on_action("claimed", claimed, name='claimed', wait=False)
    plugin.on_action("claimed", reset_claim, name='reset_claim', wait=False)


async def resource_buttons_python(action, app):
    response = Message()
    name = action['actions'][0]['name']

    response['text'] = HELP_MENU_RESPONSES[name]
    response['channel'] = action['channel']['id']
    response['ts'] = action['message_ts']
    response['as_user'] = True

    await app.plugins["slack"].api.query(methods.CHAT_UPDATE, response)


async def member_greeted(action, app):
    response = base_response(action)
    user_id = action['user']['id']
    response['attachments'] = greeted_attachment(user_id)

    await app.plugins["slack"].api.query(methods.CHAT_UPDATE, response)


async def claimed(action, app):
    response = base_response(action)
    user_id = action['user']['id']
    response['attachments'] = claimed_attachment(user_id)
    await app.plugins['slack'].api.query(methods.CHAT_UPDATE, response)


async def reset_claim(action, app):
    response = base_response(action)
    response['attachments'] = not_claimed_attachment()
    await app.plugins['slack'].api.query(methods.CHAT_UPDATE, response)


async def reset_greet(action, app):
    response = base_response(action)
    response['attachments'] = not_greeted_attachment()
    response['attachments'][0]['text'] = reset_greet_message(action['user']['id'])

    await app.plugins["slack"].api.query(methods.CHAT_UPDATE, response)


async def open_suggestion(action, app):
    response = Message()
    trigger_id = action['trigger_id']
    response['trigger_id'] = trigger_id
    response['dialog'] = suggestion_dialog(trigger_id)

    await app.plugins["slack"].api.query(methods.DIALOG_OPEN, response)


async def post_suggestion(action, app):
    response = Message()

    response['text'] = new_suggestion_text(action['user']['id'], action['submission']['suggestion'])
    response['channel'] = COMMUNITY_CHANNEL

    await app.plugins["slack"].api.query(methods.CHAT_POST_MESSAGE, response)


async def claim_mentee(action, app):
    update_airtable = True
    clicker_id = action['user']['id']
    request_record = action['actions'][0]['name']
    click_type = action['actions'][0]['value']

    response = base_claim_mentee_response(action)

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
