"""
Tests for Slack message handlers.

Covers: advertise_pybot(), here_bad(), tech_tips(),
        message_changed(), message_deleted()
"""

import logging
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from pybot._vendor.sirbot import SirBot
from pybot._vendor.slack.events import Message
from pybot.endpoints.slack.messages import (
    advertise_pybot,
    here_bad,
    tech_tips,
    message_changed,
    message_deleted,
    not_bot_message,
    not_bot_delete,
)
from tests.fixtures import SlackMock


def make_message_event(
    channel_id: str = "C123",
    user_id: str = "U456",
    text: str = "Hello world",
    channel_type: str = "channel",
    subtype: str | None = None,
) -> dict:
    """Create a basic message event."""
    event = {
        "type": "message",
        "channel": channel_id,
        "user": user_id,
        "text": text,
        "ts": "123456.789",
        "channel_type": channel_type,
    }
    if subtype:
        event["subtype"] = subtype
    return event


def make_edited_message_event(
    channel_id: str = "C123",
    user_id: str = "U456",
    old_text: str = "Original text",
    new_text: str = "Edited text",
) -> dict:
    """Create a message_changed event."""
    return {
        "type": "message",
        "subtype": "message_changed",
        "channel": channel_id,
        "ts": "123456.789001",
        "message": {
            "type": "message",
            "user": user_id,
            "text": new_text,
            "ts": "123456.789",
            "edited": {"user": user_id, "ts": "123456.789001"},
        },
        "previous_message": {
            "type": "message",
            "user": user_id,
            "text": old_text,
            "ts": "123456.789",
        },
    }


def make_deleted_message_event(
    channel_id: str = "C123",
    user_id: str = "U456",
    deleted_text: str = "Deleted message",
) -> dict:
    """Create a message_deleted event."""
    return {
        "type": "message",
        "subtype": "message_deleted",
        "channel": channel_id,
        "ts": "123456.789001",
        "deleted_ts": "123456.789",
        "previous_message": {
            "type": "message",
            "user": user_id,
            "text": deleted_text,
            "ts": "123456.789",
        },
    }


class TestAdvertisePybot:
    """Tests for advertise_pybot() handler."""

    async def test_advertise_pybot_posts_message(self, bot: SirBot, slack_mock: SlackMock):
        """advertise_pybot() posts a message to the channel."""
        event = make_message_event(channel_id="C123", text="!pybot")

        await advertise_pybot(event, bot)

        slack_mock.assert_called_with_method("chat.postMessage")

    async def test_advertise_pybot_includes_source_link(self, bot: SirBot, slack_mock: SlackMock):
        """advertise_pybot() includes link to source code."""
        event = make_message_event(channel_id="C123", text="!pybot")

        await advertise_pybot(event, bot)

        calls = slack_mock.get_calls("chat.postMessage")
        assert len(calls) > 0
        data = calls[0][1]
        assert "source" in data["text"].lower() or "community" in data["text"].lower()


class TestHereBad:
    """Tests for here_bad() handler."""

    async def test_here_bad_responds_in_channel(self, bot: SirBot, slack_mock: SlackMock):
        """here_bad() posts a warning in the channel."""
        event = make_message_event(
            channel_id="C123",
            user_id="U456",
            text="<@here> pay attention!",
            channel_type="channel",
        )

        await here_bad(event, bot)

        slack_mock.assert_called_with_method("chat.postMessage")

    async def test_here_bad_mentions_user(self, bot: SirBot, slack_mock: SlackMock):
        """here_bad() mentions the user who used @here."""
        event = make_message_event(
            channel_id="C123",
            user_id="U789OFFENDER",
            text="<@here> important!",
            channel_type="channel",
        )

        await here_bad(event, bot)

        calls = slack_mock.get_calls("chat.postMessage")
        assert len(calls) > 0
        data = calls[0][1]
        # Should mention the user or say "Hey you"
        assert "<@U789OFFENDER>" in data["text"] or "Hey you" in data["text"]

    async def test_here_bad_ignores_im(self, bot: SirBot, slack_mock: SlackMock):
        """here_bad() does not respond in direct messages."""
        event = make_message_event(
            channel_id="D123",
            text="<@here>",
            channel_type="im",
        )

        await here_bad(event, bot)

        # Should not have posted a message
        calls = slack_mock.get_calls("chat.postMessage")
        assert len(calls) == 0

    async def test_here_bad_handles_missing_user(self, bot: SirBot, slack_mock: SlackMock):
        """here_bad() handles events without a user field."""
        event = make_message_event(
            channel_id="C123",
            text="<@here>",
            channel_type="channel",
        )
        del event["user"]  # Remove user field

        await here_bad(event, bot)

        calls = slack_mock.get_calls("chat.postMessage")
        assert len(calls) > 0
        data = calls[0][1]
        assert "Hey you" in data["text"]


class TestTechTips:
    """Tests for tech_tips() handler."""

    async def test_tech_tips_posts_response(self, bot: SirBot, slack_mock: SlackMock):
        """tech_tips() posts a response when triggered."""
        event = make_message_event(channel_id="C123", user_id="U456", text="!tech python")

        with patch(
            "pybot.endpoints.slack.messages.TechTerms"
        ) as mock_tech:
            mock_instance = MagicMock()
            mock_instance.grab_values = AsyncMock(
                return_value={"message": {"channel": "C123", "text": "Python info"}}
            )
            mock_tech.return_value = mock_instance

            await tech_tips(event, bot)

            slack_mock.assert_called_with_method("chat.postMessage")

    async def test_tech_tips_ignores_bot_messages(self, bot: SirBot, slack_mock: SlackMock):
        """tech_tips() ignores messages from bots."""
        event = make_message_event(channel_id="C123", text="!tech python")
        event["message"] = {"subtype": "bot_message"}

        with patch("pybot.endpoints.slack.messages.TechTerms") as mock_tech:
            await tech_tips(event, bot)

            mock_tech.assert_not_called()


class TestMessageChanged:
    """Tests for message_changed() handler."""

    async def test_message_changed_logs_edit(self, bot: SirBot, caplog):
        """message_changed() logs the edit."""
        event = make_edited_message_event(
            user_id="U456",
            old_text="Original",
            new_text="Edited",
        )

        with caplog.at_level(logging.INFO):
            await message_changed(event, bot)

        assert any("CHANGE_LOGGING: edited" in record.message for record in caplog.records)

    async def test_message_changed_ignores_bot_edits(self, bot: SirBot, caplog):
        """message_changed() ignores edits from bots."""
        event = make_edited_message_event()
        event["message"]["subtype"] = "bot_message"

        with caplog.at_level(logging.INFO):
            await message_changed(event, bot)

        assert not any("CHANGE_LOGGING" in record.message for record in caplog.records)


class TestMessageDeleted:
    """Tests for message_deleted() handler."""

    async def test_message_deleted_logs_deletion(self, bot: SirBot, caplog):
        """message_deleted() logs the deletion."""
        event = make_deleted_message_event(user_id="U456", deleted_text="Deleted text")

        with caplog.at_level(logging.INFO):
            await message_deleted(event, bot)

        assert any("CHANGE_LOGGING: deleted" in record.message for record in caplog.records)

    async def test_message_deleted_ignores_bot_deletions(self, bot: SirBot, caplog):
        """message_deleted() ignores deletions of bot messages."""
        event = make_deleted_message_event()
        event["previous_message"]["bot_id"] = "B123BOT"

        with caplog.at_level(logging.INFO):
            await message_deleted(event, bot)

        assert not any("CHANGE_LOGGING" in record.message for record in caplog.records)


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_not_bot_message_returns_true_for_user_message(self):
        """not_bot_message returns True for regular user messages."""
        event = make_message_event()
        assert not_bot_message(event) is True

    def test_not_bot_message_returns_false_for_bot_message(self):
        """not_bot_message returns False for bot messages."""
        event = make_edited_message_event()
        event["message"]["subtype"] = "bot_message"
        assert not_bot_message(event) is False

    def test_not_bot_delete_returns_true_for_user_delete(self):
        """not_bot_delete returns True for user message deletions."""
        event = make_deleted_message_event()
        assert not_bot_delete(event) is True

    def test_not_bot_delete_returns_false_for_bot_delete(self):
        """not_bot_delete returns False for bot message deletions."""
        event = make_deleted_message_event()
        event["previous_message"]["bot_id"] = "B123BOT"
        assert not_bot_delete(event) is False
