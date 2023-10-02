import logging  # noqa: D100
from typing import Any

from slack_bolt.context.async_context import AsyncBoltContext

from modules.models.slack_models.shared_models import SlackUserInfo
from modules.models.slack_models.slack_models import SlackResponseBody
from modules.slack.blocks.report_blocks import (
    report_claim_blocks,
    report_claim_button,
    report_claim_claimed_button,
    report_failed_ephemeral_message,
    report_form_view_elements,
    report_received_ephemeral_message,
)
from modules.utils import get_team_info, log_to_thread

logger = logging.getLogger(__name__)


async def handle_report(body: dict[str, Any], context: AsyncBoltContext) -> None:  # noqa: D103
    await context.ack()
    await context.client.views_open(
        trigger_id=body["trigger_id"],
        view=report_form_view_elements(),
    )


async def handle_report_submit(body: dict[str, Any], context: AsyncBoltContext) -> None:  # noqa: D103
    await context.ack()
    slack_team = get_team_info()
    logger.debug(f"Parsing received body: {body}")  # noqa: G004
    parsed_body = SlackResponseBody(
        **body,
        originating_user=SlackUserInfo(**body["user"]),
    )
    response = await context.client.chat_postMessage(
        channel=slack_team.moderators_channel.id,
        blocks=report_claim_blocks(
            parsed_body.originating_user.username,
            parsed_body.view.state["values"]["report_input"]["report_input_field"]["value"],
        ),
        text="New report submitted...",
    )
    if response.data["ok"]:
        await context.client.chat_postEphemeral(
            channel=parsed_body.originating_user.id,
            text="Successfully sent report to moderators...",
            blocks=[report_received_ephemeral_message()],
            user=parsed_body.originating_user.id,
        )
    else:
        await context.client.chat_postEphemeral(
            channel=parsed_body.originating_user.id,
            text="There was an issue sending your report...",
            blocks=[report_failed_ephemeral_message()],
            user=parsed_body.originating_user.id,
        )


async def handle_report_claim(  # noqa: D103
    body: SlackResponseBody,
    context: AsyncBoltContext,
) -> None:
    await context.ack()
    blocks = body.message.blocks
    blocks[-1] = report_claim_claimed_button(body.originating_user.username)
    await log_to_thread(
        client=context.client,
        channel_id=body.channel.id,
        message_ts=body.message.ts,
        username=body.originating_user.username,
        action_ts=body.actions[0].action_ts,
        claim=True,
    )
    await context.respond(
        text="Modified the claim to reach out about the report...",
        blocks=blocks,
        replace_original=True,
    )


async def handle_reset_report_claim(  # noqa: D103
    body: SlackResponseBody,
    context: AsyncBoltContext,
) -> None:
    await context.ack()
    blocks = body.message.blocks
    blocks[-1] = report_claim_button()
    await log_to_thread(
        client=context.client,
        channel_id=body.channel.id,
        message_ts=body.message.ts,
        username=body.originating_user.username,
        action_ts=body.actions[0].action_ts,
        claim=False,
    )
    await context.respond(
        text="Modified the claim to reach out about the report...",
        blocks=blocks,
        replace_original=True,
    )
