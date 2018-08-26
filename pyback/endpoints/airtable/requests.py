from sirbot import SirBot
import asyncio
import logging

from pyback.endpoints.airtable.utils import (_create_messages, _get_matching_skillset_mentors, _get_requested_mentor,
                                             _post_messages, _slack_user_id_from_email)

logger = logging.getLogger(__name__)


def create_endpoints(plugin):
    plugin.on_request('mentor_request', mentor_request)


async def mentor_request(request: dict, app: SirBot) -> None:
    slack_id = await _slack_user_id_from_email(request['email'], app)

    futures = [app.plugins['airtable'].api.translate_service_id(request['service']),
               _get_requested_mentor(request['requested_mentor'], app),
               _get_matching_skillset_mentors(request['skillsets'], app)]

    service_translation, requested_mentor_message, mentors = await asyncio.gather(*futures)

    first_message, *children = _create_messages(mentors, request, requested_mentor_message, service_translation,
                                                slack_id)

    await _post_messages(first_message, children, app)
