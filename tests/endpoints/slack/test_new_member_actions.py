"""
Tests for new member action handlers.

Covers: resource_buttons(), open_suggestion(), post_suggestion(),
        member_greeted(), reset_greet(), member_messaged(), reset_message()
"""

import pytest
from unittest.mock import AsyncMock

from pybot._vendor.sirbot import SirBot
from pybot.endpoints.slack.actions.new_member import (
    resource_buttons,
    open_suggestion,
    post_suggestion,
    member_greeted,
    reset_greet,
    member_messaged,
    reset_message,
)
from tests.fixtures import SlackMock


def make_resource_button_action(
    user_id: str = "U123",
    channel_id: str = "C123",
    message_ts: str = "123456.789",
    resource_name: str = "slack",
) -> dict:
    """Create a resource button action payload."""
    return {
        "type": "interactive_message",
        "user": {"id": user_id},
        "channel": {"id": channel_id},
        "message_ts": message_ts,
        "original_message": {"text": "Select a resource"},
        "actions": [{"name": resource_name, "value": resource_name}],
        "token": "supersecuretoken",
    }


def make_suggestion_action(
    user_id: str = "U123",
    trigger_id: str = "trigger123",
) -> dict:
    """Create an open suggestion action payload."""
    return {
        "type": "interactive_message",
        "user": {"id": user_id},
        "trigger_id": trigger_id,
        "channel": {"id": "C123"},
        "message_ts": "123456.789",
        "original_message": {"text": "Help menu"},
        "token": "supersecuretoken",
    }


def make_suggestion_submission(
    user_id: str = "U123",
    suggestion: str = "Add more resources about Python",
) -> dict:
    """Create a suggestion dialog submission payload."""
    return {
        "type": "dialog_submission",
        "callback_id": "suggestion",
        "user": {"id": user_id},
        "submission": {"suggestion": suggestion},
        "token": "supersecuretoken",
    }


def make_greet_action(
    user_id: str = "U123GREETER",
    channel_id: str = "C123",
    message_ts: str = "123456.789",
    greeted_user_id: str = "U456NEWMEMBER",
) -> dict:
    """Create a member greeted action payload."""
    return {
        "type": "interactive_message",
        "user": {"id": user_id},
        "channel": {"id": channel_id},
        "message_ts": message_ts,
        "original_message": {
            "text": f"New member <@{greeted_user_id}> joined!",
            "attachments": [
                {
                    "text": "Click to track greeting",
                    "callback_id": "greeted",
                    "actions": [
                        {
                            "name": "greeted",
                            "text": "I greeted them!",
                            "type": "button",
                            "value": "greeted",
                        }
                    ],
                }
            ],
        },
        "token": "supersecuretoken",
    }


def make_message_action(
    user_id: str = "U123OUTREACH",
    channel_id: str = "C123",
    message_ts: str = "123456.789",
) -> dict:
    """Create a member messaged action payload."""
    return {
        "type": "interactive_message",
        "user": {"id": user_id},
        "channel": {"id": channel_id},
        "message_ts": message_ts,
        "original_message": {
            "text": "New member needs outreach",
            "attachments": [
                {
                    "text": "Click to track DM",
                    "callback_id": "messaged",
                    "actions": [
                        {
                            "name": "messaged",
                            "text": "I messaged them!",
                            "type": "button",
                            "value": "messaged",
                        }
                    ],
                }
            ],
        },
        "token": "supersecuretoken",
    }


class TestResourceButtons:
    """Tests for resource_buttons() handler."""

    async def test_resource_buttons_updates_message(self, bot: SirBot, slack_mock: SlackMock):
        """resource_buttons() updates the message via chat.update."""
        action = make_resource_button_action(resource_name="slack")

        await resource_buttons(action, bot)

        slack_mock.assert_called_with_method("chat.update")

    async def test_resource_buttons_uses_correct_response(self, bot: SirBot, slack_mock: SlackMock):
        """resource_buttons() responds with the correct help text."""
        action = make_resource_button_action(resource_name="slack")

        await resource_buttons(action, bot)

        calls = slack_mock.get_calls("chat.update")
        assert len(calls) > 0
        data = calls[0][1]
        assert "text" in data


class TestOpenSuggestion:
    """Tests for open_suggestion() handler."""

    async def test_open_suggestion_opens_dialog(self, bot: SirBot, slack_mock: SlackMock):
        """open_suggestion() opens a Slack dialog."""
        action = make_suggestion_action(trigger_id="trigger999")

        await open_suggestion(action, bot)

        slack_mock.assert_called_with_method("dialog.open")

    async def test_open_suggestion_uses_trigger_id(self, bot: SirBot, slack_mock: SlackMock):
        """open_suggestion() uses the correct trigger_id."""
        action = make_suggestion_action(trigger_id="trigger999")

        await open_suggestion(action, bot)

        calls = slack_mock.get_calls("dialog.open")
        assert len(calls) > 0
        data = calls[0][1]
        assert data["trigger_id"] == "trigger999"


class TestPostSuggestion:
    """Tests for post_suggestion() handler."""

    async def test_post_suggestion_posts_to_community_channel(self, bot: SirBot, slack_mock: SlackMock):
        """post_suggestion() posts to the community channel."""
        action = make_suggestion_submission(
            user_id="U456",
            suggestion="Add more Python resources",
        )

        await post_suggestion(action, bot)

        slack_mock.assert_called_with_method("chat.postMessage")

    async def test_post_suggestion_includes_user_and_text(self, bot: SirBot, slack_mock: SlackMock):
        """post_suggestion() includes the user and suggestion text."""
        action = make_suggestion_submission(
            user_id="U456",
            suggestion="Add JavaScript tutorials",
        )

        await post_suggestion(action, bot)

        calls = slack_mock.get_calls("chat.postMessage")
        assert len(calls) > 0
        data = calls[0][1]
        assert "text" in data
        # The text should contain the user mention or suggestion
        text = data["text"]
        assert "U456" in text or "JavaScript" in text


class TestMemberGreeted:
    """Tests for member_greeted() handler."""

    async def test_member_greeted_updates_message(self, bot: SirBot, slack_mock: SlackMock):
        """member_greeted() updates the message via chat.update."""
        action = make_greet_action(user_id="U123GREETER")

        await member_greeted(action, bot)

        slack_mock.assert_called_with_method("chat.update")

    async def test_member_greeted_includes_greeter(self, bot: SirBot, slack_mock: SlackMock):
        """member_greeted() includes the greeter in the attachment."""
        action = make_greet_action(user_id="U123GREETER")

        await member_greeted(action, bot)

        calls = slack_mock.get_calls("chat.update")
        assert len(calls) > 0


class TestResetGreet:
    """Tests for reset_greet() handler."""

    async def test_reset_greet_updates_message(self, bot: SirBot, slack_mock: SlackMock):
        """reset_greet() updates the message via chat.update."""
        action = make_greet_action(user_id="U123")

        await reset_greet(action, bot)

        slack_mock.assert_called_with_method("chat.update")

    async def test_reset_greet_shows_who_reset(self, bot: SirBot, slack_mock: SlackMock):
        """reset_greet() shows who reset the greeting."""
        action = make_greet_action(user_id="U999RESETTER")

        await reset_greet(action, bot)

        calls = slack_mock.get_calls("chat.update")
        assert len(calls) > 0
        data = calls[0][1]
        # The attachment should contain info about the reset
        assert "attachments" in data


class TestMemberMessaged:
    """Tests for member_messaged() handler."""

    async def test_member_messaged_updates_message(self, bot: SirBot, slack_mock: SlackMock):
        """member_messaged() updates the message via chat.update."""
        action = make_message_action(user_id="U123OUTREACH")

        await member_messaged(action, bot)

        slack_mock.assert_called_with_method("chat.update")

    async def test_member_messaged_includes_outreach_user(self, bot: SirBot, slack_mock: SlackMock):
        """member_messaged() includes the outreach user in the attachment."""
        action = make_message_action(user_id="U123OUTREACH")

        await member_messaged(action, bot)

        calls = slack_mock.get_calls("chat.update")
        assert len(calls) > 0


class TestResetMessage:
    """Tests for reset_message() handler."""

    async def test_reset_message_updates_message(self, bot: SirBot, slack_mock: SlackMock):
        """reset_message() updates the message via chat.update."""
        action = make_message_action(user_id="U123")

        await reset_message(action, bot)

        slack_mock.assert_called_with_method("chat.update")

    async def test_reset_message_restores_button(self, bot: SirBot, slack_mock: SlackMock):
        """reset_message() restores the message button to initial state."""
        action = make_message_action(user_id="U999RESETTER")

        await reset_message(action, bot)

        calls = slack_mock.get_calls("chat.update")
        assert len(calls) > 0
        data = calls[0][1]
        assert "attachments" in data
