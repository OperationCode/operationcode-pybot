"""
Tests for Slack event handlers.

Covers: team_join flow, message edit/delete logging, greeting messages,
        community notifications, and backend user linking.
"""

import inspect
import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pybot import endpoints
from pybot.endpoints.slack.events import team_join
from pybot.endpoints.slack.utils.event_utils import (
    build_messages,
    send_user_greetings,
    send_community_notification,
    link_backend_user,
    get_backend_auth_headers,
)
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


# ============================================================================
# Additional Team Join Flow Tests
# ============================================================================


class TestBuildMessages:
    """Tests for build_messages utility function."""

    def test_build_messages_returns_five_messages(self):
        """build_messages returns exactly 5 messages."""
        messages = build_messages("U123TEST")
        assert len(messages) == 5

    def test_build_messages_first_is_initial_greeting(self):
        """First message is the initial greeting to the user."""
        messages = build_messages("U123TEST")
        initial = messages[0]

        assert initial["channel"] == "U123TEST"
        assert "text" in initial

    def test_build_messages_includes_user_id_in_community_notification(self):
        """Community notification includes the user ID."""
        messages = build_messages("U456NEWUSER")
        community = messages[3]

        assert "<@U456NEWUSER>" in community["text"]

    def test_build_messages_community_has_greet_attachment(self):
        """Community message has 'not greeted' attachment."""
        messages = build_messages("U123TEST")
        community = messages[3]

        assert "attachments" in community


class TestSendUserGreetings:
    """Tests for send_user_greetings utility function."""

    async def test_send_user_greetings_posts_all_messages(self):
        """send_user_greetings posts all provided messages."""
        mock_api = AsyncMock()

        messages = [
            {"channel": "U123", "text": "Message 1"},
            {"channel": "U123", "text": "Message 2"},
            {"channel": "U123", "text": "Message 3"},
        ]

        await send_user_greetings(messages, mock_api)

        assert mock_api.query.call_count == 3


class TestSendCommunityNotification:
    """Tests for send_community_notification utility function."""

    async def test_send_community_notification_posts_message(self):
        """send_community_notification posts the message."""
        mock_api = AsyncMock()
        mock_api.query.return_value = {"ok": True, "ts": "123456.789"}

        message = {"channel": "C123COMMUNITY", "text": "New member joined!"}

        result = await send_community_notification(message, mock_api)

        mock_api.query.assert_called_once()
        assert result == {"ok": True, "ts": "123456.789"}


class TestLinkBackendUser:
    """Tests for link_backend_user utility function."""

    async def test_link_backend_user_handles_missing_email(self):
        """link_backend_user returns early when user has no email."""
        mock_slack_api = AsyncMock()
        mock_slack_api.query.return_value = {
            "user": {"profile": {}}  # No email
        }
        mock_session = AsyncMock()

        await link_backend_user("U123", {"Authorization": "Bearer token"}, mock_slack_api, mock_session)

        # Should not call session.patch when no email
        mock_session.patch.assert_not_called()

    async def test_link_backend_user_calls_backend_api(self):
        """link_backend_user calls the backend API with correct params."""
        mock_slack_api = AsyncMock()
        mock_slack_api.query.return_value = {
            "user": {"profile": {"email": "user@example.com"}}
        }

        mock_response = AsyncMock()
        mock_response.json.return_value = {"success": True}

        mock_session = MagicMock()
        mock_session.patch.return_value.__aenter__.return_value = mock_response

        await link_backend_user(
            "U123",
            {"Authorization": "Bearer token"},
            mock_slack_api,
            mock_session
        )

        mock_session.patch.assert_called_once()


class TestGetBackendAuthHeaders:
    """Tests for get_backend_auth_headers utility function."""

    async def test_get_backend_auth_headers_returns_empty_on_error(self):
        """get_backend_auth_headers returns empty dict on auth failure."""
        mock_response = AsyncMock()
        mock_response.status = 401

        mock_session = MagicMock()
        mock_session.post.return_value.__aenter__.return_value = mock_response

        result = await get_backend_auth_headers(mock_session)

        assert result == {}

    async def test_get_backend_auth_headers_returns_headers_on_success(self):
        """get_backend_auth_headers returns auth headers on success."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"token": "jwt_token_here"}

        mock_session = MagicMock()
        mock_session.post.return_value.__aenter__.return_value = mock_response

        result = await get_backend_auth_headers(mock_session)

        assert "Authorization" in result
        assert "Bearer" in result["Authorization"]
