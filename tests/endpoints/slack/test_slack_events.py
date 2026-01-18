import inspect
import logging
from unittest.mock import AsyncMock, patch

from pybot import endpoints
from pybot.endpoints.slack.events import team_join
from pybot._vendor.slack.events import Event
from tests.data.events import MESSAGE_DELETE, MESSAGE_EDIT, PLAIN_MESSAGE, TEAM_JOIN


async def test_team_join_handler_exists(bot):
    endpoints.slack.create_endpoints(bot["plugins"]["slack"])

    assert inspect.iscoroutinefunction(
        bot["plugins"]["slack"].routers["event"]._routes["team_join"]["*"]["*"][0][0]
    )


async def test_edits_are_logged(bot, aiohttp_client, caplog):
    client = await aiohttp_client(bot)

    with caplog.at_level(logging.INFO):
        await client.post("/slack/events", json=MESSAGE_EDIT)
    assert any("CHANGE_LOGGING: edited" in record.message for record in caplog.records)


async def test_deletes_are_logged(bot, aiohttp_client, caplog):
    client = await aiohttp_client(bot)

    with caplog.at_level(logging.INFO):
        await client.post("/slack/events", json=MESSAGE_DELETE)
    assert any("CHANGE_LOGGING: deleted" in record.message for record in caplog.records)


async def test_no_other_messages_logged(bot, aiohttp_client, caplog):
    client = await aiohttp_client(bot)

    with caplog.at_level(logging.INFO):
        await client.post("/slack/events", json=PLAIN_MESSAGE)
    assert not any("CHANGE_LOGGING" in record.message for record in caplog.records)


async def test_team_join_asyncio_gather_does_not_raise_typeerror(bot):
    """
    Regression test for Python 3.14 compatibility.

    In Python 3.14, asyncio.wait() no longer accepts bare coroutines.
    This test verifies that team_join uses asyncio.gather() correctly.
    """
    event = Event.from_http(TEAM_JOIN, verification_token="supersecuretoken")

    with (
        patch("pybot.endpoints.slack.events.asyncio.sleep", new_callable=AsyncMock),
        patch(
            "pybot.endpoints.slack.events.send_user_greetings", new_callable=AsyncMock
        ),
        patch(
            "pybot.endpoints.slack.events.send_community_notification",
            new_callable=AsyncMock,
        ),
        patch(
            "pybot.endpoints.slack.events.get_backend_auth_headers",
            new_callable=AsyncMock,
            return_value={},
        ),
    ):
        # This should not raise TypeError about coroutines
        await team_join(event, bot)
