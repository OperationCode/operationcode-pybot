import asyncio
import logging
import os
from collections import defaultdict
from typing import Any, Callable, Coroutine

from pybot.plugins.airtable import endpoints
from pybot.plugins.airtable.api import AirtableAPI

logger = logging.getLogger(__name__)

# Type alias for async handlers
AsyncHandler = Callable[..., Coroutine[Any, Any, Any]]


def _ensure_async(handler: Callable) -> AsyncHandler:
    """Ensure handler is an async function."""
    if not asyncio.iscoroutinefunction(handler):
        raise TypeError(
            f"Handler {handler.__name__} must be an async function (defined with 'async def')"
        )
    return handler


class AirtablePlugin:
    __name__ = "airtable"

    def __init__(self):
        self.session = None  # set lazily on plugin load
        self.api_key = None
        self.base_key = None
        self.api = None
        self.verify = None

        self.routers = {"request": RequestRouter()}

    def load(
        self,
        sirbot: Any,
        api_key: str | None = None,
        base_key: str | None = None,
        verify: str | None = None
    ) -> None:
        self.session = sirbot.http_session
        self.api_key = api_key or os.environ.get("AIRTABLE_API_KEY", "")
        self.base_key = base_key or os.environ.get("AIRTABLE_BASE_KEY", "")
        self.verify = verify or os.environ.get("AIRTABLE_VERIFY", "")

        self.api = AirtableAPI(self.session, self.api_key, self.base_key)

        sirbot.router.add_route("POST", "/airtable/request", endpoints.incoming_request)

    def on_request(self, request: str, handler: AsyncHandler, **kwargs: Any) -> None:
        handler = _ensure_async(handler)
        options = {**kwargs, "wait": False}
        self.routers["request"].register(request, (handler, options))


class RequestRouter:
    def __init__(self):
        self._routes = defaultdict(list)

    def register(self, request_type, handler, **detail):
        logger.info("Registering %s, %s to %s", request_type, detail, handler)
        self._routes[request_type].append(handler)

    def dispatch(self, request):
        logger.debug('Dispatching request "%s"', request.get("type"))
        if request["type"] in self._routes:
            for handler in self._routes.get(request["type"]):
                yield handler
        else:
            return
