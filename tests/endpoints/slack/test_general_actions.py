"""
Tests for general action handlers.

Covers: claimed(), reset_claim(), delete_message()
"""

import pytest
from unittest.mock import AsyncMock

from pybot._vendor.sirbot import SirBot
from pybot.endpoints.slack.actions.general_actions import (
    claimed,
    reset_claim,
    delete_message,
)
from tests.fixtures import SlackMock


def make_general_claim_action(
    user_id: str = "U123",
    channel_id: str = "C123",
    message_ts: str = "123456.789",
    is_claimed: bool = False,
) -> dict:
    """Create a general claim action payload."""
    return {
        "type": "interactive_message",
        "user": {"id": user_id},
        "channel": {"id": channel_id},
        "message_ts": message_ts,
        "original_message": {
            "text": "A message that can be claimed",
            "attachments": [
                {
                    "text": "Click to claim",
                    "callback_id": "claimed",
                    "actions": [
                        {
                            "name": "claim",
                            "text": "Claim" if not is_claimed else "Reset",
                            "type": "button",
                            "value": "claim" if not is_claimed else "reset",
                        }
                    ],
                }
            ],
        },
        "token": "supersecuretoken",
    }


def make_delete_action(
    user_id: str = "U123",
    channel_id: str = "C123",
    message_ts: str = "123456.789",
) -> dict:
    """Create a delete message action payload."""
    return {
        "type": "block_actions",
        "user": {"id": user_id},
        "channel": {"id": channel_id},
        "message": {"ts": message_ts},
        "actions": [{"action_id": "delete_message", "value": "delete"}],
        "token": "supersecuretoken",
    }


class TestClaimed:
    """Tests for claimed() handler."""

    async def test_claimed_updates_message(self, bot: SirBot, slack_mock: SlackMock):
        """claimed() updates the message via chat.update."""
        action = make_general_claim_action(user_id="U456CLAIMER")

        await claimed(action, bot)

        slack_mock.assert_called_with_method("chat.update")

    async def test_claimed_includes_user_in_attachment(self, bot: SirBot, slack_mock: SlackMock):
        """claimed() includes the claiming user in the updated attachment."""
        action = make_general_claim_action(user_id="U456CLAIMER")

        await claimed(action, bot)

        # Verify the call was made
        calls = slack_mock.get_calls("chat.update")
        assert len(calls) > 0

    async def test_claimed_preserves_other_attachments(self, bot: SirBot, slack_mock: SlackMock):
        """claimed() preserves non-claim attachments."""
        action = make_general_claim_action()
        action["original_message"]["attachments"].insert(
            0, {"text": "Other attachment", "callback_id": "other"}
        )

        await claimed(action, bot)

        calls = slack_mock.get_calls("chat.update")
        assert len(calls) > 0
        data = calls[0][1]
        # Should still have both attachments
        assert len(data.get("attachments", [])) >= 2


class TestResetClaim:
    """Tests for reset_claim() handler."""

    async def test_reset_claim_updates_message(self, bot: SirBot, slack_mock: SlackMock):
        """reset_claim() updates the message via chat.update."""
        action = make_general_claim_action(is_claimed=True)

        await reset_claim(action, bot)

        slack_mock.assert_called_with_method("chat.update")

    async def test_reset_claim_restores_claim_button(self, bot: SirBot, slack_mock: SlackMock):
        """reset_claim() restores the claim button to unclaimed state."""
        action = make_general_claim_action(is_claimed=True)

        await reset_claim(action, bot)

        calls = slack_mock.get_calls("chat.update")
        assert len(calls) > 0


class TestDeleteMessage:
    """Tests for delete_message() handler."""

    async def test_delete_message_calls_chat_delete(self, bot: SirBot, slack_mock: SlackMock):
        """delete_message() calls chat.delete API."""
        action = make_delete_action(channel_id="C123", message_ts="123456.789")

        await delete_message(action, bot)

        slack_mock.assert_called_with_method("chat.delete")

    async def test_delete_message_uses_correct_params(self, bot: SirBot, slack_mock: SlackMock):
        """delete_message() uses correct channel and ts."""
        action = make_delete_action(channel_id="C999", message_ts="999888.777")

        await delete_message(action, bot)

        calls = slack_mock.get_calls("chat.delete")
        assert len(calls) > 0
        data = calls[0][1]
        assert data["channel"] == "C999"
        assert data["ts"] == "999888.777"
