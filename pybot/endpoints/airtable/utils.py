import logging

from pybot._vendor.sirbot import SirBot
from pybot._vendor.slack import ROOT_URL, methods
from pybot._vendor.slack.events import Message
from pybot._vendor.slack.exceptions import SlackAPIError
from pybot._vendor.slack.io.aiohttp import SlackAPI
from pybot.endpoints.slack.utils import MENTOR_CHANNEL
from pybot.plugins.airtable.api import AirtableAPI

from .message_templates.messages import claim_mentee_attachment, mentor_request_text

logger = logging.getLogger(__name__)


async def _get_requested_mentor(
    requested_mentor: str | None, slack: SlackAPI, airtable: AirtableAPI
) -> str | None:
    try:
        if not requested_mentor:
            return None
        mentor = await airtable.get_row_from_record_id("Mentors", requested_mentor)
        # mentor could be {} if the record wasn't found or an error occurred
        email = mentor.get("Email")
        if not email:
            return None
        slack_user_id = await _slack_user_id_from_email(email, slack)
        return f" Requested mentor: <@{slack_user_id}>"
    except SlackAPIError:
        return None


async def _slack_user_id_from_email(
    email: str, slack: SlackAPI, fallback: str | None = None
) -> str:
    try:
        response = await slack.query(url=ROOT_URL + "users.lookupByEmail", data={"email": email})
        return response["user"]["id"]
    except SlackAPIError:
        return fallback or "Slack User"


async def _get_matching_skillset_mentors(
    skillsets: str, slack: SlackAPI, airtable: AirtableAPI
) -> list[str]:
    if not skillsets:
        return ["No skillset Given"]
    mentors = await airtable.find_mentors_with_matching_skillsets(skillsets)
    mentor_ids = []
    for mentor in mentors:
        email = mentor.get("Email")
        fallback = mentor.get("Slack Name", "Unknown Mentor")
        if email:
            mentor_id = await _slack_user_id_from_email(email, slack, fallback=fallback)
            mentor_ids.append(mentor_id)
        elif fallback:
            mentor_ids.append(fallback)
    return [f"<@{mentor}>" for mentor in mentor_ids]


def _create_messages(
    mentors: list[str],
    request: dict,
    requested_mentor_message: str,
    service_translation: str,
    slack_id: str,
) -> tuple[dict, dict, dict]:
    first_message = {
        "text": mentor_request_text(
            slack_id,
            service_translation,
            request.get("skillsets", None),
            request.get("affiliation", "None Provided"),
            requested_mentor_message,
        ),
        "attachments": claim_mentee_attachment(request["record"]),
        "channel": MENTOR_CHANNEL,
    }

    details_message = {
        "text": f"Additional details: {request.get('details', 'None Given')}",
        "channel": MENTOR_CHANNEL,
    }

    matching_mentors_message = {
        "text": "Mentors matching all or some of the requested skillsets: " + " ".join(mentors),
        "channel": MENTOR_CHANNEL,
    }

    return first_message, details_message, matching_mentors_message


async def _post_messages(parent: Message, children: list[Message], app: SirBot) -> None:
    response = await app.plugins["slack"].api.query(url=methods.CHAT_POST_MESSAGE, data=parent)

    # Safely get timestamp from response - if missing, children won't be threaded
    timestamp = response.get("ts")
    if not timestamp:
        logger.warning("Slack response missing 'ts' field - children messages will not be threaded")
        return

    for child in children:
        child["thread_ts"] = timestamp
        await app.plugins["slack"].api.query(url=methods.CHAT_POST_MESSAGE, data=child)
