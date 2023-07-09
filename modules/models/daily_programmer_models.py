from datetime import datetime  # noqa: D100

from pydantic import Field

from modules.models.shared_models import AirtableRowBaseModel


class DailyProgrammerInfo(AirtableRowBaseModel):  # noqa: D101
    name: str = Field(
        ...,
        example="Minimum Absolute Difference",
        description="The display name of the daily programmer entry - will be wrapped in [] in the text from Slack",
    )
    slug: str = Field(
        ...,
        example="minimum_absolute_difference",
        description="A more parseable representation of the name of the message - should be snake cased; this is set by formula in Airtable based on the Message Name field",  # noqa: E501
    )
    text: str = Field(
        ...,
        example="Your report has been received :check_mark:",
        description="The text of the message - utilizes Slack's mrkdwn format",
    )
    category: str = Field(
        ...,
        example="mentorship_request",
        description="Snake cased category of the message",
    )
    initially_posted_on: datetime = Field(
        None,
        example="2021-04-23T10:20:30.400+00:00",
        description="ISO formatted datetime in UTC for when the message was first posted to the channel",
    )
    last_posted_on: datetime = Field(
        None,
        example="2021-04-23T10:20:30.400+00:00",
        description="ISO formatted datetime in UTC for when the message was last posted to the channel",
    )
    posted_count: int = Field(
        ...,
        description="The number of time this message has been posted to the channel",
    )
