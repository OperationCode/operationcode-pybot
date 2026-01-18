import inspect
import logging
from collections import defaultdict
from collections.abc import Callable, Coroutine
from typing import Any

from pybot.plugins.api import endpoints

logger = logging.getLogger(__name__)

# Type alias for async handlers
AsyncHandler = Callable[..., Coroutine[Any, Any, Any]]


def _ensure_async(handler: Callable) -> AsyncHandler:
    """Ensure handler is an async function."""
    if not inspect.iscoroutinefunction(handler):
        raise TypeError(
            f"Handler {handler.__name__} must be an async function (defined with 'async def')"
        )
    return handler


class APIPlugin:
    __name__ = "api"

    def __init__(self):
        self.session = None
        self.routers = {"slack": SlackAPIRequestRouter()}

    def load(self, sirbot: Any) -> None:
        self.session = sirbot.http_session

        sirbot.router.add_route("GET", "/pybot/api/v1/slack/{resource}", endpoints.slack_api)
        sirbot.router.add_route("POST", "/pybot/api/v1/slack/{resource}", endpoints.slack_api)

    def on_get(self, request: str, handler: AsyncHandler, **kwargs: Any) -> None:
        handler = _ensure_async(handler)
        options = {**kwargs, "wait": False}
        self.routers["slack"].register(request, (handler, options))


class SlackAPIRequestRouter:
    def __init__(self):
        self._routes = defaultdict(list)

    def register(self, resource, handler, **detail):
        logger.info(f"Registering {resource}, {detail} to {handler}")
        self._routes[resource].append(handler)

    def dispatch(self, request):
        resource = request.resource
        logger.debug(f"Dispatching request {resource}")
        if resource in self._routes:
            yield from self._routes.get(resource)
        else:
            return
