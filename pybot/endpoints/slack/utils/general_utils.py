import functools

from pybot._vendor.sirbot import SirBot
from pybot._vendor.slack.commands import Command
from pybot._vendor.slack.exceptions import SlackAPIError
from pybot._vendor.slack.methods import Methods


def catch_command_slack_error(func):
    """
    Decorator for wrapping/catching exceptions thrown by
    the slack client and displaying an error to the user.

    Only necessary (for now) for functions that post messages to
    slack channels
    """

    @functools.wraps(func)
    async def handler(command: Command, app: SirBot, *args, **kwargs):
        try:
            await func(command, app, *args, **kwargs)

        except SlackAPIError:
            channel_id = command["channel_id"]
            slash_command = command["command"]
            slack_id = command["user_id"]
            slack = app["plugins"]["slack"]

            await slack.api.query(
                Methods.CHAT_POST_EPHEMERAL,
                dict(
                    user=slack_id,
                    channel=slack_id,
                    as_user=True,
                    text=(
                        f"Could not post result of `{slash_command}` "
                        f"to channel <#{channel_id}>"
                    ),
                ),
            )

    return handler
