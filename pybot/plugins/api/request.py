import copy
import json
import os
from typing import MutableMapping

BACKEND_AUTH_TOKEN = os.environ.get("BACKEND_AUTH_TOKEN", "devBackendToken")


class SlackApiRequest(MutableMapping):
    """
    MutableMapping representing an api query request.  Shameless stolen from pyslackers/slack-sansio

    Attributes:
        resource: The resource the request was made for (i.e. the last part of the request url)

        query: Querystring params as a dict

        token: Bearer Token provided with request
    """

    auth_tokens = {BACKEND_AUTH_TOKEN}

    def __init__(self, raw_request, resource, query):
        self.request = raw_request
        self.resource = resource
        self.query = query
        self.token = self.__get_token(raw_request)

    @property
    def authorized(self):
        return self.token is not None and self.token in self.auth_tokens

    async def json(self):
        if self.request.can_read_body:
            return await self.request.json()
        else:
            return {}

    @classmethod
    def from_request(cls, raw_request):
        resource = raw_request.match_info["resource"]
        query = raw_request.query

        return cls(raw_request, resource, query)

    @staticmethod
    def __get_token(raw_request):
        if "Authorization" in raw_request.headers:
            auth_header = raw_request.headers["Authorization"]
            if auth_header.startswith("Bearer "):
                return auth_header[7:]
        return None

    def __getitem__(self, item):
        return self.request[item]

    def __setitem__(self, key, value):
        self.request[key] = value

    def __delitem__(self, key):
        del self.request[key]

    def __iter__(self):
        return iter(self.request)

    def __len__(self):
        return len(self.request)

    def __repr__(self):
        return "API Request: " + str(self.request)

    def clone(self) -> "SlackApiRequest":
        return self.__class__(
            copy.deepcopy(self.request),
            copy.deepcopy(self.resource),
            copy.deepcopy(self.query),
        )
