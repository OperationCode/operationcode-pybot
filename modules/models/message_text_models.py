"""Models related to message text."""
from pydantic import Field

from modules.models.shared_models import AirtableRowBaseModel


class MessageTextInfo(AirtableRowBaseModel):
    """The message text info model.

    This model represents messages that are sent to different channels in Slack.
    """

    name: str = Field(
        ...,
        example="Report Received",
        description="The display name of the message text",
    )
    slug: str = Field(
        ...,
        example="report_received",
        description="A more parseable representation of the name of the message - should be snake cased; "
        "this is set by formula in Airtable based on the Message Name field",
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
