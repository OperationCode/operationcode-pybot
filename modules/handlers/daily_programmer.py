import re
import logging
from typing import Optional, Union
from datetime import datetime, timezone
from difflib import SequenceMatcher
from slack_bolt.context.async_context import AsyncBoltContext

from modules.airtable import daily_programmer_table
from modules.models.slack_models.event_models import MessageReceivedChannelEvent
from modules.models.slack_models.shared_models import SlackMessageInfo

logger = logging.getLogger(__name__)


async def handle_daily_programmer_post(
    parsed_body: MessageReceivedChannelEvent, context: AsyncBoltContext
) -> None:
    await context.ack()
    logger.info("STAGE: Handling a daily programmer post...")
    post_id, post_count = check_for_existing_post(parsed_body.event.text)
    if post_id and post_count:
        daily_programmer_table.update(
            post_id,
            {"Post Count": post_count, "Last Posted On": datetime.now(timezone.utc)},
        )
        return None
    process_daily_programmer_post_text(parsed_body.event)


def check_for_existing_post(text: str) -> Union[tuple[str, int], tuple[None, None]]:
    existing_posts = daily_programmer_table.all(
        view="Valid", fields=["Text", "Posted Count"]
    )
    for post in existing_posts:
        if SequenceMatcher(None, post["fields"]["Text"], text).ratio() > 0.85:
            logger.debug(f"Found matching post: {post}")
            return post["id"], int(post["fields"]["Posted Count"])
    return None, None


def process_daily_programmer_post_text(body: SlackMessageInfo) -> None:
    logger.info("STAGE: Processing a daily programmer post text...")
    title = re.search(r"(={2,3}.*={2,3})", body.text)
    if title:
        name = re.search(r"(\[.*?])", body.text)
        if name:
            try:
                daily_programmer_table.create_record(
                    {
                        "Name": name[0]
                        .replace("[", "")
                        .replace("]", "")
                        .replace("*", ""),
                        "Text": body.text[name.span()[1] + 1 :],
                        "Initially Posted On": str(
                            datetime.fromtimestamp(float(body.ts), timezone.utc)
                        ),
                        "Last Posted On": str(
                            datetime.fromtimestamp(float(body.ts), timezone.utc)
                        ),
                        "Posted Count": 1,
                        "Initial Slack TS": body.ts,
                        "Blocks": body.blocks,
                    }
                )
                return None
            except Exception as general_error:
                logger.exception(
                    f"Unable to create new daily programmer entry: {general_error}"
                )
        logger.warning(
            f"Unable to create new daily programmer entry due to not finding the name..."
        )
        return None
    logger.warning(
        f"Unable to create new daily programmer entry due to not finding the title..."
    )
    return None
