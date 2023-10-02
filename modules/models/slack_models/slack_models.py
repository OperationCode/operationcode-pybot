from typing import Any  # noqa: D100

from pydantic import BaseModel, Field

from modules.models.slack_models.shared_models import (
    BasicSlackRequest,
    SlackActionContainerInfo,
    SlackActionInfo,
    SlackChannelInfo,
    SlackMessageInfo,
    SlackUserInfo,
    SlackViewInfo,
)


class SlackResponseBody(BasicSlackRequest):
    """The body of a Slack response."""

    type: str = Field(
        ...,
        example="view_submission",
        description="The type of request the response is responding to",
    )
    originating_user: SlackUserInfo = Field(
        ...,
        description="The info of the user who triggered the request",
    )
    view: SlackViewInfo | None = Field(
        None,
        description="View object of the original message if it exists",
    )
    container: SlackActionContainerInfo | None = Field(
        None,
        description="The container that the action originated from if it exists",
    )
    channel: SlackChannelInfo | None = Field(
        None,
        description="The channel information for where the original request was from",
    )
    message: SlackMessageInfo | None = Field(
        None,
        description="The original message from the request, if it exists",
    )
    response_urls: list[str] | None = Field(
        None,
        description="List of response URLs, typically included with a view response",
    )
    actions: list[SlackActionInfo] | None = Field(
        None,
        description="The list of actions in this message",
    )


class BotInfo(BaseModel):
    """Information about the bot that sent the request."""

    slack_id: str = Field(
        ...,
        example="B02QRQ4KU5V",
        description="Slack ID for the bot that sent the request",
    )
    app_id: str = Field(
        ...,
        example="A02R6C6S9JN",
        description="Slack ID for the parent application",
    )
    name: str = Field(
        ...,
        example="retrieval-bot",
        description="Name of the bot that sent the request",
    )
    team_id: str = Field(
        ...,
        example="T01SBLCQ57A",
        description="Slack team ID of the bot that sent the request",
    )


class BasicSlackBotResponse(BaseModel):
    """Basic information about a Slack bot response."""

    date_time_received: str = Field(
        ...,
        example="Tue, 28 Dec 2021 05:36:22 GMT",
        description="Timestamp for when the response was received",
    )
    oauth_scopes: str = Field(
        ...,
        example="app_mentions:read,channels:history,channels:read,channels:join,emoji:read",
        description="List of oauth scopes the bot is authorized to use",
    )
    status_ok: bool = Field(
        ...,
        description="Status of the request that triggered the response, true means the request was successful while "
        "false means it was in error",
    )
    received_timestamp: str = Field(
        ...,
        example="1640669783.000100",
        description="Unix epoch timestamp for when the request was received",
    )


class SlackBotResponseContent(BasicSlackBotResponse):
    """The content of a Slack bot response."""

    channel: str = Field(
        ...,
        example="D02R6CR6DMG",
        description="Channel the request was sent to",
    )
    bot_info: BotInfo = Field(
        ...,
        description="Information about the bot that sent the request",
    )
    request_blocks: list[dict[str, Any]] | None = Field(
        None,
        description="List of blocks in the original request",
    )
