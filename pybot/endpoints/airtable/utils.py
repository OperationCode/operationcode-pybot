import os
from typing import List, Optional, Tuple

from sirbot import SirBot
from slack import ROOT_URL, methods
from slack.events import Message
from slack.exceptions import SlackAPIError

from pybot.endpoints.airtable.messages import (claim_mentee_attachment,
                                               mentor_request_text)

MENTORS_CHANNEL = os.environ.get("MENTORS_CHANNEL") or "G1DRT62UC"


async def _get_requested_mentor(requested_mentor: Optional[str], app: SirBot) -> Optional[str]:
    try:
        if not requested_mentor:
            return None
        mentor = await app.plugins['airtable'].api.get_mentor_from_record_id(requested_mentor)
        email = mentor['Email']
        slack_user_id = await _slack_user_id_from_email(email, app)
        return f" Requested mentor: <@{slack_user_id}>"
    except SlackAPIError:
        return None


async def _slack_user_id_from_email(email: str, app: SirBot, fallback: Optional[str] = None) -> str:
    response = Message()
    response['email'] = email
    try:
        response = await app.plugins['slack'].api.query(url=ROOT_URL + 'users.lookupByEmail', data=response)
        return response['user']['id']
    except SlackAPIError:
        # TODO: something better here
        return fallback or 'Slack User'


async def _get_matching_skillset_mentors(skillsets: str, app: SirBot) -> List[str]:
    if not skillsets:
        return ['No skillset Given']
    mentors = await app.plugins['airtable'].api.find_mentors_with_matching_skillsets(skillsets)
    mentor_ids = [await _slack_user_id_from_email(mentor['Email'], app, fallback=mentor['Slack Name']) for mentor in
                  mentors]
    return [f'<@{mentor}>' for mentor in mentor_ids]


def _create_messages(mentors: List[str], request: dict, requested_mentor_message: str, service_translation: str,
                     slack_id: str) -> Tuple[Message, Message, Message]:
    first_message = Message()
    first_message['text'] = mentor_request_text(slack_id, service_translation, request.get('skillsets', None),
                                                requested_mentor_message)
    first_message['attachments'] = claim_mentee_attachment(request['record'])
    first_message['channel'] = MENTORS_CHANNEL
    details_message = Message()
    details_message['text'] = f"Additional details: {request.get('details', 'None Given')}"
    details_message['channel'] = MENTORS_CHANNEL
    matching_mentors_message = Message()
    matching_mentors_message['text'] = "Mentors matching all or some of the requested skillsets: " + ' '.join(mentors)
    matching_mentors_message['channel'] = MENTORS_CHANNEL
    return first_message, details_message, matching_mentors_message


async def _post_messages(parent: Message, children: List[Message], app: SirBot) -> None:
    response = await app.plugins['slack'].api.query(url=methods.CHAT_POST_MESSAGE, data=parent)
    timestamp = response['ts']

    for child in children:
        child['thread_ts'] = timestamp
        await app.plugins['slack'].api.query(url=methods.CHAT_POST_MESSAGE, data=child)
