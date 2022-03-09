import logging
from slack_bolt.context.async_context import AsyncBoltContext

logger = logging.getLogger(__name__)


async def handle_daily_programmer_post(parsed_body, context: AsyncBoltContext) -> None:
    logger.info("STAGE: Beginning task populate_daily_programmer_table...")
    logger.debug(f"Received body: {parsed_body}")
