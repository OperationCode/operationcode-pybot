import json
import logging

from pybot._vendor.sirbot import SirBot
from pybot._vendor.slack import methods
from pybot._vendor.slack.actions import Action

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
        request.add_errors()
        await request.update_message(slack)
        return

    username = action["user"]["name"]
    user_info = await slack.query(methods.USERS_INFO, {"user": action["user"]["id"]})
    email = user_info["user"]["profile"]["email"]

    airtable_response = await request.submit_request(username, email, airtable)

    if "error" in airtable_response:
        await request.submission_error(airtable_response, slack)
    else:
        await request.submission_complete(slack)


async def mentor_details_submit(action: Action, app: SirBot):
    slack = app.plugins["slack"].api
    request = MentorRequest(action)

    state = json.loads(action["state"])
    channel = state["channel"]
    ts = state["ts"]
    search = {"inclusive": True, "channel": channel, "oldest": ts, "latest": ts}

    history = await slack.query(methods.CONVERSATIONS_HISTORY, search)
    request["message"] = history["messages"][0]
    request.details = action["submission"]["details"]

    await request.update_message(slack)


async def open_details_dialog(action: Action, app: SirBot):
    request = MentorRequest(action)
    cur_details = request.details
    trigger_id = action["trigger_id"]
    response = {
        "trigger_id": trigger_id,
        "dialog": mentor_details_dialog(action, cur_details),
    }
    await app.plugins["slack"].api.query(methods.DIALOG_OPEN, response)


async def clear_skillsets(action: Action, app: SirBot):
    request = MentorRequest(action)
    request.clear_skillsets()

    slack = app.plugins["slack"].api
    await request.update_message(slack)


async def clear_mentor(action: Action, app: SirBot):
    slack = app.plugins["slack"].api

    request = MentorRequest(action)
    request.mentor = ""

    await request.update_message(slack)


async def set_group(action: Action, app: SirBot):
    request = MentorRequest(action)
    request.affiliation = request.selected_option

    slack = app.plugins["slack"].api
    await request.update_message(slack)


async def set_requested_service(action: Action, app: SirBot):
    request = MentorRequest(action)

    request.service = request.selected_option

    slack = app.plugins["slack"].api
    await request.update_message(slack)


async def set_requested_mentor(action: Action, app: SirBot):
    request = MentorRequest(action)
    request.mentor = request.selected_option

    slack = app.plugins["slack"].api
    await request.update_message(slack)


async def add_skillset(action: Action, app: SirBot):
    request = MentorRequest(action)
    selected_skill = request.selected_option
    request.add_skillset(selected_skill["value"])

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
