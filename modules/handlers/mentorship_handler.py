import logging  # noqa: D100
from datetime import datetime, timezone
from typing import Any

from slack_bolt.context.async_context import AsyncBoltContext

from modules.airtable import (
    mentor_table,
    mentorship_affiliations_table,
    mentorship_requests_table,
    mentorship_services_table,
    mentorship_skillsets_table,
)
from modules.models.greeting_models import UserInfo
from modules.models.mentorship_models import MentorshipRequestCreate
from modules.models.slack_models.action_models import SlackActionRequestBody
from modules.models.slack_models.command_models import SlackCommandRequestBody
from modules.models.slack_models.view_models import SlackViewRequestBody
from modules.slack.blocks.mentorship_blocks import (
    mentorship_request_view,
    request_claim_blocks,
    request_claim_button,
    request_claim_details_block,
    request_claim_reset_button,
    request_claim_tagged_users_block,
    request_successful_block,
    request_unsuccessful_block,
)
from modules.utils import get_slack_user_by_id, log_to_thread, slack_team

logger = logging.getLogger(__name__)


async def handle_mentor_request(  # noqa: D103
    parsed_body: SlackCommandRequestBody,
    context: AsyncBoltContext,
) -> None:
    logging.info("STAGE: Handling the mentor request...")
    await context.ack()
    response = await context.client.views_open(
        trigger_id=parsed_body.trigger_id,
        view=mentorship_request_view(
            services=mentorship_services_table.valid_services,
            skillsets=mentorship_skillsets_table.valid_skillsets,
            affiliations=mentorship_affiliations_table.valid_affiliations,
        ),
    )
    if response["ok"]:
        logger.debug("View opened successfully")

    else:
        logger.warning(f"Unable to open the view, given response: {response}")  # noqa: G004


async def handle_mentorship_request_form_submit(  # noqa: D103
    parsed_body: SlackViewRequestBody,
    context: AsyncBoltContext,
) -> None:
    logger.info("STAGE: Handling the mentorship request form submission...")
    await context.ack()
    try:
        slack_user_info = await get_slack_user_by_id(
            context.client,
            parsed_body.user.id,
        )
        mentorship_request, airtable_record = create_mentor_request_record(
            parsed_body,
            slack_user_info,
        )
        mentors_channel_response = await context.client.chat_postMessage(
            channel=slack_team.mentors_internal_channel.id,
            blocks=request_claim_blocks(
                mentorship_request.service,
                mentorship_request.skillsets_requested,
                mentorship_request.affiliation
                if isinstance(mentorship_request.affiliation, str)
                else mentorship_request.affiliation[0],
                mentorship_request.slack_name,
            ),
            text="New mentorship request received...",
        )
        mentorship_requests_table.update_record(
            airtable_id=airtable_record["id"],
            fields_to_update={"Slack Message TS": mentors_channel_response["ts"]},
        )
        await context.client.chat_postMessage(
            channel=slack_team.mentors_internal_channel.id,
            thread_ts=mentors_channel_response["ts"],
            text="Additional details added to mentorship request...",
            blocks=[request_claim_details_block(mentorship_request.additional_details)],
        )
        matching_mentors = mentorship_skillsets_table.mentors_by_skillset(
            mentorship_request.skillsets_requested,
        )
        retrieve_mentor_slack_names = [
            mentor.slack_name for mentor in mentor_table.valid_mentors if mentor.airtable_id in matching_mentors
        ]
        await context.client.chat_postMessage(
            channel=slack_team.mentors_internal_channel.id,
            thread_ts=mentors_channel_response["ts"],
            text="Tagged users for mentorship request...",
            blocks=[request_claim_tagged_users_block(retrieve_mentor_slack_names)],
            link_names=True,
        )
        await context.client.chat_postEphemeral(
            channel=parsed_body.user.id,
            user=parsed_body.user.id,
            text="Successfully sent mentorship request...",
            blocks=[request_successful_block()],
        )
    except Exception as general_exception:
        logger.exception(
            f"Unable to create the mentorship request record due to error: {general_exception}",  # noqa: TRY401, G004
        )
        await context.client.chat_postEphemeral(
            channel=parsed_body.user.id,
            user=parsed_body.user.id,
            text="Mentorship request was unsuccessful...",
            blocks=[request_unsuccessful_block()],
        )


async def handle_mentorship_request_claim(
    parsed_body: SlackActionRequestBody,
    context: AsyncBoltContext,
) -> None:
    """Handle a mentorship request claim submission from Slack.

    :param parsed_body: The parsed body of the Slack request.
    :param context: The context object for the Slack request.
    """
    logger.info("STAGE: Handling mentorship request claim...")
    await context.ack()
    blocks = parsed_body.message.blocks
    blocks[-1] = request_claim_reset_button(parsed_body.user.username)
    request_record = mentorship_requests_table.return_record_by_slack_message_ts(
        timestamp=str(parsed_body.message.ts),
    )
    mentorship_requests_table.update_record(
        airtable_id=request_record.airtable_id,
        fields_to_update={
            "Claimed": "true",
            "Claimed By": parsed_body.user.username,
            "Claimed On": str(datetime.now(timezone.utc)),
            "Reset By": "",
        },
    )
    await log_to_thread(
        client=context.client,
        channel_id=parsed_body.channel.id,
        message_ts=parsed_body.message.ts,
        username=parsed_body.user.username,
        action_ts=parsed_body.actions[0].action_ts,
        claim=True,
    )
    await context.respond(
        text="Someone claimed the mentorship request...",
        blocks=blocks,
        replace_original=True,
    )


async def handle_mentorship_request_claim_reset(  # noqa: D103
    parsed_body: SlackActionRequestBody,
    context: AsyncBoltContext,
) -> None:
    logger.info("STAGE: Handling mentorship request claim reset...")
    await context.ack()
    blocks = parsed_body.message.blocks
    blocks[-1] = request_claim_button()
    request_record = mentorship_requests_table.return_record_by_slack_message_ts(
        timestamp=parsed_body.message.ts,
    )
    mentorship_requests_table.update_record(
        airtable_id=request_record.airtable_id,
        fields_to_update={
            "Claimed": "false",
            "Claimed By": "",
            "Reset By": parsed_body.user.username,
            "Reset On": str(datetime.now(timezone.utc)),
            "Reset Count": int(request_record.reset_count) + 1,
        },
    )
    await log_to_thread(
        client=context.client,
        channel_id=parsed_body.channel.id,
        message_ts=parsed_body.message.ts,
        username=parsed_body.user.username,
        action_ts=parsed_body.actions[0].action_ts,
        claim=False,
    )
    await context.respond(
        text="Someone reset the claimed mentorship request...",
        blocks=blocks,
        replace_original=True,
    )


def create_mentor_request_record(  # noqa: D103
    parsed_body: SlackViewRequestBody,
    slack_user_info: UserInfo,
) -> tuple[MentorshipRequestCreate, dict[str, Any]]:
    logger.info("STAGE: Creating the mentorship request record...")
    try:
        mentorship_request = MentorshipRequestCreate(
            slack_name=slack_user_info.name,
            email=slack_user_info.email,
            service=parsed_body.view.state["values"]["mentorship_service_input"]["mentorship_service_selection"][
                "selected_option"
            ]["value"],
            additional_details=parsed_body.view.state["values"]["details_input_block"]["details_text_input"]["value"],
            skillsets_requested=[
                skill["value"]
                for skill in parsed_body.view.state["values"]["mentor_skillset_input"][
                    "mentorship_skillset_multi_selection"
                ]["selected_options"]
            ],
            affiliation=parsed_body.view.state["values"]["mentorship_affiliation_input"][
                "mentorship_affiliation_selection"
            ]["selected_option"]["text"]["text"],
        )
        modified_request = {k.title().replace("_", " "): v for k, v in mentorship_request.__dict__.items()}
        created_record = mentorship_requests_table.create_record(modified_request)
        return mentorship_request, created_record  # noqa: TRY300
    except Exception as exc:
        logger.exception(
            f"Unable to create the Airtable record for user: {slack_user_info.name} due to an exception",  # noqa: G004
            exc,  # noqa: TRY401
        )
        raise exc  # noqa: TRY201
