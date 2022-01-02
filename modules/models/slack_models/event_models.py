from pydantic import BaseModel, Field


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
