import asyncio

import pytest
import asynctest
from sirbot import SirBot
from sirbot.plugins.slack import SlackPlugin

from pybot import endpoints
from pybot.endpoints.slack.events import create_endpoints, team_join


@pytest.fixture
async def bot(loop):
    b = SirBot(loop=loop)
    slack = SlackPlugin(
        token='token',
        verify='supersecuretoken',
        bot_user_id='bot_user_id',
        bot_id='bot_id',
    )
    b.load_plugin(slack)
    return b


@pytest.fixture
def team_join_event():
    return {
        "token": "supersecuretoken",
        "team_id": "T000AAA0A",
        "api_app_id": "A0AAAAAAA",
        "event": {
            "type": "team_join",
            "channel": "C00000A00",
            "user": {"id": "U0AAAA",
                     "team_id": "T000AAA0A",
                     "name": "test",
                     "real_name": "test testerson",
                     },
            "event_ts": "123456789.000001",
        },
        "type": "event_callback",
        "authed_teams": ["T000AAA0A"],
        "event_id": "AAAAAAA",
        "event_time": 123456789,
    }


async def test_team_join_handler_exists(bot):
    endpoints.slack.create_endpoints(bot["plugins"]["slack"])

    assert asynctest.asyncio.iscoroutinefunction(
        bot["plugins"]["slack"].routers["event"]._routes["team_join"]['*']['*'][0][0]
    )


async def test_slack_event_denies_on_missing_token(mocker, bot, test_client, team_join_event):
    mocker.patch('asyncio.sleep', return_value=asyncio.sleep(0))
    create_endpoints(bot['plugins']['slack'])
    spy = mocker.spy(bot['plugins']['slack'].api, 'query')
    await team_join(team_join_event['event'], bot)

    assert spy.called


