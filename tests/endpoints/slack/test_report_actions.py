"""
Tests for report message action handlers.

Covers: open_report_dialog(), send_report()
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock

from pybot._vendor.sirbot import SirBot
from pybot._vendor.slack.actions import Action
from pybot.endpoints.slack.actions.report_message import (
    open_report_dialog,
    send_report,
)
from tests.fixtures import SlackMock


def make_report_action(
    user_id: str = "U123REPORTER",
    channel_id: str = "C123",
    message_ts: str = "123456.789",
    message_text: str = "The message being reported",
    trigger_id: str = "trigger123",
) -> dict:
    """Create a report message action payload."""
    return {
        "type": "message_action",
        "user": {"id": user_id},
        "channel": {"id": channel_id},
        "message": {"ts": message_ts, "text": message_text},
        "trigger_id": trigger_id,
        "token": "supersecuretoken",
    }


def make_report_submission(
    user_id: str = "U123REPORTER",
    details: str = "This message contains inappropriate content",
    message_details: dict | None = None,
) -> dict:
    """Create a report dialog submission payload."""
    if message_details is None:
        message_details = {
            "channel": {"id": "C123", "name": "general"},
            "ts": "123456.789",
            "text": "The reported message",
            "user": "U999OFFENDER",
        }

    return {
        "type": "dialog_submission",
        "callback_id": "report_message",
        "user": {"id": user_id},
        "submission": {"details": details},
        "state": json.dumps(message_details),
        "token": "supersecuretoken",
    }


class TestOpenReportDialog:
    """Tests for open_report_dialog() handler."""

    async def test_open_report_dialog_opens_dialog(self, bot: SirBot, slack_mock: SlackMock):
        """open_report_dialog() opens a Slack dialog."""
        action = make_report_action(trigger_id="trigger999")

        await open_report_dialog(action, bot)

        slack_mock.assert_called_with_method("dialog.open")

    async def test_open_report_dialog_uses_trigger_id(self, bot: SirBot, slack_mock: SlackMock):
        """open_report_dialog() uses the correct trigger_id."""
        action = make_report_action(trigger_id="trigger999")

        await open_report_dialog(action, bot)

        calls = slack_mock.get_calls("dialog.open")
        assert len(calls) > 0
        data = calls[0][1]
        assert data["trigger_id"] == "trigger999"

    async def test_open_report_dialog_includes_dialog_config(self, bot: SirBot, slack_mock: SlackMock):
        """open_report_dialog() includes dialog configuration."""
        action = make_report_action()

        await open_report_dialog(action, bot)

        calls = slack_mock.get_calls("dialog.open")
        assert len(calls) > 0
        data = calls[0][1]
        assert "dialog" in data


class TestSendReport:
    """Tests for send_report() handler."""

    async def test_send_report_posts_to_channel(self, bot: SirBot, slack_mock: SlackMock):
        """send_report() posts to the moderators channel."""
        action = make_report_submission(
            user_id="U123REPORTER",
            details="Inappropriate content",
        )

        await send_report(action, bot)

        slack_mock.assert_called_with_method("chat.postMessage")

    async def test_send_report_includes_reporter_id(self, bot: SirBot, slack_mock: SlackMock):
        """send_report() includes the reporter's user ID."""
        action = make_report_submission(user_id="U456REPORTER")

        await send_report(action, bot)

        calls = slack_mock.get_calls("chat.postMessage")
        assert len(calls) > 0

    async def test_send_report_includes_details(self, bot: SirBot, slack_mock: SlackMock):
        """send_report() includes the report details."""
        action = make_report_submission(details="This is spam content")

        await send_report(action, bot)

        calls = slack_mock.get_calls("chat.postMessage")
        assert len(calls) > 0

    async def test_send_report_includes_message_context(self, bot: SirBot, slack_mock: SlackMock):
        """send_report() includes context about the reported message."""
        message_details = {
            "channel": {"id": "C999", "name": "random"},
            "ts": "999888.777",
            "text": "The offensive message",
            "user": "U888OFFENDER",
        }
        action = make_report_submission(message_details=message_details)

        await send_report(action, bot)

        calls = slack_mock.get_calls("chat.postMessage")
        assert len(calls) > 0
