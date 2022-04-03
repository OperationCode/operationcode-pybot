import os
import logging
from functools import cached_property
from typing import Any, Union

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class SlackUserInfo(BaseModel):
    id: str = Field(
        ...,
        example="U01RN31JSTD",
        description="Slack ID of the user",
    )
    username: str = Field(
        ..., example="julio123", description="The Slack username of the user"
    )
    name: str = Field(
        ..., example="JulioMendez", description="The Slack display name of the user"
    )


class SlackEditedInfo(BaseModel):
    user: str = Field(
        ..., example="B02QRQ4KU5V", description="The user who last edited the message"
    )
    ts: str = Field(
        ...,
        example="1640727458.000000",
        description="The Unix Epoch timestamp of when the message was last edited",
    )


class SlackTextObjectInfo(BaseModel):
    type: str = Field(..., example="mrkdwn", description="The type of text object")
    text: str = Field(
        ...,
        example="Testing text for a text object",
        description="The text that makes up the text object",
    )


class SlackBlockInfo(BaseModel):
    type: str = Field(..., example="section", description="The type of block")
    block_id: str = Field(
        ...,
        example="report_title_block",
        description="ID of the block - must be unique within the immediate set of blocks. Will be added by Slack if it's missing in the definition",
    )
    text: SlackTextObjectInfo = Field(
        None, description="Optional text object for this block"
    )

    class Config:
        # Allows extra attributes on this model
        extra = "allow"


class SlackViewInfo(BaseModel):
    id: str = Field(
        ...,
        example="V02S65HDH9Q",
        description="Slack ID of the view",
    )
    type: str = Field(..., example="modal", description="The type of view")
    blocks: list[SlackBlockInfo] = Field(
        ..., description="List of blocks in the view - there must be at least one"
    )
    private_metadata: str = Field(
        None,
        description="Private data that can be included on a view and sent with a submission - not visible to the user",
    )
    callback_id: str = Field(
        ...,
        example="report_form_submit",
        description="Callback for the submission action of the view, used to handle the submission",
    )
    state: dict[str, Any] = Field(
        None,
        description="State of a view, if it exists - contains the value of the input elements in the view",
    )
    hash: str = Field(
        ...,
        example="1640903702.u8C2NM3Y",
        description="Hash string sent with the submission of the view, this is used by the update and publish views API calls to ensure that only the most recent view is updated or published",
    )
    title: SlackTextObjectInfo = Field(
        None, description="The text object used for the title of the view"
    )
    previous_view_id: str = Field(
        None,
        example="V02S65HDH9Q",
        description="The previous view's ID - typically used in workflows",
    )
    root_view_id: str = Field(
        None, example="V02S65HDH9Q", description="The root view's ID"
    )
    external_id: str = Field(
        None,
        example="report_form_modal",
        description="The optional external ID for the view, must be unique across all views - this is added by the bot",
    )
    bot_id: str = Field(
        None,
        example="B02QRQ4KU5V",
        description="The ID of the bot that generated the view",
    )


class SlackMessageInfo(BaseModel):
    client_msg_id: str = Field(None, example="de437daf-67fd-48a6-b9bd-03f9336509e9")
    bot_id: str = Field(
        None,
        example="B02QRQ4KU5V",
        description="Slack ID of the bot that sent the message - provided that the original message was sent from a bot",
    )
    type: str = Field(..., example="message", description="The type of message")
    text: str = Field(
        None,
        example="Typical fallback text...",
        description="If blocks are provided, this is the fallback text for the message. If no blocks are present, this is the message",
    )
    user: str = Field(
        ...,
        example="U02RK2AL5LZ",
        description="Slack user ID of the user who triggered the action",
    )
    blocks: list[Union[Any, SlackBlockInfo]] = Field(
        None, description="The list of blocks for a particular message"
    )
    ts: str = Field(
        ...,
        example="1640727423.003500",
        description="Unix Epoch timestamp the message was received by Slack - typically used to locate the message",
    )
    edited: SlackEditedInfo = Field(
        None, description="Information about who and when the message was last edited"
    )
    thread_ts: str = Field(
        None,
        example="1640727423.003500",
        description="The Unix Epoch timestamp the thread was created",
    )
    reply_count: int = Field(None, description="The number of replies the message has")
    reply_users_count: int = Field(
        None, description="The number of users who have replied to the message"
    )
    latest_reply: str = Field(
        None,
        example="1640727423.003500",
        description="The Unix Epoch timestamp of when the latest reply was created",
    )
    reply_users: list[str] = Field(
        None,
        example=["U02RK2AL5LZ"],
        description="A list of Slack user IDs of users who have replied to the message",
    )
    last_read: str = Field(
        None,
        example="1640727423.003500",
        description="The Unix Epoch timestamp of when the message was last read",
    )

    class Config:
        arbitrary_types_allowed = True


class SlackActionInfo(BaseModel):
    action_id: str = Field(
        ...,
        example="reset_greet_new_user_claim",
        description="The ID that identifies this particular action and allows the application to handle it when triggered",
    )
    block_id: str = Field(
        None,
        example="reset_claim_action",
        description="The ID that identifies the block the action is part of",
    )
    text: SlackTextObjectInfo = Field(
        None,
        description="The text object that represents the text on the action (button, etc)",
    )
    value: Union[dict[str, Any], str] = Field(
        None,
        description="The value sent to the application when the action is triggered",
    )
    style: str = Field(
        None,
        example="danger",
        description="The style of the action, typically the style of the button",
    )
    type: str = Field(..., example="button", description="The type of action")
    action_ts: str = Field(
        ...,
        example="1640727423.003500",
        description="The Unix Epoch timestamp of when the action was triggered",
    )


class SlackActionContainerInfo(BaseModel):
    type: str = Field(
        ..., example="message", description="The type of container the action came from"
    )
    message_ts: str = Field(
        ...,
        example="1640752131.000200",
        description="Unix Epoch timestamp of when the message was sent to Slack, typically used to locate the message",
    )
    channel_id: str = Field(
        ..., example="C01S0K034TB", description="The channel ID the message came from"
    )
    is_ephemeral: bool = Field(
        ..., description="Whether or not the message is ephemeral"
    )


class SlackChannelInfo(BaseModel):
    id: str = Field(..., example="C01S0K034TB", description="Slack ID of the channel")
    name: str = Field(..., example="general", description="Name of the channel")


class BasicSlackRequest(BaseModel):
    trigger_id: str = Field(
        ...,
        example="2875577934983.1895692821248.5b6bb2ed4127b90954e8d32a86e2cafc",
        description="The ID of the trigger for this request, typically used to respond to the correct place and user",
    )
    api_app_id: str = Field(
        ..., example="A02R6C6S9JN", description="The Slack application ID"
    )


class SlackConversationInfo(BaseModel):
    """Slack used to call these channels, but now they are called conversations, of which channels are a subset along with IMs and MPIMs (Multi Person IMs)"""

    id: str = Field(
        ...,
        example="C012AB3CD",
        description="Slack ID of the conversation",
    )
    name: str = Field(..., example="general", description="Name of the conversation")
    is_channel: bool = Field(
        ..., description="Whether the conversation is a channel or not"
    )
    is_im: bool = Field(..., description="Whether the conversation is an IM or not")
    is_mpim: bool = Field(
        ..., description="Whether the conversation is a Multi Person IM or not"
    )
    is_private: bool = Field(
        ..., description="Whether the conversation is private or not"
    )


class BaseSlackTeamInfo(BaseModel):
    id: str = Field(
        ...,
        example="T01SBLCQ57A",
        description="Slack ID of the team",
    )
    domain: str = Field(
        None, example="bot-testing-field", description="The domain of the team"
    )


class SlackTeamInfo(BaseSlackTeamInfo):
    """Slack used to call these workspaces, but they are referred to as teams now"""

    name: str = Field(
        ..., example="Bot-Testing-Field", description="The name of the Slack workspace"
    )
    conversations: list[SlackConversationInfo] = Field(
        ..., description="The list of Slack channels in this workspace"
    )


class SlackTeam:
    def __init__(self, team_info: SlackTeamInfo) -> None:
        logger.debug(f"Initializing the Slack Team with team_info: {team_info}")
        self._team_info = team_info

    def find_channel_by_name(self, channel_name: str) -> SlackConversationInfo:
        logger.debug(f"Finding channel by name: {channel_name}")
        logger.debug(f"Full channel list: {[conversation_info.name for conversation_info in self.full_conversation_list]}")
        return [
            conversation
            for conversation in self.full_conversation_list
            if conversation.name == channel_name
        ][0]

    @cached_property
    def slack_id(self) -> str:
        return self._team_info.id

    @cached_property
    def name(self) -> str:
        return self._team_info.name

    @cached_property
    def full_conversation_list(self) -> list[SlackConversationInfo]:
        return self._team_info.conversations

    @cached_property
    def greetings_channel(self) -> SlackConversationInfo:
        return self.find_channel_by_name(os.getenv("GREETINGS_CHANNEL_NAME"))

    @cached_property
    def mentors_internal_channel(self) -> SlackConversationInfo:
        return self.find_channel_by_name(os.getenv("MENTORS_CHANNEL_NAME"))

    @cached_property
    def moderators_channel(self) -> SlackConversationInfo:
        return self.find_channel_by_name(os.getenv("MODERATORS_CHANNEL_NAME"))

    @cached_property
    def general_channel(self) -> SlackConversationInfo:
        return self.find_channel_by_name(os.getenv("GENERAL_CHANNEL_NAME"))

    @cached_property
    def pride_channel(self) -> SlackConversationInfo:
        return self.find_channel_by_name(os.getenv("PRIDE_CHANNEL_NAME"))

    @cached_property
    def blacks_in_tech(self) -> SlackConversationInfo:
        return self.find_channel_by_name(os.getenv("BLACKS_IN_TECH_CHANNEL_NAME"))
