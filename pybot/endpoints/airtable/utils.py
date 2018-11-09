import os
from typing import List, Optional, Tuple

from sirbot import SirBot
from slack import ROOT_URL, methods
from slack.events import Message
from slack.exceptions import SlackAPIError
from slack.io.aiohttp import SlackAPI
from pybot.plugins.airtable.api import AirtableAPI
from pybot.endpoints.slack.utils import MENTOR_CHANNEL
from .message_templates.messages import claim_mentee_attachment, mentor_request_text


async def _get_requested_mentor(requested_mentor: Optional[str], slack: SlackAPI,
                                airtable: AirtableAPI) -> Optional[str]:
    try:
        if not requested_mentor:
            return None
        mentor = await airtable.get_mentor_from_record_id(requested_mentor)
        email = mentor['Email']
        slack_user_id = await _slack_user_id_from_email(email, slack)
        return f" Requested mentor: <@{slack_user_id}>"
    except SlackAPIError:
        return None


async def _slack_user_id_from_email(email: str, slack: SlackAPI, fallback: Optional[str] = None) -> str:
    try:
        response = await slack.query(url=ROOT_URL + 'users.lookupByEmail', data={'email': email})
        return response['user']['id']
    except SlackAPIError:
        # TODO: something better here
        return fallback or 'Slack User'


async def _get_matching_skillset_mentors(skillsets: str, slack: SlackAPI, airtable: AirtableAPI) -> List[str]:
    if not skillsets:
        return ['No skillset Given']
    mentors = await airtable.find_mentors_with_matching_skillsets(skillsets)
    mentor_ids = [await _slack_user_id_from_email(mentor['Email'], slack, fallback=mentor['Slack Name']) for mentor in
                  mentors]
    return [f'<@{mentor}>' for mentor in mentor_ids]


def _create_messages(mentors: List[str], request: dict, requested_mentor_message: str, service_translation: str,
                     slack_id: str) -> Tuple[dict, dict, dict]:
    first_message = {
        'text': mentor_request_text(slack_id, service_translation, request.get('skillsets', None),
                                    requested_mentor_message),
        'attachments': claim_mentee_attachment(request['record']),
        'channel': MENTOR_CHANNEL
    }

    details_message = {
        'text': f"Additional details: {request.get('details', 'None Given')}",
        'channel': MENTOR_CHANNEL
    }

    matching_mentors_message = {
        'text': "Mentors matching all or some of the requested skillsets: " + ' '.join(mentors),
        'channel': MENTOR_CHANNEL
    }

    return first_message, details_message, matching_mentors_message


async def _post_messages(parent: Message, children: List[Message], app: SirBot) -> None:
    response = await app.plugins['slack'].api.query(url=methods.CHAT_POST_MESSAGE, data=parent)
    timestamp = response['ts']

    for child in children:
        child['thread_ts'] = timestamp
        await app.plugins['slack'].api.query(url=methods.CHAT_POST_MESSAGE, data=child)
