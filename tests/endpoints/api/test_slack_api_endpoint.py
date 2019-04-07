import json

import pytest
from asynctest import CoroutineMock
from sirbot import SirBot

MOCK_USER_NAME = "userName"
MOCK_USER_ID = "U8N6XBL7Q"
AUTH_HEADER = {"Authorization": "Bearer devBackendToken"}

VALID_SLACK_RESPONSE = CoroutineMock(
    return_value={"user": {"exists": True, "id": MOCK_USER_ID, "name": MOCK_USER_NAME}}
)


@pytest.mark.parametrize(
    "headers, status",
    [
        ({"Authorization": "Bearer devBackendToken"}, 200),
        ({"Authorization": "Bearer abc"}, 403),
        (None, 403),
    ],
)
async def test_detect_credentials(bot: SirBot, aiohttp_client, headers, status):
    bot.plugins["slack"].api.query = VALID_SLACK_RESPONSE
    client = await aiohttp_client(bot)

    res = await client.get(
        "/pybot/api/v1/slack/verify?email=test@test.test", headers=headers
    )

    assert res.status == status


async def test_verify_returns_correct_success_params(bot: SirBot, aiohttp_client):
    client = await aiohttp_client(bot)

    bot.plugins["slack"].api.query = VALID_SLACK_RESPONSE

    res = await client.get(
        "/pybot/api/v1/slack/verify?email=test@test.test", headers=AUTH_HEADER
    )
    body = json.loads(await res.text())

    assert body["exists"] is True
    assert body["id"] == MOCK_USER_ID
    assert body["displayName"] == MOCK_USER_NAME
