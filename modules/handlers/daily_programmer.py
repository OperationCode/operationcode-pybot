"""Handles the daily programmer channel."""
import logging
import re
from datetime import datetime, timezone
from difflib import SequenceMatcher

from slack_bolt.context.async_context import AsyncBoltContext

from modules.airtable import daily_programmer_table
from modules.models.slack_models.event_models import MessageReceivedChannelEvent
from modules.models.slack_models.shared_models import SlackMessageInfo

LOGGER = logging.getLogger(__name__)
MATCHING_TEXT_RATIO = 0.85


async def handle_daily_programmer_post(
    parsed_body: MessageReceivedChannelEvent,
    context: AsyncBoltContext,
) -> None:
    """Process a message that was posted to the daily programmer channel.

    :param parsed_body: The parsed body of the Slack message event.
    :param context: The Slack Bolt context.
    """
    await context.ack()
    LOGGER.info("STAGE: Handling a daily programmer post...")
    post_id, post_count = check_for_existing_post(parsed_body.event.text)
    if post_id and post_count:
        daily_programmer_table.update(
            post_id,
            {"Post Count": post_count, "Last Posted On": datetime.now(timezone.utc)},
        )
        return None  # noqa: RET501
    process_daily_programmer_post_text(parsed_body.event)


def check_for_existing_post(text: str) -> tuple[str, int] | tuple[None, None]:
    """Check for an existing daily programmer post.

    :param text: The text of the post.
    :return: The existing post ID and the number of times it has been posted, if it exists.
    """
    existing_posts = daily_programmer_table.all(
        view="Valid",
        fields=["Text", "Posted Count"],
    )
    for post in existing_posts:
        if SequenceMatcher(None, post["fields"]["Text"], text).ratio() > MATCHING_TEXT_RATIO:
            LOGGER.info("Found matching post", extra={"post": post})
            return post["id"], int(post["fields"]["Posted Count"])
    return None, None


def process_daily_programmer_post_text(body: SlackMessageInfo) -> None:
    """Process a post to the daily programming channel.

    :param body: The body of the Slack message.
    """
    LOGGER.info("STAGE: Processing a daily programmer post text...")
    # Posts to the daily programmer channel should be in the format:
    # ==[Name]==
    title = re.search(r"(={2,3}.*={2,3})", body.text)
    if title:
        LOGGER.info("Found a daily programmer post title...")
        name = re.search(r"(\[.*?])", body.text)
        if name:
            try:
                daily_programmer_table.create_record(
                    {
                        "Name": name[0].replace("[", "").replace("]", "").replace("*", ""),
                        "Text": body.text[name.span()[1] + 1 :],
                        "Initially Posted On": str(
                            datetime.fromtimestamp(float(body.ts), timezone.utc),
                        ),
                        "Last Posted On": str(
                            datetime.fromtimestamp(float(body.ts), timezone.utc),
                        ),
                        "Posted Count": 1,
                        "Initial Slack TS": body.ts,
                        "Blocks": body.blocks,
                    },
                )
            except Exception as general_error:
                LOGGER.exception(
                    "Unable to create new daily programmer entry",
                )
                raise general_error from general_error
            return
        LOGGER.warning(
            "Unable to create new daily programmer entry due to not finding the name...",
        )
        return
    LOGGER.warning(
        "Unable to create new daily programmer entry due to not finding the title...",
    )
