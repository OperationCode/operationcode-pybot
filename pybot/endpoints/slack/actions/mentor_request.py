import json
import logging

from sirbot import SirBot
from slack import methods
from slack.actions import Action

from pybot.endpoints.slack.message_templates.mentor_request import (
    MentorRequest,
    MentorRequestClaim,
)
from pybot.endpoints.slack.utils.action_messages import mentor_details_dialog

logger = logging.getLogger(__name__)


async def mentor_request_submit(action: Action, app: SirBot):
    slack = app.plugins["slack"].api
    airtable = app.plugins["airtable"].api
    request = MentorRequest(action)

    if not request.validate_self():
        await request.update_message(slack)
        return

    username = action["user"]["name"]
    user_info = await slack.query(methods.USERS_INFO, {"user": action["user"]["id"]})
    email = user_info["user"]["profile"]["email"]

    # Submission disabled for testing the rest of the workflow in prod

    # airtable_response = await request.submit_request(username, email, airtable)
    #
    # if "error" in airtable_response:
    #     await request.submission_error(airtable_response, slack)
    # else:
    #     await request.submission_complete(slack)


async def cancel_mentor_request(action: Action, app: SirBot):
    response = {"ts": action["message_ts"], "channel": action["channel"]["id"]}
    await app.plugins["slack"].api.query(methods.CHAT_DELETE, response)


async def mentor_details_submit(action: Action, app: SirBot):
    slack = app.plugins["slack"].api
    request = MentorRequest(action)

    state = json.loads(action["state"])
    channel = state["channel"]
    ts = state["ts"]
    search = {"inclusive": True, "channel": channel, "oldest": ts, "latest": ts}

    history = await slack.query(methods.IM_HISTORY, search)
    request["original_message"] = history["messages"][0]
    request.details = action["submission"]["details"]

    await request.update_message(slack)


async def open_details_dialog(action: Action, app: SirBot):
    trigger_id = action["trigger_id"]
    response = {"trigger_id": trigger_id, "dialog": mentor_details_dialog(action)}
    await app.plugins["slack"].api.query(methods.DIALOG_OPEN, response)


async def clear_skillsets(action: Action, app: SirBot):
    request = MentorRequest(action)
    request.clear_skillsets()

    slack = app.plugins["slack"].api
    await request.update_message(slack)


async def set_group(action: Action, app: SirBot):
    group = MentorRequest.selected_option(action)
    request = MentorRequest(action)
    request.certify_group = group

    slack = app.plugins["slack"].api
    await request.update_message(slack)


async def set_requested_service(action: Action, app: SirBot):
    request = MentorRequest(action)

    service = MentorRequest.selected_option(action)
    request.service = service

    slack = app.plugins["slack"].api
    await request.update_message(slack)


async def set_requested_mentor(action: Action, app: SirBot):
    mentor = MentorRequest.selected_option(action)
    request = MentorRequest(action)
    request.mentor = mentor

    slack = app.plugins["slack"].api
    await request.update_message(slack)


async def add_skillset(action: Action, app: SirBot):
    selected_skill = MentorRequest.selected_option(action)
    request = MentorRequest(action)
    request.add_skillset(selected_skill)

    slack = app.plugins["slack"].api
    await request.update_message(slack)


async def claim_mentee(action: Action, app: SirBot):
    """
    Called when a mentor clicks on the button to claim a mentor request.

    Attempts to update airtable with the new request status and updates the claim
    button allowing it to be reset if needed.
    """
    try:
        slack = app.plugins["slack"].api
        airtable = app.plugins["airtable"].api

        event = MentorRequestClaim(action, slack, airtable)
        if event.is_claim():
            user_info = await slack.query(methods.USERS_INFO, {"user": event.clicker})
            clicker_email = user_info["user"]["profile"]["email"]

            mentor_records = await airtable.find_records(
                table_name="Mentors", field="Email", value=clicker_email
            )
            mentor_id = mentor_records[0]["id"] if mentor_records else False

            await event.claim_request(mentor_id)
        else:
            await event.unclaim_request()

        await event.update_message()

    except Exception as ex:
        logger.exception("Exception while updating claim", ex)
