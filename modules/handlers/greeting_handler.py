import re
from typing import Any, Union
from datetime import datetime, timezone, timedelta
from slack_bolt.context.async_context import AsyncBoltContext

from modules.models.slack_models.action_models import SlackActionRequestBody
from modules.models.slack_models.command_models import SlackCommandRequestBody
from modules.models.slack_models.event_models import MemberJoinedChannelEvent
from modules.slack.blocks.new_join_blocks import (
    new_join_immediate_welcome_blocks,
    new_join_delayed_welcome_blocks,
)
from modules.utils import get_team_info, get_slack_user_by_id, log_to_thread, slack_team
from modules.slack.blocks.greeting_blocks import (
    initial_greet_user_blocks,
    greeting_block_claimed_button,
    greeting_block_button,
)


async def handle_new_member_join(
    parsed_body: Union[MemberJoinedChannelEvent, SlackCommandRequestBody], context: AsyncBoltContext
) -> None:
    await context.ack()
    user = None
    if isinstance(parsed_body, MemberJoinedChannelEvent):
        user = await get_slack_user_by_id(context.client, parsed_body.user)
    elif isinstance(parsed_body, SlackCommandRequestBody):
        user = await get_slack_user_by_id(context.client, parsed_body.user_id)
    await context.client.chat_postMessage(
        channel=slack_team.greetings_channel.id,
        blocks=initial_greet_user_blocks(user),
        text="A new member has joined!",
    )
    # Add one minute to the current timestamp
    immediate_message_timestamp = datetime.now(timezone.utc).timestamp() + 60
    await context.client.chat_scheduleMessage(
        channel=user.id,
        user=user.id,
        post_at=int(immediate_message_timestamp),
        text="Welcome to Operation Code Slack!",
        blocks=new_join_immediate_welcome_blocks(user.name),
        unfurl_links=False,
        unfurl_media=False,
    )
    # Schedule the delayed message for the next day at 1600 UTC (10 AM CST/CDT)
    # This could be in two days, by popular measure, if UTC has already rolled over midnight
    delayed_message_timestamp = (
        (datetime.now(timezone.utc) + timedelta(days=1))
        .replace(hour=16, minute=00)
        .timestamp()
    )
    await context.client.chat_scheduleMessage(
        channel=user.id,
        user=user.id,
        post_at=int(delayed_message_timestamp),
        text="We're happy to have you at Operation Code!",
        blocks=new_join_delayed_welcome_blocks(),
        unfurl_media=False,
        unfurl_links=False,
    )

async def handle_greeting_new_user_claim(
    parsed_body: SlackActionRequestBody,
    context: AsyncBoltContext,
) -> None:
    await context.ack()
    original_blocks = parsed_body.message.blocks
    original_blocks[-1] = greeting_block_claimed_button(parsed_body.user.username)
    modified_blocks = original_blocks
    await log_to_thread(
        client=context.client,
        channel_id=parsed_body.channel.id,
        message_ts=parsed_body.message.ts,
        username=parsed_body.user.username,
        action_ts=parsed_body.actions[0].action_ts,
        claim=True,
    )
    await context.respond(
        text="Modified the claim to greet the new user...",
        blocks=modified_blocks,
        replace_original=True,
    )


async def handle_resetting_greeting_new_user_claim(
    parsed_body: SlackActionRequestBody,
    context: AsyncBoltContext,
) -> None:
    await context.ack()
    original_blocks = parsed_body.message.blocks
    # Extract out the username of the new user (the user we are greeting)
    original_blocks[-1] = greeting_block_button(
        str(re.match(r"\((@.*)\)", parsed_body.message.blocks[0]['text']["text"]))
    )
    modified_blocks = original_blocks
    await log_to_thread(
        client=context.client,
        channel_id=parsed_body.channel.id,
        message_ts=parsed_body.message.ts,
        username=parsed_body.user.username,
        action_ts=parsed_body.actions[0].action_ts,
        claim=True,
    )
    await context.respond(
        text="Modified the claim to greet the new user...",
        blocks=modified_blocks,
        replace_original=True,
    )
