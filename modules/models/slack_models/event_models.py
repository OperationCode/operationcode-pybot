from pydantic import BaseModel, Field

from modules.models.slack_models.shared_models import SlackMessageInfo


class MemberJoinedChannelEvent(BaseModel):
    type: str = Field(
        ...,
        example="member_joined_channel",
        description="The type of event, should always be member_joined_channel",
    )
    user: str = Field(
        ...,
        example="U123456789",
        description="The Slack ID of the user who joined the channel",
    )
    channel: str = Field(
        ...,
        example="C0698JE0H",
        description="The Slack ID of the channel the user joined",
    )
    channel_type: str = Field(
        ...,
        example="C",
        description="The channel type - C is typically a public channel and G is for a private channel or group",
    )
    team: str = Field(..., example="T024BE7LD", description="The Slack ID of the team")
    inviter: str = Field(
        None,
        example="U123456789",
        description="The Slack user ID of the user who invited the joining user - is optional and won't show up for default channels, for example",
    )


class MessageReceivedChannelEvent(BaseModel):
    team_id: str = Field(
        ..., example="T024BE7LD", description="The Slack ID of the team"
    )
    api_app_id: str = Field(
        ..., example="A02R6C6S9JN", description="The Slack application ID"
    )
    event: SlackMessageInfo = Field(
        ..., description="The information about the message that was received"
    )
    type: str = Field(
        ...,
        example="event_callback",
        description="The type of event, should always be event_callback",
    )
    event_id: str = Field(
        ..., example="Ev02UJP6HDBR", description="The Slack provided ID of the event"
    )
    event_time: int = Field(
        ..., example=1642732981, description="The Unix timestamp of the event"
    )
    event_context: str = Field(
        ...,
        example="4-eyJldCI6Im1lc3NhZ2UiLCJ0aWQiOiJUMDFTQkxDUTU3QSIsImFpZCI6IkEwMlI2QzZTOUpOIiwiY2lkIjoiQzAxUlUxTUhNRkUifQ",
    )
