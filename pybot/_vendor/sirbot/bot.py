"""
Vendored sirbot library for Python 3.12+
Original: https://github.com/pyslackers/sir-bot-a-lot-2
"""

import logging
from typing import Any

import aiohttp.web

from . import endpoints

LOG = logging.getLogger(__name__)


class SirBot(aiohttp.web.Application):
    def __init__(self, user_agent: str | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.router.add_route("GET", "/sirbot/plugins", endpoints.plugins)

        self["plugins"] = {}
        self["http_session"] = None  # Created on startup
        self["user_agent"] = user_agent or "sir-bot-a-lot"

        self.on_startup.append(self._create_session)
        self.on_shutdown.append(self.stop)

    async def _create_session(self, app: aiohttp.web.Application) -> None:
        """Create HTTP session on startup (when event loop exists)."""
        self["http_session"] = aiohttp.ClientSession()

    def start(self, **kwargs: Any) -> None:
        LOG.info("Starting SirBot")
        aiohttp.web.run_app(self, **kwargs)

    def load_plugin(self, plugin: Any, name: str | None = None) -> None:
        name = name or plugin.__name__
        self["plugins"][name] = plugin
        plugin.load(self)

    async def stop(self, sirbot: "SirBot") -> None:
        if self["http_session"]:
            await self["http_session"].close()

    @property
    def plugins(self) -> dict:
        return self["plugins"]

    @property
    def http_session(self) -> aiohttp.ClientSession:
        return self["http_session"]

    @property
    def user_agent(self) -> str:
        return self["user_agent"]
