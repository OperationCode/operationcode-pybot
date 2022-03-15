import logging
from datetime import datetime, timedelta, timezone
from slack_bolt.async_app import AsyncApp

from modules.utils import slack_team
from modules.airtable import scheduled_message_table
from modules.slack.blocks.announcement_blocks import general_announcement_blocks

logger = logging.getLogger(__name__)


async def schedule_messages(async_app: AsyncApp) -> None:
    logger.info("STAGE: Beginning task schedule_messages...")
    messages = scheduled_message_table.all_valid_scheduled_messages
    logger.debug(f"Retrieved {len(messages)} total valid messages to be potentially be scheduled")
    for message in messages:
        if message.scheduled_next < datetime.now(tz=timezone.utc):
            logger.debug(f"Scheduling message {message.name}")
            if message.when_to_send < datetime.now(tz=timezone.utc):
                logger.debug(f"Scheduling message {message.name} to be sent immediately")
                send_message_timestamp = int(datetime.now(timezone.utc).timestamp()) + 240
                if message.frequency == "daily":
                    new_scheduled_next = datetime.now(timezone.utc) + timedelta(days=1)
                elif message.frequency == "weekly":
                    new_scheduled_next = datetime.now(timezone.utc) + timedelta(days=7)
                elif message.frequency == "monthly":
                    new_scheduled_next = datetime.now(timezone.utc) + timedelta(days=30)
            else:
                send_message_timestamp = int(message.when_to_send.timestamp())
                new_scheduled_next = message.when_to_send

            channel_to_send_to = slack_team.find_channel_by_name(message.channel)

            response = await async_app.client.chat_scheduleMessage(
                channel=channel_to_send_to.id,
                post_at=send_message_timestamp,
                text=f"Announcement in {message.channel}...",
                blocks=general_announcement_blocks(message.name, message.message_text),
            )
            if response.status_code == 200:
                logger.debug(
                    f"Updating the Airtable {scheduled_message_table.table_name} table for row with id: {message.airtable_id} with new value Scheduled Next: {new_scheduled_next}"
                )
                scheduled_message_table.update_record(
                    message.airtable_id,
                    {
                        "Scheduled Next": str(new_scheduled_next),
                    },
                )
            else:
                logger.warning(
                    f"Issue sending the scheduled message: {message.name}, scheduling failed with slack response: {response.__dict__}"
                )
