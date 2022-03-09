from datetime import datetime
from pydantic import Field
from enum import Enum

from modules.models.shared_models import AirtableRowBaseModel


class FrequencyEnum(str, Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"


class ScheduledMessageInfo(AirtableRowBaseModel):
    name: str = Field(
        ...,
        example="Mentorship Reminder",
        description="The display name of the message to be scheduled",
    )
    slug: str = Field(
        ...,
        example="mentorship_reminder",
        description="A more parseable representation of the name of the scheduled message - should be snake cased",
    )
    channel: str = Field(
        ..., example="general", description="Channel to send the message to"
    )
    message_text: str = Field(
        ...,
        example="Don't forget you can use the `/mentor` command to request a 1 on 1 session with a mentor!",
        description="A text string that can contain markdown syntax to be posted to Slack",
    )
    initial_date_time_to_send: datetime = Field(
        ...,
        example="2021-04-23T10:20:30.400+00:00",
        description="ISO formatted datetime in UTC to send the first message - this is used to set the schedule for this message",
    )
    frequency: FrequencyEnum = Field(
        ...,
        example="daily",
        description="Frequency to send the message - one of daily, weekly, monthly",
    )
    last_sent: datetime = Field(
        None,
        example="2021-04-23T10:20:30.400+00:00",
        description="When the message was last sent",
    )
    when_to_send: datetime = Field(
        ...,
        example="2021-04-23T10:20:30.400+00:00",
        description="When to send the message - this is calculated using a formula on the Airtable table",
    )
