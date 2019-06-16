from enum import IntEnum

from sirbot import SirBot
from slack import methods
from slack.actions import Action

from pybot.endpoints.slack.message_templates.mentor_volunteer import MentorVolunteer
from pybot.endpoints.slack.utils import MENTOR_CHANNEL


class VolunteerBlockIndex(IntEnum):
    SKILLSET_OPTIONS = 2
    SELECTED_SKILLSETS = 3
    SUBMIT = 5


async def add_volunteer_skillset(action: Action, app: SirBot) -> None:
    slack = app.plugins["slack"].api

    request = MentorVolunteer(action)

    selected_skill = request.selected_option
    request.add_skillset(selected_skill["value"])
    await request.update_message(slack)


async def clear_volunteer_skillsets(action: Action, app: SirBot) -> None:
    slack = app.plugins["slack"].api

    request = MentorVolunteer(action)

    request.clear_skillsets()
    await request.update_message(slack)


async def submit_mentor_volunteer(action: Action, app: SirBot) -> None:
    slack = app.plugins["slack"].api
    admin_slack = app.plugins["admin_slack"].api
    airtable = app.plugins["airtable"].api
    bot_user_id = action["user"]["id"]

    request = MentorVolunteer(action)

    if not request.validate_self():
        request.add_errors()
        await request.update_message(slack)
        return

    user_id = action["user"]["id"]
    user_info = await slack.query(methods.USERS_INFO, {"user": user_id})
    airtable_fields = await build_airtable_fields(action, request, user_info)

    airtable_response = await airtable.add_record(
        "Mentors", {"fields": airtable_fields}
    )

    if "error" in airtable_response:
        request.airtable_error(airtable_response)
    else:

        # checks if the user submitting the form owns the admin token used for the bot
        # stops an exception being being raised if a user tries to invite themselves to a channel
        if bot_user_id != user_id:
            await admin_slack.query(
                methods.CONVERSATIONS_INVITE,
                {"channel": MENTOR_CHANNEL, "users": [user_id]},
            )
        request.on_submit_success()

    await request.update_message(slack)


async def build_airtable_fields(action, request, user_info):
    username = action["user"]["name"]
    email = user_info["user"]["profile"]["email"]
    name = user_info["user"]["real_name"]
    airtable_fields = {
        "Slack Name": username,
        "Full Name": name,
        "Skillsets": request.skillsets,
        "Email": email,
    }
    return airtable_fields
