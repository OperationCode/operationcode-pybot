import logging
from datetime import datetime, timezone, timedelta
from slack_bolt.async_app import AsyncApp

from modules.airtable.scheduled_message_table import ScheduledMessagesTable
from modules.slack.blocks.announcement_blocks import general_announcement_blocks
from modules.utils import slack_team

logger = logging.getLogger(__name__)


async def schedule_messages(async_app: AsyncApp) -> None:
    logging.info("STAGE: Beginning task schedule_messages...")
    scheduled_message_table = ScheduledMessagesTable()
    messages = scheduled_message_table.all_valid_scheduled_messages
    logging.debug(f"Retrieved {len(messages)} total valid messages to be scheduled")
    for message in messages:
        # If the next send time is more than 119 days in the future, skip it as that's the limit for Slack
        if message.when_to_send < message.when_to_send + timedelta(days=119):
            # If the datetime in the table is in the past, schedule the message for now plus 2 minutes but update the
            #  table to have a datetime that is today with the same hour and minute as the first time to send
            # This can be readjusted in the table if need be to get the correct next send time
            if message.when_to_send < datetime.now(timezone.utc):
                datetime_to_update = datetime(
                    datetime.utcnow().year,
                    datetime.utcnow().month,
                    datetime.utcnow().day,
                    message.initial_date_time_to_send.hour,
                    message.initial_date_time_to_send.minute,
                    tzinfo=timezone.utc,
                )
                # Add on 120 seconds to the timestamp in order to not run into the "time in past" error
                datetime_to_send_message = (
                    int(datetime.now(timezone.utc).timestamp()) + 240
                )
            else:
                datetime_to_send_message = int(message.when_to_send.timestamp())
                datetime_to_update = message.when_to_send
            logging.debug(
                f"Scheduling message with name: {message.name} to be sent at datetime: {str(datetime_to_send_message)}"
            )
            response = await async_app.client.chat_scheduleMessage(
                channel=slack_team.general_channel.id,
                post_at=datetime_to_send_message,
                text=f"Announcement in {message.channel}...",
                blocks=general_announcement_blocks(message.name, message.message_text),
            )
            if response.status_code == 200:
                # if message.frequency == "Daily":
                #     next_when_to_send = datetime_to_update + timedelta(days=1)
                # elif message.frequency == "Weekly":
                #     next_when_to_send = datetime_to_update + timedelta(days=7)
                # else:
                #     next_when_to_send = datetime_to_update + timedelta(days=30)
                logging.debug(
                    f"Updating the Airtable {scheduled_message_table.table_name} table for row with id: {message.airtable_id} with new value Last Sent: {datetime_to_update}"
                )
                scheduled_message_table.update_record(
                    message.airtable_id,
                    {
                        "Last Sent": str(datetime_to_update),
                        # "When To Send": str(next_when_to_send),
                    },
                )
            else:
                logger.warning(
                    f"Issue sending the scheduled message: {message.name}, scheduling failed with slack response: {response.__dict__}"
                )
        else:
            logging.warning(
                f"Next send time for scheduled message: {message.name} is more than 119 days in the future"
            )
