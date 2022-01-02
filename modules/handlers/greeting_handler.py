import re
from typing import Any
from datetime import datetime, timezone, timedelta
from slack_bolt.context.async_context import AsyncBoltContext

from modules.models.slack_models.event_models import MemberJoinedChannelEvent
from modules.slack.blocks.new_join_blocks import (
    new_join_immediate_welcome_blocks,
    new_join_delayed_welcome_blocks,
)
from modules.utils import get_team_info, get_slack_user_by_id, log_to_thread
from modules.slack.blocks.greeting_blocks import (
    initial_greet_user_blocks,
    greeting_block_claimed_button,
    greeting_block_button,
)


async def handle_new_member_join(
    parsed_body: MemberJoinedChannelEvent, context: AsyncBoltContext
) -> None:
    await context.ack()
    slack_team = get_team_info()
    user = await get_slack_user_by_id(context.client, parsed_body.user)
    await context.client.chat_postMessage(
        channel=slack_team.greetings_channel.id,
        blocks=initial_greet_user_blocks(user),
        text="A new member has joined!",
    )
    user_info = await context.client.users_info(user=parsed_body.user)
    # Add one minute to the current timestamp
    immediate_message_timestamp = datetime.now(timezone.utc).timestamp() + 60
    await context.client.chat_scheduleMessage(
        channel=parsed_body.user,
        user=parsed_body.user,
        post_at=int(immediate_message_timestamp),
        text="Welcome to Operation Code Slack!",
        blocks=new_join_immediate_welcome_blocks(user_info["body"]["name"]),
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
        channel=parsed_body.user,
        user=parsed_body.user,
        post_at=int(delayed_message_timestamp),
        text="We're happy to have you at Operation Code!",
        blocks=new_join_delayed_welcome_blocks(),
        unfurl_media=False,
        unfurl_links=False,
    )


async def handle_greeting_new_user_claim(
    body: dict[str, Any],
    context: AsyncBoltContext,
) -> None:
    await context.ack()
    original_blocks = body["message"]["blocks"]
    original_blocks[-1] = greeting_block_claimed_button(body["user"]["username"])
    modified_blocks = original_blocks
    await log_to_thread(context.client, body, claim=True)
    await context.respond(
        text="Modified the claim to greet the new user...",
        blocks=modified_blocks,
        replace_original=True,
    )


async def handle_resetting_greeting_new_user_claim(
    body: dict[str, Any],
    context: AsyncBoltContext,
) -> None:
    await context.ack()
    original_blocks = body["message"]["blocks"]
    # Extract out the username of the new user (the user we are greeting)
    original_blocks[-1] = greeting_block_button(
        str(re.match(r"\((@.*)\)", body["message"]["blocks"][0]["text"]["text"]))
    )
    modified_blocks = original_blocks
    await log_to_thread(context.client, body, claim=False)
    await context.respond(
        text="Modified the claim to greet the new user...",
        blocks=modified_blocks,
        replace_original=True,
    )
