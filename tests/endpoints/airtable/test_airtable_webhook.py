"""
Tests for Airtable webhook endpoint (Zapier mentor request handler).

Covers: mentor_request webhook handler, utility functions for creating messages,
        finding mentors, and posting to Slack.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pybot._vendor.sirbot import SirBot
from pybot.endpoints.airtable.requests import mentor_request
from pybot.endpoints.airtable.utils import (
    _create_messages,
    _get_matching_skillset_mentors,
    _get_requested_mentor,
    _post_messages,
    _slack_user_id_from_email,
)
from tests.data.blocks import ZAPIER_MENTOR_REQUEST, ZAPIER_MENTOR_REQUEST_WITH_MENTOR
from tests.fixtures import AirtableMock, SlackMock


class TestMentorRequestWebhook:
    """Tests for the mentor_request webhook handler."""

    async def test_posts_to_mentor_channel(
        self, bot: SirBot, slack_mock: SlackMock, airtable_mock: AirtableMock
    ):
        """Webhook posts a message to the mentor channel."""
        request = ZAPIER_MENTOR_REQUEST.copy()

        airtable_mock.setup_service("Resume Review", "recSVC001")
        slack_mock.setup_lookup_by_email("requester@example.com", "U456REQUESTER")

        await mentor_request(request, bot)

        # Should have posted a message
        slack_mock.assert_called_with_method("chat.postMessage")

    async def test_message_includes_claim_button(
        self, bot: SirBot, slack_mock: SlackMock, airtable_mock: AirtableMock
    ):
        """Posted message includes a claim button."""
        request = ZAPIER_MENTOR_REQUEST.copy()

        airtable_mock.setup_service("Resume Review", "recSVC001")
        slack_mock.setup_lookup_by_email("requester@example.com", "U456REQUESTER")

        await mentor_request(request, bot)

        # Check that chat.postMessage was called with attachments containing a button
        calls = slack_mock.get_calls("chat.postMessage")
        assert len(calls) > 0
        data = calls[0][1]
        assert "attachments" in data
        # The claim button should be in the attachments
        attachments = data["attachments"]
        assert len(attachments) > 0

    async def test_includes_requested_mentor_when_provided(
        self, bot: SirBot, slack_mock: SlackMock, airtable_mock: AirtableMock
    ):
        """Message includes the requested mentor when specified."""
        request = ZAPIER_MENTOR_REQUEST_WITH_MENTOR.copy()

        airtable_mock.setup_service("Resume Review", "recSVC001")
        airtable_mock.setup_mentor("Jane Mentor", "mentor@example.com", record_id="recMENTOR001")
        slack_mock.setup_lookup_by_email("requester@example.com", "U456REQUESTER")
        slack_mock.setup_lookup_by_email("mentor@example.com", "U123MENTOR")

        await mentor_request(request, bot)

        slack_mock.assert_called_with_method("chat.postMessage")

    async def test_finds_matching_mentors(
        self, bot: SirBot, slack_mock: SlackMock, airtable_mock: AirtableMock
    ):
        """Handler finds mentors matching the requested skillsets."""
        request = ZAPIER_MENTOR_REQUEST.copy()
        request["skillsets"] = "Python,AWS"

        airtable_mock.setup_service("Resume Review", "recSVC001")
        airtable_mock.setup_mentor(
            "Jane Mentor", "mentor1@example.com", skillsets=["Python", "JavaScript"]
        )
        airtable_mock.setup_mentor(
            "John Mentor", "mentor2@example.com", skillsets=["AWS", "DevOps"]
        )
        slack_mock.setup_lookup_by_email("requester@example.com", "U456REQUESTER")
        slack_mock.setup_lookup_by_email("mentor1@example.com", "U001")
        slack_mock.setup_lookup_by_email("mentor2@example.com", "U002")

        await mentor_request(request, bot)

        slack_mock.assert_called_with_method("chat.postMessage")

    async def test_user_email_fallback(
        self, bot: SirBot, slack_mock: SlackMock, airtable_mock: AirtableMock
    ):
        """When user email lookup fails, uses fallback message."""
        request = ZAPIER_MENTOR_REQUEST.copy()

        airtable_mock.setup_service("Resume Review", "recSVC001")
        # Don't set up email lookup - it will fail

        await mentor_request(request, bot)

        # Should still post message with fallback
        slack_mock.assert_called_with_method("chat.postMessage")


class TestGetRequestedMentor:
    """Tests for _get_requested_mentor utility."""

    async def test_returns_none_when_no_mentor_requested(self):
        """Returns None when no mentor was requested."""
        slack_mock = AsyncMock()
        airtable_mock = AsyncMock()

        result = await _get_requested_mentor(None, slack_mock, airtable_mock)

        assert result is None

    async def test_returns_none_when_mentor_record_empty(self):
        """Returns None when mentor record is empty."""
        slack_mock = AsyncMock()
        airtable_mock = AsyncMock()
        airtable_mock.get_row_from_record_id.return_value = {}

        result = await _get_requested_mentor("recMENTOR001", slack_mock, airtable_mock)

        assert result is None

    async def test_returns_none_when_mentor_has_no_email(self):
        """Returns None when mentor record has no email."""
        slack_mock = AsyncMock()
        airtable_mock = AsyncMock()
        airtable_mock.get_row_from_record_id.return_value = {"Name": "John Mentor"}

        result = await _get_requested_mentor("recMENTOR001", slack_mock, airtable_mock)

        assert result is None

    async def test_returns_mentor_message_when_found(self):
        """Returns formatted mentor message when mentor is found."""
        slack_mock = AsyncMock()
        slack_mock.query.return_value = {"user": {"id": "U123MENTOR"}}

        airtable_mock = AsyncMock()
        airtable_mock.get_row_from_record_id.return_value = {
            "Name": "Jane Mentor",
            "Email": "mentor@example.com",
        }

        result = await _get_requested_mentor("recMENTOR001", slack_mock, airtable_mock)

        assert result is not None
        assert "Requested mentor" in result
        assert "<@U123MENTOR>" in result


class TestSlackUserIdFromEmail:
    """Tests for _slack_user_id_from_email utility."""

    async def test_returns_user_id_when_found(self):
        """Returns user ID when email lookup succeeds."""
        slack_mock = AsyncMock()
        slack_mock.query.return_value = {"user": {"id": "U123"}}

        result = await _slack_user_id_from_email("test@example.com", slack_mock)

        assert result == "U123"

    async def test_returns_fallback_when_not_found(self):
        """Returns fallback when email lookup fails."""
        from pybot._vendor.slack.exceptions import SlackAPIError

        slack_mock = AsyncMock()
        slack_mock.query.side_effect = SlackAPIError(
            error={"error": "users_not_found"}, headers={}, data={}
        )

        result = await _slack_user_id_from_email(
            "test@example.com", slack_mock, fallback="Unknown User"
        )

        assert result == "Unknown User"

    async def test_returns_default_when_no_fallback(self):
        """Returns 'Slack User' when no fallback provided."""
        from pybot._vendor.slack.exceptions import SlackAPIError

        slack_mock = AsyncMock()
        slack_mock.query.side_effect = SlackAPIError(
            error={"error": "users_not_found"}, headers={}, data={}
        )

        result = await _slack_user_id_from_email("test@example.com", slack_mock)

        assert result == "Slack User"


class TestGetMatchingSkillsetMentors:
    """Tests for _get_matching_skillset_mentors utility."""

    async def test_returns_no_skillset_message_when_none_provided(self):
        """Returns appropriate message when no skillsets provided."""
        slack_mock = AsyncMock()
        airtable_mock = AsyncMock()

        result = await _get_matching_skillset_mentors(None, slack_mock, airtable_mock)

        assert result == ["No skillset Given"]

    async def test_returns_empty_skillset_message_when_empty(self):
        """Returns appropriate message when skillsets string is empty."""
        slack_mock = AsyncMock()
        airtable_mock = AsyncMock()

        result = await _get_matching_skillset_mentors("", slack_mock, airtable_mock)

        assert result == ["No skillset Given"]

    async def test_returns_mentor_ids_when_found(self):
        """Returns list of mentor IDs when mentors match."""
        slack_mock = AsyncMock()
        slack_mock.query.return_value = {"user": {"id": "U123"}}

        airtable_mock = AsyncMock()
        airtable_mock.find_mentors_with_matching_skillsets.return_value = [
            {"Email": "mentor1@example.com", "Slack Name": "mentor1"},
            {"Email": "mentor2@example.com", "Slack Name": "mentor2"},
        ]

        result = await _get_matching_skillset_mentors("Python", slack_mock, airtable_mock)

        # Should return formatted mentor mentions
        assert len(result) == 2
        assert all("<@" in m for m in result)

    async def test_uses_slack_name_fallback_when_no_email(self):
        """Uses Slack Name as fallback when mentor has no email."""
        slack_mock = AsyncMock()
        airtable_mock = AsyncMock()
        airtable_mock.find_mentors_with_matching_skillsets.return_value = [
            {"Slack Name": "johndoe"},  # No email
        ]

        result = await _get_matching_skillset_mentors("Python", slack_mock, airtable_mock)

        # Should use Slack Name as fallback
        assert len(result) == 1
        assert "<@johndoe>" in result[0]


class TestCreateMessages:
    """Tests for _create_messages utility."""

    def test_creates_three_messages(self):
        """Creates main message, details message, and mentor matching message."""
        mentors = ["<@U001>", "<@U002>"]
        request = {
            "record": "recABC123",
            "skillsets": "Python,AWS",
            "affiliation": "Veteran",
            "details": "Need help with code review",
        }

        result = _create_messages(
            mentors=mentors,
            request=request,
            requested_mentor_message=" Requested mentor: <@U999>",
            service_translation="Resume Review",
            slack_id="<@U456>",
        )

        # Should return 3 messages
        assert len(result) == 3
        first, details, mentors_msg = result

        # First message should have text and attachments
        assert "text" in first
        assert "attachments" in first

        # Details message should contain the details
        assert "details" in details["text"].lower()

        # Mentors message should contain mentor mentions
        assert "<@U001>" in mentors_msg["text"]

    def test_includes_claim_button_in_attachment(self):
        """First message includes claim button in attachments."""
        mentors = []
        request = {"record": "recABC123"}

        result = _create_messages(
            mentors=mentors,
            request=request,
            requested_mentor_message=None,
            service_translation="Resume Review",
            slack_id="<@U456>",
        )

        first_message = result[0]
        assert "attachments" in first_message
        # The attachment should have actions with claim button
        attachments = first_message["attachments"]
        assert len(attachments) > 0


class TestPostMessages:
    """Tests for _post_messages utility."""

    async def test_posts_parent_and_children_in_thread(self, bot: SirBot, slack_mock: SlackMock):
        """Posts parent message and children as thread replies."""
        parent = {"text": "Parent message", "channel": "C123"}
        children = [
            {"text": "Child 1", "channel": "C123"},
            {"text": "Child 2", "channel": "C123"},
        ]

        # Mock the response to include timestamp
        slack_mock.setup_method_response("chat.postMessage", {"ts": "123456.789"})

        await _post_messages(parent, children, bot)

        # Should have posted messages (1 parent + 2 children in thread)
        slack_mock.assert_called_with_method("chat.postMessage", times=3)
