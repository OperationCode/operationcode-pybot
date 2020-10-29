"""Simple bot module."""
from daily_programmer_helper import DailyProgrammerHelper
from slack_bolt.async_app import AsyncApp
from slack_sdk.web.async_internal_utils import _get_event_loop


async def recognize_challenge(message, client, say, context, *args, **kwargs):
    r"""Detect challenges.

    Detect messages which start with something matching the regex
    in DailyProgrammerHelper

    Example:
    === Wednesday October 14th 2020 - Daily Programmer ===
    """
    helper = await DailyProgrammerHelper.getInstance()
    await helper.parse_message(message)


class DailyProgrammerBot(AsyncApp):
    """Bot specialization."""

    def __init__(self, **options):
        """Init bot and register listener."""
        super().__init__(**options)
        self.message(DailyProgrammerHelper.CHALLENGE_REGEX)(
            recognize_challenge)

    def start(self, port: int = 3000, path: str = "/slack/events") -> None:
        """Start a web server using AIOHTTP.

        parameters:
        port (int): The port to listen on (Default: 3000)

        path (string): The path to handle request from Slack
        (Default: /slack/events)

        returns: None
        """
        # Get asyncio event loop
        loop = _get_event_loop()
        # List challenges
        loop.run_until_complete(self.list_challenges())
        # Start server
        super().start(port, path)

    async def list_challenges(self):
        """List challenges already in channel."""
        print("Fetching challenge history...")
        # Fetch conversations available
        response = await self.client.conversations_list()
        if response is None or response['channels'] is None:
            raise HistoryFetchingException()
        daily_programmer_channel = None
        # Find correct channel
        for channel in response['channels']:
            if channel['name'] == 'daily-programmer':
                daily_programmer_channel = channel

        # Get channel id
        channel_id = daily_programmer_channel['id']
        # Fetch channel history
        history = await self.client.conversations_history(channel=channel_id)
        # Parse channel history using helper
        print("Done...")
        helper = await DailyProgrammerHelper.getInstance()
        await helper.parse_channel_history(history)


class HistoryFetchingException(Exception):
    """Exception raised when channel history cannot be fetch."""

    def __init__(self):
        """Init exception."""
        self.error = "Currently unable to fetch channel history. Try later."
