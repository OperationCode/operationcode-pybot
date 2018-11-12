import json

from sirbot import SirBot
from slack import methods
from slack.actions import Action

from pybot.endpoints.slack.message_templates.mentor_request import MentorRequest
from pybot.endpoints.slack.utils.action_messages import base_response, mentor_details_dialog, \
    mentee_unclaimed_attachment, mentee_claimed_attachment


async def mentor_request_submit(action: Action, app: SirBot):
    slack = app.plugins['slack'].api
    airtable = app.plugins['airtable'].api
    request = MentorRequest(action['original_message'], action['channel']['id'])

    if not request.validate_self():
        await request.update(slack)
        return

    username = action['user']['name']
    user_info = await slack.query(methods.USERS_INFO, {'user': action['user']['id']})
    email = user_info['user']['profile']['email']
    airtable_response = await request.submit_request(username, email, airtable)

    if 'error' in airtable_response:
        await request.submission_error(airtable_response, slack)
    else:
        await request.submission_complete(slack)

    # debugging
    await slack.query(methods.CHAT_POST_MESSAGE, {
        'channel': action['channel']['id'],
        'text': f' Debugging: {json.dumps(airtable_response)}\nAirtable response: {json.dumps(airtable_response)}'
    })


async def cancel_mentor_request(action: Action, app: SirBot):
    response = {'ts': action['message_ts'], 'channel': action['channel']['id']}
    await app.plugins['slack'].api.query(methods.CHAT_DELETE, response)


async def mentor_details_submit(action: Action, app: SirBot):
    slack = app.plugins['slack'].api

    state = json.loads(action['state'])
    channel = state['channel']
    ts = state['ts']
    search = {
        'inclusive': True, 'channel': channel,
        'oldest': ts, 'latest': ts
    }

    history = await slack.query(methods.IM_HISTORY, search)

    request = MentorRequest(history['messages'][0], channel)
    request.details = action['submission']['details']

    await request.update(slack)


async def open_details_dialog(action: Action, app: SirBot):
    trigger_id = action['trigger_id']
    response = {
        'trigger_id': trigger_id,
        'dialog': mentor_details_dialog(action),
    }
    await app.plugins["slack"].api.query(methods.DIALOG_OPEN, response)


async def clear_skillsets(action: Action, app: SirBot):
    request = MentorRequest(action['original_message'], action['channel']['id'])
    request.clear_skillsets()

    slack = app.plugins['slack'].api
    await request.update(slack)


async def set_group(action: Action, app: SirBot):
    group = MentorRequest.selected_option(action)
    request = MentorRequest(action['original_message'], action['channel']['id'])
    request.certify_group = group

    slack = app.plugins['slack'].api
    await request.update(slack)


async def set_requested_service(action: Action, app: SirBot):
    service = MentorRequest.selected_option(action)
    request = MentorRequest(action['original_message'], action['channel']['id'])
    request.service = service

    slack = app.plugins['slack'].api
    await request.update(slack)


async def set_requested_mentor(action: Action, app: SirBot):
    mentor = MentorRequest.selected_option(action)
    request = MentorRequest(action['original_message'], action['channel']['id'])
    request.mentor = mentor

    slack = app.plugins['slack'].api
    await request.update(slack)


async def add_skillset(action: Action, app: SirBot):
    selected_skill = MentorRequest.selected_option(action)
    request = MentorRequest(action['original_message'], action['channel']['id'])
    request.add_skillset(selected_skill)

    slack = app.plugins['slack'].api
    await request.update(slack)


async def claim_mentee(action: Action, app: SirBot):
    """
    Called when a mentor clicks on the button to claim a mentor request.

    Attempts to update airtable with the new request status and updates the claim
    button allowing it to be reset if needed.
    """
    try:
        slack = app.plugins['slack'].api
        airtable = app.plugins['airtable'].api

        update_airtable = True
        clicker_id = action['user']['id']
        request_record = action['actions'][0]['name']
        click_type = action['actions'][0]['value']

        response = base_response(action)

        user_info = await slack.query(methods.USERS_INFO, dict(user=clicker_id))
        clicker_email = user_info['user']['profile']['email']

        if click_type == 'mentee_claimed':
            records = await airtable.find_records(table_name='Mentors', field='Email', value=clicker_email)
            mentor_id = records[0]['id'] if records else ''

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

        await slack.query(methods.CHAT_UPDATE, response)
        if update_airtable:
            await airtable.update_request(request_record, mentor_id)
    except Exception as ex:
        print(ex)
