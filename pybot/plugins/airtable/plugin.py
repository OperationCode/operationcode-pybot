import asyncio
import logging
import os
from collections import defaultdict

from pybot.plugins.airtable import endpoints
from pybot.plugins.airtable.api import AirtableAPI

logger = logging.getLogger(__name__)


class AirtablePlugin:
    __name__ = "airtable"

    def __init__(self):
        self.session = None  # set lazily on plugin load
        self.api_key = None
        self.base_key = None
        self.api = None
        self.verify = None

        self.routers = {"request": RequestRouter()}

    def load(self, sirbot, api_key=None, base_key=None, verify=None):
        self.session = sirbot.http_session
        self.api_key = api_key or os.environ["AIRTABLE_API_KEY"]
        self.base_key = base_key or os.environ["AIRTABLE_BASE_KEY"]
        self.verify = verify or os.environ["AIRTABLE_VERIFY"]

        self.api = AirtableAPI(self.session, self.api_key, self.base_key)

        sirbot.router.add_route("POST", "/airtable/request", endpoints.incoming_request)

    def on_request(self, request, handler, **kwargs):
        if not asyncio.iscoroutinefunction(handler):
            handler = asyncio.coroutine(handler)
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
