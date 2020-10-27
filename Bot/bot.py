"""Simple bot module."""
from daily_programmer_helper import DailyProgrammerHelper
from slack_bolt.async_app import AsyncApp


async def recognize_challenge(message, client, say, context, *args, **kwargs):
    r"""Detect challenges.

    Detect messages which start with something matching the regex
    in DailyProgrammerHelper

    Example:
    === Wednesday October 14th 2020 - Daily Programmer ===
    """
    helper = await DailyProgrammerHelper.getInstance()
    await helper.parse_message(message)


async def list_challenges(ack, body, respond, context, client):
    """List challenges from channel."""
    # must always ack
    await ack()
    # recover channel name and id
    channel_name = body['channel_name'] if body else None
    if channel_name is None or channel_name != 'daily-programmer':
        return
    channel_id = body['channel_id']
    # recover channel history (messages + events)
    channel_history = await client.conversations_history(channel=channel_id)
    # parse channel history using helper
    helper = await DailyProgrammerHelper.getInstance()
    await helper.parse_channel_history(channel_history)


class DailyProgrammerBot(AsyncApp):
    """Bot specialization."""

    def __init__(self, **options):
        """Init bot and register listener."""
        super().__init__(**options)
        self.command("/list-challenges")(list_challenges)
        self.message(DailyProgrammerHelper.CHALLENGE_REGEX)(
            recognize_challenge)
