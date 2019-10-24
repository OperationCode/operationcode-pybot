import copy
import pytest

from sirbot import SirBot
from sirbot.plugins.slack import SlackPlugin
from pybot import endpoints
from pybot.plugins import AirtablePlugin, APIPlugin
from tests import data

pytest_plugins = ("slack.tests.plugin",)


@pytest.fixture(params={**data.Action.__members__})
def action(request):
    if isinstance(request.param, str):
        payload = copy.deepcopy(data.Action[request.param].value)
    else:
        payload = copy.deepcopy(request.param)
    return payload


@pytest.fixture
async def bot(loop) -> SirBot:
    b = SirBot()
    slack = SlackPlugin
    (
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

    return b

@pytest.fixture
def slack_bot(bot: SirBot):
    slack = SlackPlugin
    (
        token="token",
        verify="supersecuretoken",
        bot_user_id="bot_user_id",
        bot_id="bot_id",
    )
    endpoints.slack.create_endpoints(slack)
    bot.load_plugin(slack)
    return bot
