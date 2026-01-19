"""
Unit tests for MentorVolunteer model class.

Tests cover skillset handling, validation, and submission state.
"""

import pytest

from pybot.endpoints.slack.message_templates.mentor_volunteer import (
    MentorVolunteer,
    VolunteerBlockIndex,
)
from tests.data.blocks import make_mentor_volunteer_action


class TestMentorVolunteerProperties:
    """Tests for MentorVolunteer property getters and setters."""

    def test_skillsets_returns_list_when_populated(self):
        """Skillsets property returns list of selected skillsets."""
        action = make_mentor_volunteer_action(skillsets=["Python", "JavaScript"])
        volunteer = MentorVolunteer(action)

        # Note: skillsets are stored as newline-separated text
        skillsets = volunteer.skillsets
        assert "Python" in skillsets
        assert "JavaScript" in skillsets

    def test_skillset_field_text_returns_raw_text(self):
        """skillset_field_text returns the raw text from the field."""
        action = make_mentor_volunteer_action(skillsets=["Python", "AWS"])
        volunteer = MentorVolunteer(action)

        text = volunteer.skillset_field_text
        assert "Python" in text
        assert "AWS" in text

    def test_skillset_field_text_setter_updates_field(self):
        """Setting skillset_field_text updates the underlying field."""
        action = make_mentor_volunteer_action()
        volunteer = MentorVolunteer(action)

        volunteer.skillset_field_text = "DevOps\nKubernetes"

        assert "DevOps" in volunteer.skillset_field_text
        assert "Kubernetes" in volunteer.skillset_field_text


class TestMentorVolunteerSkillsets:
    """Tests for skillset handling in MentorVolunteer."""

    def test_add_skillset_appends_new_skillset(self):
        """Adding a new skillset appends it to the list."""
        action = make_mentor_volunteer_action(skillsets=["Python"])
        volunteer = MentorVolunteer(action)

        volunteer.add_skillset("AWS")

        assert "AWS" in volunteer.skillsets

    def test_add_skillset_does_not_duplicate(self):
        """Adding an existing skillset does not create duplicates."""
        action = make_mentor_volunteer_action(skillsets=["Python"])
        volunteer = MentorVolunteer(action)

        volunteer.add_skillset("Python")

        # Count occurrences
        count = volunteer.skillsets.count("Python")
        assert count == 1

    def test_add_skillset_to_empty_list(self):
        """Adding skillset to empty list works correctly."""
        action = make_mentor_volunteer_action(skillsets=None)
        volunteer = MentorVolunteer(action)

        volunteer.add_skillset("JavaScript")

        assert "JavaScript" in volunteer.skillsets

    def test_clear_skillsets_resets_to_space(self):
        """Clearing skillsets resets the field to a space."""
        action = make_mentor_volunteer_action(skillsets=["Python", "AWS", "JavaScript"])
        volunteer = MentorVolunteer(action)

        volunteer.clear_skillsets()

        # After clearing, the text should be a single space
        assert volunteer.skillset_field_text == " "


class TestMentorVolunteerValidation:
    """Tests for MentorVolunteer validation logic."""

    def test_validate_self_returns_true_with_skillsets(self):
        """Validation passes when skillsets are selected."""
        action = make_mentor_volunteer_action(skillsets=["Python"])
        volunteer = MentorVolunteer(action)

        assert volunteer.validate_self() is True

    def test_validate_self_clears_errors_on_success(self):
        """Successful validation clears any existing error attachments."""
        action = make_mentor_volunteer_action(skillsets=["Python"])
        volunteer = MentorVolunteer(action)
        volunteer.attachments = [{"text": "Old error"}]

        volunteer.validate_self()

        assert volunteer.attachments == []


class TestMentorVolunteerErrors:
    """Tests for error handling in MentorVolunteer."""

    def test_add_errors_creates_warning_attachment(self):
        """Adding errors creates a warning attachment."""
        action = make_mentor_volunteer_action()
        volunteer = MentorVolunteer(action)

        volunteer.add_errors()

        assert len(volunteer.attachments) == 1
        assert ":warning:" in volunteer.attachments[0]["text"]
        assert volunteer.attachments[0]["color"] == "danger"

    def test_add_errors_mentions_skillset_requirement(self):
        """Error message mentions skillset selection requirement."""
        action = make_mentor_volunteer_action()
        volunteer = MentorVolunteer(action)

        volunteer.add_errors()

        text = volunteer.attachments[0]["text"]
        assert "area" in text.lower() or "skillset" in text.lower()

    def test_airtable_error_creates_error_attachment(self):
        """Airtable error creates appropriate error attachment."""
        action = make_mentor_volunteer_action()
        volunteer = MentorVolunteer(action)

        airtable_response = {
            "error": {"type": "INVALID_REQUEST", "message": "Field validation failed"}
        }
        volunteer.airtable_error(airtable_response)

        assert len(volunteer.attachments) == 1
        assert "INVALID_REQUEST" in volunteer.attachments[0]["text"]
        assert "Field validation failed" in volunteer.attachments[0]["text"]
        assert volunteer.attachments[0]["color"] == "danger"


class TestMentorVolunteerSubmission:
    """Tests for submission state handling in MentorVolunteer."""

    def test_on_submit_success_replaces_blocks(self):
        """Successful submission replaces blocks with success message."""
        action = make_mentor_volunteer_action(skillsets=["Python"])
        volunteer = MentorVolunteer(action)

        volunteer.on_submit_success()

        # Should have replaced blocks with success message
        assert len(volunteer.blocks) == 2  # Success message + dismiss button

    def test_on_submit_success_includes_thank_you_message(self):
        """Success message includes thank you text."""
        action = make_mentor_volunteer_action(skillsets=["Python"])
        volunteer = MentorVolunteer(action)

        volunteer.on_submit_success()

        # Find the text block
        text_block = volunteer.blocks[0]
        assert "Thank you" in text_block["text"]["text"]

    def test_on_submit_success_includes_dismiss_button(self):
        """Success message includes a dismiss button."""
        action = make_mentor_volunteer_action(skillsets=["Python"])
        volunteer = MentorVolunteer(action)

        volunteer.on_submit_success()

        # Find the actions block
        actions_block = volunteer.blocks[1]
        assert actions_block["type"] == "actions"
        assert any(e.get("action_id") == "cancel_btn" for e in actions_block.get("elements", []))

    def test_on_submit_success_mentions_mentor_channel(self):
        """Success message mentions the mentor channel."""
        action = make_mentor_volunteer_action(skillsets=["Python"])
        volunteer = MentorVolunteer(action)

        volunteer.on_submit_success()

        text = volunteer.blocks[0]["text"]["text"]
        assert "mentors-internal" in text.lower() or "channel" in text.lower()


class TestMentorVolunteerInitialization:
    """Tests for MentorVolunteer initialization."""

    def test_creates_original_message_if_missing(self):
        """Creates original_message dict if not present in raw action."""
        # Create an action without original_message
        action = make_mentor_volunteer_action()
        if "original_message" in action:
            del action["original_message"]

        volunteer = MentorVolunteer(action)

        # Should have created the key
        assert "original_message" in volunteer

    def test_preserves_existing_original_message(self):
        """Preserves existing original_message if present."""
        action = make_mentor_volunteer_action()
        action["original_message"] = {"custom": "data"}

        volunteer = MentorVolunteer(action)

        assert volunteer.get("original_message", {}).get("custom") == "data"
