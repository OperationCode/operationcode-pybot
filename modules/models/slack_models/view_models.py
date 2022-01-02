from pydantic import Field

from modules.models.slack_models.shared_models import (
    BasicSlackRequest,
    SlackUserInfo,
    SlackViewInfo,
)


class SlackViewRequestBody(BasicSlackRequest):
    user: SlackUserInfo = Field(
        ...,
        description="The Slack user object of the user who triggered the submission of the view",
    )
    view: SlackViewInfo = Field(
        ..., description="The information of the view that was submitted"
    )
    response_urls: list[str] = Field(
        [],
        example="['https://hooks.slack.com/actions/T01SBLfdsaQ57A/2902419552385/BiWpNhRSURKF9CvqujZ3x1MQ']",
        description="List of URLs to be used for responses depending on if the view has elements that are configured to generate a response URL",
    )
