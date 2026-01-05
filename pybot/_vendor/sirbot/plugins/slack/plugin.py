"""
Vendored sirbot Slack plugin for Python 3.12+
"""

import asyncio
import logging
import os
from collections.abc import Callable, Coroutine
from typing import Any

from pybot._vendor.slack import methods
from pybot._vendor.slack.actions import Router as ActionRouter
from pybot._vendor.slack.commands import Router as CommandRouter
from pybot._vendor.slack.events import EventRouter, MessageRouter
from pybot._vendor.slack.io.aiohttp import SlackAPI

from . import endpoints

LOG = logging.getLogger(__name__)

# Type alias for async handlers
AsyncHandler = Callable[..., Coroutine[Any, Any, Any]]


def _ensure_async(handler: Callable) -> AsyncHandler:
    """Ensure handler is an async function."""
    if not asyncio.iscoroutinefunction(handler):
        raise TypeError(
            f"Handler {handler.__name__} must be an async function (defined with 'async def')"
        )
    return handler


class SlackPlugin:
    """
    Handle communication from and to Slack.

    Endpoints:
        * ``/slack/events``: Incoming events.
        * ``/slack/commands``: Incoming commands.
        * ``/slack/actions``: Incoming actions.

    Args:
        token: Slack authentication token (env var: `SLACK_TOKEN`).
        bot_id: Bot ID (env var: `SLACK_BOT_ID`).
        bot_user_id: User ID of the bot (env var: `SLACK_BOT_USER_ID`).
        admins: List of Slack admin user IDs (env var: `SLACK_ADMINS`).
        verify: Slack verification token (env var: `SLACK_VERIFY`).
        signing_secret: Slack signing secret (env var: `SLACK_SIGNING_SECRET`).
    """

    __name__ = "slack"

    def __init__(
        self,
        *,
        token: str | None = None,
        bot_id: str | None = None,
        bot_user_id: str | None = None,
        admins: list[str] | None = None,
        verify: str | None = None,
        signing_secret: str | None = None,
    ) -> None:
        self.api: SlackAPI | None = None
        self.token = token or os.environ["SLACK_TOKEN"]
        self.admins = admins or os.environ.get("SLACK_ADMINS", [])

        if signing_secret or "SLACK_SIGNING_SECRET" in os.environ:
            self.signing_secret = signing_secret or os.environ["SLACK_SIGNING_SECRET"]
            self.verify = None
        else:
            self.verify = verify or os.environ["SLACK_VERIFY"]
            self.signing_secret = None

        self.bot_id = bot_id or os.environ.get("SLACK_BOT_ID")
        self.bot_user_id = bot_user_id or os.environ.get("SLACK_BOT_USER_ID")
        self.handlers_option: dict = {}

        if not self.bot_user_id:
            LOG.warning(
                "`SLACK_BOT_USER_ID` not set. It is required for `on mention` routing "
                "and discarding messages from Sir Bot-a-lot to avoid loops."
            )

        self.routers = {
            "event": EventRouter(),
            "command": CommandRouter(),
            "message": MessageRouter(),
            "action": ActionRouter(),
        }

    def load(self, sirbot: Any) -> None:
        LOG.info("Loading slack plugin")
        self.api = SlackAPI(session=sirbot.http_session, token=self.token)

        sirbot.router.add_route("POST", "/slack/events", endpoints.incoming_event)
        sirbot.router.add_route("POST", "/slack/commands", endpoints.incoming_command)
        sirbot.router.add_route("POST", "/slack/actions", endpoints.incoming_action)

        if self.bot_user_id and not self.bot_id:
            sirbot.on_startup.append(self.find_bot_id)

    def on_event(self, event_type: str, handler: AsyncHandler, wait: bool = True) -> None:
        """Register handler for an event."""
        handler = _ensure_async(handler)
        configuration = {"wait": wait}
        self.routers["event"].register(event_type, (handler, configuration))

    def on_command(self, command: str, handler: AsyncHandler, wait: bool = True) -> None:
        """Register handler for a command."""
        handler = _ensure_async(handler)
        configuration = {"wait": wait}
        self.routers["command"].register(command, (handler, configuration))

    def on_message(
        self,
        pattern: str,
        handler: AsyncHandler,
        mention: bool = False,
        admin: bool = False,
        wait: bool = True,
        **kwargs: Any,
    ) -> None:
        """Register handler for a message pattern."""
        handler = _ensure_async(handler)

        if admin and not self.admins:
            LOG.warning("Slack admin IDs are not set. Admin-limited endpoints will not work.")

        configuration = {"mention": mention, "admin": admin, "wait": wait}
        self.routers["message"].register(
            pattern=pattern, handler=(handler, configuration), **kwargs
        )

    def on_action(
        self,
        action: str,
        handler: AsyncHandler,
        name: str = "*",
        wait: bool = True,
    ) -> None:
        """Register handler for an action."""
        handler = _ensure_async(handler)
        configuration = {"wait": wait}
        self.routers["action"].register(action, (handler, configuration), name)

    def on_block(
        self,
        block_id: str,
        handler: AsyncHandler,
        action_id: str = "*",
        wait: bool = True,
    ) -> None:
        """Register handler for a block_actions type action."""
        handler = _ensure_async(handler)
        configuration = {"wait": wait}
        self.routers["action"].register_block_action(block_id, (handler, configuration), action_id)

    def on_dialog_submission(
        self,
        callback_id: str,
        handler: AsyncHandler,
        wait: bool = True,
    ) -> None:
        """Register handler for a dialog_submission type action."""
        handler = _ensure_async(handler)
        configuration = {"wait": wait}
        self.routers["action"].register_dialog_submission(callback_id, (handler, configuration))

    async def find_bot_id(self, app: Any) -> None:
        rep = await self.api.query(url=methods.USERS_INFO, data={"user": self.bot_user_id})
        self.bot_id = rep["user"]["profile"]["bot_id"]
        LOG.warning(
            '`SLACK_BOT_ID` not set. For a faster start time set it to: "%s"',
            self.bot_id,
        )
