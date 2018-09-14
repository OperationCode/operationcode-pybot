import pytest
import asynctest
from sirbot import SirBot
from sirbot.plugins.slack import SlackPlugin

from pybot import endpoints


@pytest.fixture
def bot():
    b = SirBot()
    slack = SlackPlugin(
        token='token',
        verify='supersecuretoken',
        bot_user_id='bot_user_id',
        bot_id='bot_id'
    )
    b.load_plugin(slack)
    return b


@pytest.fixture
def team_join_event():
    pass


async def test_team_join_handler_exists(bot):
    endpoints.slack.create_endpoints(bot["plugins"]["slack"])

    assert asynctest.asyncio.iscoroutinefunction(
        bot["plugins"]["slack"].routers["event"]._routes["team_join"]['*']['*'][0][0]
    )