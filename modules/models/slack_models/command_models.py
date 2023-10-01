from pydantic import Field  # noqa: D100

from modules.models.slack_models.shared_models import BasicSlackRequest


class SlackCommandRequestBody(BasicSlackRequest):
    """The body of a Slack command request.

    These are typically received from the Slack application after a slash command is used.
    """

    command: str = Field(
        ...,
        example="/mentor_request",
        description="The command that triggered the request",
    )
    user_id: str = Field(
        ...,
        example="U01RN31JSTT",
        description="The Slack user ID for the user who triggered the request",
    )
    user_name: str = Field(
        ...,
        example="john123",
        description="The Slack user name for the user who triggered the request",
    )
    channel_id: str = Field(
        ...,
        example="D02R6CR6DMG",
        description="The Slack channel ID where the command was triggered",
    )
    channel_name: str = Field(
        ...,
        example="directmessage",
        description="The name of the channel where the command was triggered",
    )
    response_url: str | None = Field(
        None,
        example="https://hooks.slack.com/actions/T01SBLfdsaQ57A/2902419552385/BiWpNhRSURKF9CvqujZ3x1MQ",
        description="The URL to send the response to that will automatically put the response in the right place",
    )
    team_id: str = Field(
        ...,
        example="T01SBLCQ57A",
        description="The Slack ID of the team that the command came from",
    )
