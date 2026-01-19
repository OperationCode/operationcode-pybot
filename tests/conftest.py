import copy
from unittest.mock import AsyncMock, MagicMock

import pytest

from pybot import endpoints
from pybot._vendor.sirbot import SirBot
from pybot._vendor.sirbot.plugins.slack import SlackPlugin
from pybot.plugins import AirtablePlugin, APIPlugin
from tests import data
from tests.fixtures import AdminSlackMock, AirtableMock, SlackMock

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

    # Manually initialize API clients for tests that don't use aiohttp_client
    # (which would trigger startup callbacks automatically).
    # The _initialize_api methods are idempotent, so they won't overwrite mocks.
    await slack._initialize_api(b)
    await airtable._initialize_api(b)

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


@pytest.fixture
def slack_mock(bot: SirBot) -> SlackMock:
    """Pre-configured Slack API mock for testing."""
    return SlackMock(bot)


@pytest.fixture
def airtable_mock(bot: SirBot) -> AirtableMock:
    """Pre-configured Airtable API mock for testing."""
    return AirtableMock(bot)


@pytest.fixture
def admin_slack_mock(bot: SirBot) -> AdminSlackMock:
    """Pre-configured admin Slack API mock for channel invites."""
    return AdminSlackMock(bot)


@pytest.fixture
def mock_user_info_with_email():
    """Standard user.info response with email."""
    return {
        "ok": True,
        "user": {
            "id": "U123TEST",
            "name": "testuser",
            "real_name": "Test User",
            "profile": {
                "email": "test@example.com",
                "real_name": "Test User",
            },
        },
    }


@pytest.fixture
def mock_user_info_no_email():
    """User.info response without email (restricted profile)."""
    return {
        "ok": True,
        "user": {
            "id": "U123TEST",
            "name": "testuser",
            "real_name": "Test User",
            "profile": {
                "real_name": "Test User",
            },
        },
    }


@pytest.fixture
def mock_mentor_record():
    """Standard mentor record from Airtable."""
    return {
        "id": "recMENTOR001",
        "fields": {
            "Name": "Jane Mentor",
            "Email": "mentor@example.com",
            "Slack Name": "janementor",
            "Skillsets": ["Python", "JavaScript", "AWS"],
        },
    }


@pytest.fixture
def mock_service_records():
    """Standard service records from Airtable."""
    return [
        {"id": "recSVC001", "fields": {"Name": "Resume Review"}},
        {"id": "recSVC002", "fields": {"Name": "Mock Interview"}},
        {"id": "recSVC003", "fields": {"Name": "Code Review"}},
    ]
