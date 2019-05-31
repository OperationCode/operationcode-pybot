import asyncio
import logging
from collections import defaultdict

from pybot.plugins.api import endpoints

logger = logging.getLogger(__name__)


class APIPlugin:
    __name__ = "api"

    def __init__(self):
        self.session = None
        self.routers = {"slack": SlackAPIRequestRouter()}

    def load(self, sirbot):
        self.session = sirbot.http_session

        sirbot.router.add_route(
            "GET", "/pybot/api/v1/slack/{resource}", endpoints.slack_api
        )
        sirbot.router.add_route(
            "POST", "/pybot/api/v1/slack/{resource}", endpoints.slack_api
        )

    def on_get(self, request, handler, **kwargs):
        if not asyncio.iscoroutinefunction(handler):
            handler = asyncio.coroutine(handler)
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
            for handler in self._routes.get(resource):
                yield handler
        else:
            return
