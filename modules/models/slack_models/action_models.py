from pydantic import Field

from modules.models.slack_models.shared_models import (
    BasicSlackRequest,
    SlackUserInfo,
    SlackActionContainerInfo,
    BaseSlackTeamInfo,
    SlackChannelInfo,
    SlackMessageInfo,
    SlackActionInfo,
)


class SlackActionRequestBody(BasicSlackRequest):
    type: str = Field(..., example="block_actions", description="The type of action")
    user: SlackUserInfo = Field(
        ..., description="The user who triggered the action request"
    )
    container: SlackActionContainerInfo = Field(
        ..., description="The container where the action was triggered"
    )
    team: BaseSlackTeamInfo = Field(..., description="Basic team information")
    channel: SlackChannelInfo = Field(
        ..., description="The channel the action was triggered in"
    )
    message: SlackMessageInfo = Field(
        ..., description="The original message where the action was triggered"
    )
    response_url: str = Field(
        ...,
        example="https://hooks.slack.com/actions/T01SBLCQ57A/2899731511204/xb8gxI4ldtCaVwbdsddM0nb",
        description="The response URL where a response can be sent if needed",
    )
    actions: list[SlackActionInfo] = Field(
        ..., description="The action information about the action that was triggered"
    )
