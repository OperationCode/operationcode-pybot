import asyncio
import logging
import os

from pybot.plugins.airtable import endpoints
from pybot.plugins.airtable.api import AirtableAPI
from pybot.plugins.airtable.requests import RequestRouter

logger = logging.getLogger(__name__)


class AirtablePlugin:
    __name__ = 'airtable'

    def __init__(self):
        self.session = None  # set lazily on plugin load
        self.api_key = None
        self.base_key = None
        self.api = None

        self.routers = {
            'request': RequestRouter()
        }

    def load(self, sirbot, api_key=None, base_key=None):
        self.session = sirbot.http_session
        self.api_key = api_key or os.environ['AIRTABLE_API_KEY']
        self.base_key = base_key or os.environ['AIRTABLE_BASE_KEY']

        self.api = AirtableAPI(self.session, self.api_key, self.base_key)

        sirbot.router.add_route('POST', '/airtable/request', endpoints.incoming_request)

    def on_request(self, request, handler, wait=True):
        if not asyncio.iscoroutinefunction(handler):
            handler = asyncio.coroutine(handler)
        configuration = {'wait': wait}
        self.routers['request'].register(request, (handler, configuration))
