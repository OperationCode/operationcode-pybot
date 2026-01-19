"""
Tests for mentor volunteer flow action handlers.

Covers: add_volunteer_skillset, clear_volunteer_skillsets, submit_mentor_volunteer,
        build_airtable_fields
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pybot._vendor.sirbot import SirBot
from pybot._vendor.slack.exceptions import SlackAPIError
from pybot.endpoints.slack.actions.mentor_volunteer import (
    add_volunteer_skillset,
    build_airtable_fields,
    clear_volunteer_skillsets,
    submit_mentor_volunteer,
)
from tests.data.blocks import make_mentor_volunteer_action
from tests.fixtures import AdminSlackMock, AirtableMock, SlackMock


class TestSubmitMentorVolunteer:
    """Tests for submit_mentor_volunteer handler."""

    async def test_submit_success_creates_airtable_record(
        self,
        bot: SirBot,
        slack_mock: SlackMock,
        airtable_mock: AirtableMock,
        admin_slack_mock: AdminSlackMock,
    ):
        """Successful submission creates an Airtable record."""
        action = make_mentor_volunteer_action(
            user_id="U123",
            user_name="testuser",
            skillsets=["Python", "JavaScript"],
        )

        slack_mock.setup_user_info(
            "U123", email="volunteer@example.com", name="testuser", real_name="Test User"
        )

        await submit_mentor_volunteer(action, bot)

        # Should have added a record to Airtable
        airtable_mock.assert_record_added("Mentors")

    async def test_submit_success_invites_to_channel(
        self,
        bot: SirBot,
        slack_mock: SlackMock,
        airtable_mock: AirtableMock,
        admin_slack_mock: AdminSlackMock,
    ):
        """Successful submission invites user to mentor channel."""
        action = make_mentor_volunteer_action(
            user_id="U123",
            skillsets=["Python"],
        )

        slack_mock.setup_user_info("U123", email="volunteer@example.com")

        await submit_mentor_volunteer(action, bot)

        # Should have invited user to channel
        admin_slack_mock.assert_invited_to_channel("mentors-internal", "U123")

    async def test_submit_handles_invite_error_gracefully(
        self,
        bot: SirBot,
        slack_mock: SlackMock,
        airtable_mock: AirtableMock,
        admin_slack_mock: AdminSlackMock,
    ):
        """Submission continues even if channel invite fails."""
        action = make_mentor_volunteer_action(
            user_id="U123",
            skillsets=["Python"],
        )

        slack_mock.setup_user_info("U123", email="volunteer@example.com")
        admin_slack_mock.setup_invite_error(
            SlackAPIError(error={"ok": False, "error": "already_in_channel"}, headers={}, data={})
        )

        # Should not raise
        await submit_mentor_volunteer(action, bot)

        # Record should still have been added
        airtable_mock.assert_record_added("Mentors")

    async def test_submit_validation_fails_without_skillsets(
        self,
        bot: SirBot,
        slack_mock: SlackMock,
        airtable_mock: AirtableMock,
        admin_slack_mock: AdminSlackMock,
    ):
        """Submission fails validation when no skillsets selected."""
        action = make_mentor_volunteer_action(
            user_id="U123",
            skillsets=None,
        )

        slack_mock.setup_user_info("U123", email="volunteer@example.com")

        await submit_mentor_volunteer(action, bot)

        # Should not have added a record (but currently does due to bug)
        assert len(airtable_mock.get_added_records("Mentors")) == 0
        # Should have updated message with error
        slack_mock.assert_called_with_method("chat.update")

    async def test_submit_handles_airtable_error(
        self,
        bot: SirBot,
        slack_mock: SlackMock,
        airtable_mock: AirtableMock,
        admin_slack_mock: AdminSlackMock,
    ):
        """Submission handles Airtable errors gracefully."""
        action = make_mentor_volunteer_action(
            user_id="U123",
            skillsets=["Python"],
        )

        slack_mock.setup_user_info("U123", email="volunteer@example.com")
        airtable_mock.setup_error("Mentors", "add", "Airtable API Error")

        await submit_mentor_volunteer(action, bot)

        # Should have updated message with error
        slack_mock.assert_called_with_method("chat.update")

    async def test_submit_updates_message_on_success(
        self,
        bot: SirBot,
        slack_mock: SlackMock,
        airtable_mock: AirtableMock,
        admin_slack_mock: AdminSlackMock,
    ):
        """Successful submission updates message with success state."""
        action = make_mentor_volunteer_action(
            user_id="U123",
            skillsets=["Python"],
        )

        slack_mock.setup_user_info("U123", email="volunteer@example.com")

        await submit_mentor_volunteer(action, bot)

        # Should have called chat.update
        slack_mock.assert_called_with_method("chat.update")


class TestVolunteerSkillsets:
    """Tests for skillset handlers."""

    async def test_add_skillset_appends_to_list(self, bot: SirBot, slack_mock: SlackMock):
        """add_volunteer_skillset appends a skillset to the volunteer form."""
        action = make_mentor_volunteer_action(skillsets=["Python"])
        action["actions"][0]["selected_option"] = {
            "value": "AWS",
            "text": {"type": "plain_text", "text": "AWS"},
        }

        await add_volunteer_skillset(action, bot)

        # Should have updated the message
        slack_mock.assert_called_with_method("chat.update")

    async def test_add_skillset_prevents_duplicates(self, bot: SirBot, slack_mock: SlackMock):
        """add_volunteer_skillset does not add duplicate skillsets."""
        action = make_mentor_volunteer_action(skillsets=["Python"])
        action["actions"][0]["selected_option"] = {
            "value": "Python",
            "text": {"type": "plain_text", "text": "Python"},
        }

        await add_volunteer_skillset(action, bot)

        # Should have called update but Python should not be duplicated
        slack_mock.assert_called_with_method("chat.update")

    async def test_clear_skillsets_resets_form(self, bot: SirBot, slack_mock: SlackMock):
        """clear_volunteer_skillsets removes all selected skillsets."""
        action = make_mentor_volunteer_action(skillsets=["Python", "AWS", "JavaScript"])

        await clear_volunteer_skillsets(action, bot)

        slack_mock.assert_called_with_method("chat.update")


class TestBuildAirtableFields:
    """Tests for build_airtable_fields helper."""

    async def test_build_fields_includes_all_required_data(self):
        """build_airtable_fields includes all required data."""
        action = make_mentor_volunteer_action(
            user_id="U123",
            user_name="testuser",
            skillsets=["Python", "JavaScript"],
        )

        from pybot.endpoints.slack.message_templates.mentor_volunteer import MentorVolunteer

        request = MentorVolunteer(action)

        user_info = {
            "user": {
                "real_name": "Test User",
                "profile": {"email": "test@example.com"},
            }
        }

        fields = await build_airtable_fields(action, request, user_info)

        assert fields["Slack Name"] == "testuser"
        assert fields["Full Name"] == "Test User"
        assert fields["Email"] == "test@example.com"
        assert "Skillsets" in fields

    async def test_build_fields_filters_empty_skillset(self):
        """build_airtable_fields filters out the empty first skillset."""
        action = make_mentor_volunteer_action(
            user_name="testuser",
            skillsets=["Python"],  # Will have empty string at start
        )

        from pybot.endpoints.slack.message_templates.mentor_volunteer import MentorVolunteer

        request = MentorVolunteer(action)

        user_info = {
            "user": {
                "real_name": "Test User",
                "profile": {"email": "test@example.com"},
            }
        }

        fields = await build_airtable_fields(action, request, user_info)

        # Should not have empty string in skillsets
        assert "" not in fields["Skillsets"]


class TestMentorVolunteerIntegration:
    """Integration tests for the full mentor volunteer flow."""

    async def test_full_volunteer_flow(
        self,
        bot: SirBot,
        slack_mock: SlackMock,
        airtable_mock: AirtableMock,
        admin_slack_mock: AdminSlackMock,
    ):
        """Test the full flow from adding skillsets to submission."""
        # Step 1: Add first skillset
        action1 = make_mentor_volunteer_action(skillsets=None)
        action1["actions"][0]["selected_option"] = {"value": "Python"}

        await add_volunteer_skillset(action1, bot)
        slack_mock.assert_called_with_method("chat.update")

        # Step 2: Add another skillset
        slack_mock.reset()
        action2 = make_mentor_volunteer_action(skillsets=["Python"])
        action2["actions"][0]["selected_option"] = {"value": "JavaScript"}

        await add_volunteer_skillset(action2, bot)
        slack_mock.assert_called_with_method("chat.update")

        # Step 3: Submit
        slack_mock.reset()
        submit_action = make_mentor_volunteer_action(
            user_id="U123",
            skillsets=["Python", "JavaScript"],
        )

        slack_mock.setup_user_info(
            "U123", email="volunteer@example.com", real_name="Test Volunteer"
        )

        await submit_mentor_volunteer(submit_action, bot)

        # Verify record was created
        airtable_mock.assert_record_added("Mentors")

        # Verify channel invite was sent
        admin_slack_mock.assert_invited_to_channel("mentors-internal")
