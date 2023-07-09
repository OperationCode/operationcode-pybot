"""Module for scheduling messages in a background job."""
import logging
from datetime import datetime, timedelta, timezone

from slack_bolt.async_app import AsyncApp
from starlette import status

from modules.airtable import scheduled_message_table
from modules.slack.blocks.announcement_blocks import general_announcement_blocks
from modules.utils import slack_team

logger = logging.getLogger(__name__)

TOTAL_MONTHS_IN_YEAR = 12


async def schedule_messages(async_app: AsyncApp) -> None:
    """Schedule messages to be sent to various channels.

    Pulls the messages from the Airtable table Scheduled Messages
    As explained in the comments below, will schedule messages using the `when_to-send` field on the table,
    which is calculated by Airtable based on the frequency and `scheduled_next` datetime.

    :param async_app: the Slack Bolt async application.
    """
    logger.info("STAGE: Beginning task schedule_messages...")
    messages = scheduled_message_table.all_valid_scheduled_messages
    logger.debug(
        "Retrieved valid messages to be potentially be scheduled",
        extra={"number_of_message": len(messages)},
    )
    for message in messages:
        # If we had scheduled this message to be sent at a time in the past, proceed
        if message.scheduled_next < datetime.now(tz=timezone.utc):
            logger.debug("Scheduling message", extra={"message_name": message.name})
            # If when to send is in the past as well, that means we should send it immediately
            if message.when_to_send < datetime.now(tz=timezone.utc):
                logger.debug("Scheduling message to be sent immediately", extra={"message_name": message.name})
                send_message_timestamp = int(datetime.now(timezone.utc).timestamp()) + 240
                if message.frequency == "daily":
                    new_scheduled_next = datetime.now(timezone.utc) + timedelta(days=1)
                elif message.frequency == "weekly":
                    new_scheduled_next = datetime.now(timezone.utc) + timedelta(days=7)
                else:
                    when_to_send_month = (
                        message.when_to_send.month + 1 if message.when_to_send.month < TOTAL_MONTHS_IN_YEAR else 1
                    )
                    when_to_send_year = (
                        message.when_to_send.year + 1
                        if message.when_to_send.month == TOTAL_MONTHS_IN_YEAR
                        else message.when_to_send.year
                    )
                    # Should find the next Monday in the month - will have to increase the variability in frequency
                    # to post theses on different days
                    next_month = datetime(when_to_send_year, when_to_send_month, 7, tzinfo=timezone.utc)
                    offset = -next_month.weekday()
                    new_scheduled_next = next_month + timedelta(days=offset)
            # Otherwise, we send it out normally using the when_to_send field
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
            if response.status_code == status.HTTP_200_OK:
                logger.debug(
                    "Updating the Airtable table for row with new scheduled next time",
                    extra={
                        "table_name": scheduled_message_table.table_name,
                        "airtable_id": message.airtable_id,
                        "new_scheduled_next": new_scheduled_next,
                    },
                )
                scheduled_message_table.update_record(
                    message.airtable_id,
                    {
                        "Scheduled Next": str(new_scheduled_next),
                    },
                )
            else:
                logger.warning(
                    "Issue sending the scheduled message, scheduling failed with Slack response",
                    extra={"response": response.__dict__, "message_name": message.name},
                )
