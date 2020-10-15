"""Simple bot module."""
import re
from slack_bolt.async_app import AsyncApp


async def recognize_challenge(message, client, say, context, *args, **kwargs):
    r"""Detect challenges.

    Detect messages which start with something matching the regex

    ===?\s+([\w\s]+)\-?[\w\s]*\s+=?==

    Example:
    === Wednesday October 14th 2020 - Daily Programmer ===
    """
    await say("New challenge!")


class DailyProgrammerBot(AsyncApp):
    """Bot specialization."""

    def __init__(self, **options):
        """Init bot and register listener."""
        super().__init__(**options)
        self.message(re.compile(
            r"===?\s+([\w\s]+)\-?[\w\s]*\s+=?=="))(recognize_challenge)
