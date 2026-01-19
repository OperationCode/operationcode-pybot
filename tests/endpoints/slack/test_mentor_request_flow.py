"""
Tests for mentor request flow action handlers.

Covers: mentor_request_submit, mentor_details_submit, open_details_dialog,
        clear_skillsets, clear_mentor, set_group, set_requested_service,
        set_requested_mentor, add_skillset, claim_mentee
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pybot._vendor.sirbot import SirBot
from pybot.endpoints.slack.actions.mentor_request import (
    add_skillset,
    claim_mentee,
    clear_mentor,
    clear_skillsets,
    mentor_details_submit,
    mentor_request_submit,
    open_details_dialog,
    set_group,
    set_requested_service,
)
from tests.data.blocks import (
    make_claim_mentee_action,
    make_mentor_details_dialog_submission,
    make_mentor_request_action,
)
from tests.fixtures import AirtableMock, SlackMock


class TestMentorRequestSubmit:
    """Tests for mentor_request_submit handler."""

    async def test_submit_success_with_all_fields(
        self, bot: SirBot, slack_mock: SlackMock, airtable_mock: AirtableMock
    ):
        """Successful submission with all required fields."""
        action = make_mentor_request_action(
            user_id="U123",
            user_name="testuser",
            service="Resume Review",
            skillsets=["Python", "AWS"],
            details="Need help with my resume",
            affiliation="veteran",
        )

        slack_mock.setup_user_info("U123", email="test@example.com", name="testuser")
        airtable_mock.setup_service("Resume Review", "recSVC001")

        await mentor_request_submit(action, bot)

        # Should have added a record to Airtable
        airtable_mock.assert_record_added("Mentor Request")

    async def test_submit_with_skillsets_included(
        self, bot: SirBot, slack_mock: SlackMock, airtable_mock: AirtableMock
    ):
        """Submission includes skillsets in the Airtable record."""
        action = make_mentor_request_action(
            user_id="U123",
            service="Resume Review",
            skillsets=["Python", "JavaScript"],
            details="Details here",
            affiliation="veteran",
        )

        slack_mock.setup_user_info("U123", email="test@example.com")
        airtable_mock.setup_service("Resume Review", "recSVC001")

        await mentor_request_submit(action, bot)

        # Verify skillsets were included
        added = airtable_mock.get_added_records("Mentor Request")
        assert len(added) == 1
        fields = added[0][1].get("fields", {})
        assert "Skillsets" in fields

    async def test_submit_validation_failure_missing_service(
        self, bot: SirBot, slack_mock: SlackMock, airtable_mock: AirtableMock
    ):
        """Submission fails validation when service is missing."""
        action = make_mentor_request_action(
            user_id="U123",
            service=None,
            details="Details",
            affiliation="veteran",
        )

        slack_mock.setup_user_info("U123", email="test@example.com")

        await mentor_request_submit(action, bot)

        # Should have updated message with error, not added record
        assert len(airtable_mock.get_added_records("Mentor Request")) == 0
        slack_mock.assert_called_with_method("chat.update")

    async def test_submit_validation_failure_missing_affiliation(
        self, bot: SirBot, slack_mock: SlackMock, airtable_mock: AirtableMock
    ):
        """Submission fails validation when affiliation is missing."""
        action = make_mentor_request_action(
            user_id="U123",
            service="Resume Review",
            details="Details",
            affiliation=None,
        )

        slack_mock.setup_user_info("U123", email="test@example.com")
        airtable_mock.setup_service("Resume Review")

        await mentor_request_submit(action, bot)

        # Should have updated message with error
        assert len(airtable_mock.get_added_records("Mentor Request")) == 0

    async def test_submit_validation_failure_missing_details(
        self, bot: SirBot, slack_mock: SlackMock, airtable_mock: AirtableMock
    ):
        """Submission fails validation when details are missing."""
        action = make_mentor_request_action(
            user_id="U123",
            service="Resume Review",
            details="",
            affiliation="veteran",
        )

        slack_mock.setup_user_info("U123", email="test@example.com")
        airtable_mock.setup_service("Resume Review")

        await mentor_request_submit(action, bot)

        # Should not have added a record
        assert len(airtable_mock.get_added_records("Mentor Request")) == 0

    async def test_submit_fails_when_user_has_no_email(
        self, bot: SirBot, slack_mock: SlackMock, airtable_mock: AirtableMock
    ):
        """Submission fails when user's Slack profile has no email."""
        action = make_mentor_request_action(
            user_id="U123",
            service="Resume Review",
            details="Details",
            affiliation="veteran",
        )

        # Setup user without email
        slack_mock.setup_user_info("U123", email=None)
        airtable_mock.setup_service("Resume Review")

        await mentor_request_submit(action, bot)

        # Should not have added a record
        assert len(airtable_mock.get_added_records("Mentor Request")) == 0
        slack_mock.assert_called_with_method("chat.update")

    async def test_submit_handles_airtable_error(
        self, bot: SirBot, slack_mock: SlackMock, airtable_mock: AirtableMock
    ):
        """Submission handles Airtable errors gracefully."""
        action = make_mentor_request_action(
            user_id="U123",
            service="Resume Review",
            details="Details",
            affiliation="veteran",
        )

        slack_mock.setup_user_info("U123", email="test@example.com")
        airtable_mock.setup_service("Resume Review")
        airtable_mock.setup_error("Mentor Request", "add", "API Error")

        await mentor_request_submit(action, bot)

        # Should have called chat.update to show error
        slack_mock.assert_called_with_method("chat.update")


class TestMentorRequestFieldHandlers:
    """Tests for individual field update handlers."""

    async def test_set_group_updates_affiliation(self, bot: SirBot, slack_mock: SlackMock):
        """set_group handler updates affiliation in the message."""
        action = make_mentor_request_action()
        action["actions"][0]["selected_option"] = {
            "value": "spouse",
            "text": {"type": "plain_text", "text": "Spouse"},
        }

        await set_group(action, bot)

        slack_mock.assert_called_with_method("chat.update")

    async def test_set_requested_service_updates_service(self, bot: SirBot, slack_mock: SlackMock):
        """set_requested_service handler updates service in the message."""
        action = make_mentor_request_action()
        action["actions"][0]["selected_option"] = {
            "value": "Mock Interview",
            "text": {"type": "plain_text", "text": "Mock Interview"},
        }

        await set_requested_service(action, bot)

        slack_mock.assert_called_with_method("chat.update")

    async def test_add_skillset_appends_skillset(self, bot: SirBot, slack_mock: SlackMock):
        """add_skillset handler adds a skillset to the request."""
        action = make_mentor_request_action(skillsets=["Python"])
        action["actions"][0]["selected_option"] = {
            "value": "AWS",
            "text": {"type": "plain_text", "text": "AWS"},
        }

        await add_skillset(action, bot)

        slack_mock.assert_called_with_method("chat.update")

    async def test_clear_skillsets_removes_all(self, bot: SirBot, slack_mock: SlackMock):
        """clear_skillsets handler removes all skillsets."""
        action = make_mentor_request_action(skillsets=["Python", "AWS", "JavaScript"])

        await clear_skillsets(action, bot)

        slack_mock.assert_called_with_method("chat.update")

    async def test_clear_mentor_removes_mentor(self, bot: SirBot, slack_mock: SlackMock):
        """clear_mentor handler removes the selected mentor."""
        action = make_mentor_request_action()
        # Add a mentor block with initial_option
        action["message"]["blocks"][7]["accessory"]["initial_option"] = {
            "value": "recMENTOR001",
            "text": {"type": "plain_text", "text": "Jane Mentor"},
        }

        await clear_mentor(action, bot)

        slack_mock.assert_called_with_method("chat.update")


class TestMentorDetailsDialog:
    """Tests for mentor details dialog handlers."""

    async def test_open_details_dialog_calls_dialog_open(self, bot: SirBot, slack_mock: SlackMock):
        """open_details_dialog opens a Slack dialog."""
        action = make_mentor_request_action(details="Existing details")
        action["trigger_id"] = "trigger123"

        await open_details_dialog(action, bot)

        slack_mock.assert_called_with_method("dialog.open")

    async def test_submit_details_updates_message(self, bot: SirBot, slack_mock: SlackMock):
        """mentor_details_submit updates the original message with new details."""
        action = make_mentor_details_dialog_submission(
            channel_id="C123",
            ts="123456.789",
            details="My updated detailed request",
        )

        # Mock conversations.history to return the original message
        slack_mock.setup_method_response(
            "conversations.history",
            {"messages": [make_mentor_request_action()["message"]]},
        )

        await mentor_details_submit(action, bot)

        slack_mock.assert_called_with_method("chat.update")


class TestClaimMentee:
    """Tests for claim_mentee handler."""

    async def test_claim_success_updates_airtable(
        self, bot: SirBot, slack_mock: SlackMock, airtable_mock: AirtableMock
    ):
        """Claiming a mentee updates the Airtable record."""
        action = make_claim_mentee_action(
            mentor_id="U123MENTOR",
            record_id="recREQ001",
            is_claim=True,
        )

        slack_mock.setup_user_info("U123MENTOR", email="mentor@example.com")
        airtable_mock.setup_mentor(
            name="Jane Mentor",
            email="mentor@example.com",
            record_id="recMENTOR001",
        )

        await claim_mentee(action, bot)

        # Should have updated the request with the mentor
        assert len(airtable_mock._update_history) > 0

    async def test_claim_shows_warning_when_no_email(
        self, bot: SirBot, slack_mock: SlackMock, airtable_mock: AirtableMock
    ):
        """Claiming shows warning when mentor has no email in profile."""
        action = make_claim_mentee_action(
            mentor_id="U123MENTOR",
            record_id="recREQ001",
            is_claim=True,
        )

        # Setup user without email
        slack_mock.setup_user_info("U123MENTOR", email=None)

        await claim_mentee(action, bot)

        # Should have called chat.update (to show warning)
        slack_mock.assert_called_with_method("chat.update")

    async def test_claim_shows_warning_when_mentor_not_found(
        self, bot: SirBot, slack_mock: SlackMock, airtable_mock: AirtableMock
    ):
        """Claiming shows warning when mentor is not found in Airtable."""
        action = make_claim_mentee_action(
            mentor_id="U123MENTOR",
            record_id="recREQ001",
            is_claim=True,
        )

        slack_mock.setup_user_info("U123MENTOR", email="mentor@example.com")
        # Don't set up the mentor in Airtable - it won't be found

        await claim_mentee(action, bot)

        # Should still update message (with warning)
        slack_mock.assert_called_with_method("chat.update")

    async def test_unclaim_resets_attachment(
        self, bot: SirBot, slack_mock: SlackMock, airtable_mock: AirtableMock
    ):
        """Unclaiming resets the message attachment."""
        action = make_claim_mentee_action(
            mentor_id="U123MENTOR",
            record_id="recREQ001",
            is_claim=False,  # Unclaim
        )

        await claim_mentee(action, bot)

        # Should have updated the message
        slack_mock.assert_called_with_method("chat.update")

    async def test_claim_exception_is_caught(
        self, bot: SirBot, slack_mock: SlackMock, airtable_mock: AirtableMock
    ):
        """Exceptions during claim are caught and logged."""
        action = make_claim_mentee_action(
            mentor_id="U123MENTOR",
            record_id="recREQ001",
            is_claim=True,
        )

        # Make slack query raise an exception
        slack_mock.setup_error_response("users.info", Exception("API Error"))

        # Should not raise - exception is caught
        await claim_mentee(action, bot)


class TestMentorRequestIntegration:
    """Integration tests for the full mentor request flow."""

    async def test_full_flow_submit_to_claim(
        self, bot: SirBot, slack_mock: SlackMock, airtable_mock: AirtableMock
    ):
        """Test the full flow from request submission to mentor claim."""
        # Step 1: User submits request
        submit_action = make_mentor_request_action(
            user_id="U456REQUESTER",
            service="Resume Review",
            skillsets=["Python"],
            details="Need resume help",
            affiliation="veteran",
        )

        slack_mock.setup_user_info("U456REQUESTER", email="requester@example.com")
        airtable_mock.setup_service("Resume Review", "recSVC001")

        await mentor_request_submit(submit_action, bot)

        # Verify request was added
        requests = airtable_mock.get_added_records("Mentor Request")
        assert len(requests) == 1

        # Step 2: Mentor claims the request
        slack_mock.reset()
        claim_action = make_claim_mentee_action(
            mentor_id="U123MENTOR",
            record_id="recREQ001",
            is_claim=True,
        )

        slack_mock.setup_user_info("U123MENTOR", email="mentor@example.com")
        airtable_mock.setup_mentor("Jane Mentor", "mentor@example.com", record_id="recMENTOR001")

        await claim_mentee(claim_action, bot)

        # Verify claim updated Airtable
        assert len(airtable_mock._update_history) > 0
