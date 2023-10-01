import logging
from slack_bolt.async_app import AsyncApp

logger = logging.getLogger(__name__)


async def post_daily_programmer_message(async_app: AsyncApp) -> None:
    logger.info("STAGE: Beginning task post_daily_programmer_message...")
