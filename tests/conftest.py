import copy

import pytest

from pybot import endpoints
from pybot._vendor.sirbot import SirBot
from pybot._vendor.sirbot.plugins.slack import SlackPlugin
from pybot.plugins import AirtablePlugin, APIPlugin
from tests import data

pytest_plugins = ("pybot._vendor.slack.tests.plugin",)


@pytest.fixture(params={**data.Action.__members__})
def action(request):
    if isinstance(request.param, str):
        payload = copy.deepcopy(data.Action[request.param].value)
    else:
        payload = copy.deepcopy(request.param)
    return payload


@pytest.fixture
async def bot() -> SirBot:
    import aiohttp

    b = SirBot()
    # Manually create session for testing (normally done on startup)
    b["http_session"] = aiohttp.ClientSession()

    slack = SlackPlugin(
        token="token",
        verify="supersecuretoken",
        bot_user_id="bot_user_id",
        bot_id="bot_id",
    )
    airtable = AirtablePlugin()
    endpoints.slack.create_endpoints(slack)

    api = APIPlugin()
    endpoints.api.create_endpoints(api)

    b.load_plugin(slack)
    b.load_plugin(airtable)
    b.load_plugin(api)

    # Manually initialize the Slack API for tests that don't use aiohttp_client
    # (which would trigger startup callbacks automatically).
    # The _initialize_api method is idempotent, so it won't overwrite mocks.
    await slack._initialize_api(b)

    yield b

    # Cleanup session
    await b["http_session"].close()


@pytest.fixture
async def slack_bot(bot: SirBot):
    slack = SlackPlugin(
        token="token",
        verify="supersecuretoken",
        bot_user_id="bot_user_id",
        bot_id="bot_id",
    )
    endpoints.slack.create_endpoints(slack)
    bot.load_plugin(slack)
    # Manually initialize the Slack API (idempotent, won't overwrite existing)
    await slack._initialize_api(bot)
    return bot
