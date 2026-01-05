"""Unit tests for action message builders."""

import pytest

from pybot.endpoints.slack.utils.action_messages import (
    base_response,
    claimed_attachment,
    not_claimed_attachment,
)


class TestActionMessages:
    """Test message attachment builders."""

    def test_not_claimed_attachment_structure(self):
        attachment = not_claimed_attachment()

        assert "callback_id" in attachment
        assert "actions" in attachment
        assert isinstance(attachment["actions"], list)

    def test_claimed_attachment_includes_user(self):
        attachment = claimed_attachment("U12345")

        assert "callback_id" in attachment
        # Should mention the user who claimed
        assert "U12345" in str(attachment)

    def test_base_response_extracts_required_fields(self):
        mock_action = {
            "channel": {"id": "C123"},
            "message_ts": "123456.789",
            "original_message": {
                "text": "Test message"
            }
        }

        response = base_response(mock_action)

        assert response["channel"] == "C123"
        assert response["ts"] == "123456.789"
        assert response["text"] == "Test message"
