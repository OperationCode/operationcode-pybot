"""
Unit tests for MentorRequest model class.

Tests cover property getters/setters, validation logic, skillset handling,
and error attachment handling.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from pybot.endpoints.slack.message_templates.mentor_request import (
    MentorRequest,
    MentorRequestClaim,
    BlockIndex,
)
from tests.data.blocks import make_mentor_request_action, make_claim_mentee_action


class TestMentorRequestProperties:
    """Tests for MentorRequest property getters and setters."""

    def test_service_property_returns_empty_when_not_set(self):
        """Service property returns empty string when no initial_option."""
        action = make_mentor_request_action()
        request = MentorRequest(action)

        assert request.service == ""

    def test_service_property_returns_value_when_set(self):
        """Service property returns the selected value."""
        action = make_mentor_request_action(service="Resume Review")
        request = MentorRequest(action)

        assert request.service == "Resume Review"

    def test_service_setter_updates_block(self):
        """Setting service updates the block structure."""
        action = make_mentor_request_action()
        request = MentorRequest(action)

        new_option = {"text": {"type": "plain_text", "text": "Mock Interview"}, "value": "Mock Interview"}
        request.service = new_option

        assert request.blocks[BlockIndex.SERVICE]["accessory"]["initial_option"] == new_option

    def test_affiliation_property_returns_empty_when_not_set(self):
        """Affiliation property returns empty string when no initial_option."""
        action = make_mentor_request_action()
        request = MentorRequest(action)

        assert request.affiliation == ""

    def test_affiliation_property_returns_value_when_set(self):
        """Affiliation property returns the selected value."""
        action = make_mentor_request_action(affiliation="veteran")
        request = MentorRequest(action)

        assert request.affiliation == "veteran"

    def test_affiliation_setter_updates_block(self):
        """Setting affiliation updates the block structure."""
        action = make_mentor_request_action()
        request = MentorRequest(action)

        new_option = {"text": {"type": "plain_text", "text": "Spouse"}, "value": "spouse"}
        request.affiliation = new_option

        assert request.blocks[BlockIndex.AFFILIATION]["accessory"]["initial_option"] == new_option

    def test_details_property_returns_empty_when_no_fields(self):
        """Details property returns empty string when no fields set."""
        action = make_mentor_request_action()
        request = MentorRequest(action)

        assert request.details == ""

    def test_details_property_returns_value_when_set(self):
        """Details property returns the text from fields."""
        action = make_mentor_request_action(details="Need help with resume")
        request = MentorRequest(action)

        assert request.details == "Need help with resume"

    def test_details_setter_creates_field(self):
        """Setting details creates the field structure."""
        action = make_mentor_request_action()
        request = MentorRequest(action)

        request.details = "New details text"

        assert request.blocks[BlockIndex.COMMENTS]["fields"][0]["text"] == "New details text"


class TestMentorRequestSkillsets:
    """Tests for skillset handling in MentorRequest."""

    def test_skillsets_returns_empty_list_when_no_fields(self):
        """Skillsets property returns empty list when no skillsets selected."""
        action = make_mentor_request_action()
        request = MentorRequest(action)

        assert request.skillsets == []

    def test_skillsets_returns_list_of_names(self):
        """Skillsets property returns list of skillset names."""
        action = make_mentor_request_action(skillsets=["Python", "AWS", "JavaScript"])
        request = MentorRequest(action)

        assert request.skillsets == ["Python", "AWS", "JavaScript"]

    def test_skillset_fields_returns_empty_list_when_no_fields(self):
        """Skillset fields returns empty list when none selected."""
        action = make_mentor_request_action()
        request = MentorRequest(action)

        assert request.skillset_fields == []

    def test_skillset_fields_returns_field_objects(self):
        """Skillset fields returns the full field objects."""
        action = make_mentor_request_action(skillsets=["Python"])
        request = MentorRequest(action)

        fields = request.skillset_fields
        assert len(fields) == 1
        assert fields[0]["type"] == "plain_text"
        assert fields[0]["text"] == "Python"

    def test_add_skillset_appends_new_skillset(self):
        """Adding a skillset appends it to the list."""
        action = make_mentor_request_action(skillsets=["Python"])
        request = MentorRequest(action)

        request.add_skillset("AWS")

        assert "AWS" in request.skillsets
        assert "Python" in request.skillsets

    def test_add_skillset_does_not_duplicate(self):
        """Adding an existing skillset does not create duplicates."""
        action = make_mentor_request_action(skillsets=["Python"])
        request = MentorRequest(action)

        request.add_skillset("Python")

        assert request.skillsets.count("Python") == 1

    def test_add_skillset_creates_proper_field_structure(self):
        """Added skillset has correct field structure."""
        action = make_mentor_request_action()
        request = MentorRequest(action)

        request.add_skillset("DevOps")

        fields = request.skillset_fields
        assert len(fields) == 1
        assert fields[0] == {"type": "plain_text", "text": "DevOps", "emoji": True}

    def test_clear_skillsets_removes_all(self):
        """Clearing skillsets removes all selected skillsets."""
        action = make_mentor_request_action(skillsets=["Python", "AWS", "JavaScript"])
        request = MentorRequest(action)

        request.clear_skillsets()

        assert request.skillsets == []
        assert request.skillset_fields == []

    def test_clear_skillsets_does_nothing_when_empty(self):
        """Clearing skillsets when none exist does not error."""
        action = make_mentor_request_action()
        request = MentorRequest(action)

        # Should not raise
        request.clear_skillsets()

        assert request.skillsets == []


class TestMentorRequestValidation:
    """Tests for MentorRequest validation logic."""

    def test_validate_self_returns_false_when_missing_service(self):
        """Validation fails when service is not set."""
        action = make_mentor_request_action(
            service=None, details="Some details", affiliation="veteran"
        )
        request = MentorRequest(action)

        assert request.validate_self() is False

    def test_validate_self_returns_false_when_missing_affiliation(self):
        """Validation fails when affiliation is not set."""
        action = make_mentor_request_action(
            service="Resume Review", details="Some details", affiliation=None
        )
        request = MentorRequest(action)

        assert request.validate_self() is False

    def test_validate_self_returns_false_when_missing_details(self):
        """Validation fails when details are empty."""
        action = make_mentor_request_action(
            service="Resume Review", details="", affiliation="veteran"
        )
        request = MentorRequest(action)

        assert request.validate_self() is False

    def test_validate_self_returns_true_when_complete(self):
        """Validation passes when all required fields are set."""
        action = make_mentor_request_action(
            service="Resume Review", details="Need help", affiliation="veteran"
        )
        request = MentorRequest(action)

        assert request.validate_self() is True

    def test_validate_self_clears_errors_on_success(self):
        """Successful validation clears any existing error attachments."""
        action = make_mentor_request_action(
            service="Resume Review", details="Need help", affiliation="veteran"
        )
        request = MentorRequest(action)
        request.attachments = [{"text": "Old error"}]

        request.validate_self()

        assert request.attachments == []


class TestMentorRequestErrors:
    """Tests for error handling in MentorRequest."""

    def test_add_errors_creates_warning_attachment(self):
        """Adding errors creates a warning attachment."""
        action = make_mentor_request_action()
        request = MentorRequest(action)

        request.add_errors()

        assert len(request.attachments) == 1
        assert ":warning:" in request.attachments[0]["text"]
        assert request.attachments[0]["color"] == "danger"

    def test_add_errors_mentions_required_fields(self):
        """Error message mentions required fields."""
        action = make_mentor_request_action()
        request = MentorRequest(action)

        request.add_errors()

        text = request.attachments[0]["text"]
        assert "Service" in text
        assert "group" in text or "certification" in text
        assert "comments" in text

    def test_clear_errors_removes_attachments(self):
        """Clearing errors removes all attachments."""
        action = make_mentor_request_action()
        request = MentorRequest(action)
        request.attachments = [{"text": "Error 1"}, {"text": "Error 2"}]

        request.clear_errors()

        assert request.attachments == []


class TestMentorRequestSubmission:
    """Tests for MentorRequest submission methods."""

    @pytest.mark.asyncio
    async def test_submit_request_returns_error_when_service_not_found(self):
        """Submission returns error when service is not found in Airtable."""
        action = make_mentor_request_action(
            service="NonexistentService", details="Details", affiliation="veteran"
        )
        request = MentorRequest(action)

        mock_airtable = AsyncMock()
        mock_airtable.find_records.return_value = []

        result = await request.submit_request("testuser", "test@example.com", mock_airtable)

        assert "error" in result
        assert result["error"]["type"] == "SERVICE_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_submit_request_includes_skillsets_when_present(self):
        """Submission includes skillsets in the Airtable record."""
        action = make_mentor_request_action(
            service="Resume Review",
            skillsets=["Python", "AWS"],
            details="Details",
            affiliation="veteran",
        )
        request = MentorRequest(action)

        mock_airtable = AsyncMock()
        mock_airtable.find_records.return_value = [{"id": "recSVC001"}]
        mock_airtable.add_record.return_value = {"id": "recREQ001"}

        await request.submit_request("testuser", "test@example.com", mock_airtable)

        call_args = mock_airtable.add_record.call_args
        fields = call_args[0][1]["fields"]
        assert "Skillsets" in fields
        assert fields["Skillsets"] == ["Python", "AWS"]

    @pytest.mark.asyncio
    async def test_submit_request_includes_details(self):
        """Submission includes additional details in the Airtable record."""
        action = make_mentor_request_action(
            service="Resume Review",
            details="Please review my resume",
            affiliation="veteran",
        )
        request = MentorRequest(action)

        mock_airtable = AsyncMock()
        mock_airtable.find_records.return_value = [{"id": "recSVC001"}]
        mock_airtable.add_record.return_value = {"id": "recREQ001"}

        await request.submit_request("testuser", "test@example.com", mock_airtable)

        call_args = mock_airtable.add_record.call_args
        fields = call_args[0][1]["fields"]
        assert fields["Additional Details"] == "Please review my resume"

    @pytest.mark.asyncio
    async def test_submit_request_sets_status_available(self):
        """Submission sets status to Available."""
        action = make_mentor_request_action(
            service="Resume Review", details="Details", affiliation="veteran"
        )
        request = MentorRequest(action)

        mock_airtable = AsyncMock()
        mock_airtable.find_records.return_value = [{"id": "recSVC001"}]
        mock_airtable.add_record.return_value = {"id": "recREQ001"}

        await request.submit_request("testuser", "test@example.com", mock_airtable)

        call_args = mock_airtable.add_record.call_args
        fields = call_args[0][1]["fields"]
        assert fields["Status"] == "Available"


class TestMentorRequestClaim:
    """Tests for MentorRequestClaim class."""

    def test_is_claim_returns_true_for_claim_action(self):
        """is_claim returns True when claim button was clicked."""
        action = make_claim_mentee_action(is_claim=True)
        slack_mock = MagicMock()
        airtable_mock = MagicMock()

        claim = MentorRequestClaim(action, slack_mock, airtable_mock)

        assert claim.is_claim() is True

    def test_is_claim_returns_false_for_unclaim_action(self):
        """is_claim returns False when unclaim button was clicked."""
        action = make_claim_mentee_action(is_claim=False)
        slack_mock = MagicMock()
        airtable_mock = MagicMock()

        claim = MentorRequestClaim(action, slack_mock, airtable_mock)

        assert claim.is_claim() is False

    def test_record_returns_airtable_record_id(self):
        """record property returns the Airtable record ID."""
        action = make_claim_mentee_action(record_id="recXYZ789")
        slack_mock = MagicMock()
        airtable_mock = MagicMock()

        claim = MentorRequestClaim(action, slack_mock, airtable_mock)

        assert claim.record == "recXYZ789"

    def test_clicker_returns_user_id(self):
        """clicker property returns the clicking user's ID."""
        action = make_claim_mentee_action(mentor_id="U999MENTOR")
        slack_mock = MagicMock()
        airtable_mock = MagicMock()

        claim = MentorRequestClaim(action, slack_mock, airtable_mock)

        assert claim.clicker == "U999MENTOR"

    @pytest.mark.asyncio
    async def test_claim_request_updates_attachment_when_mentor_found(self):
        """claim_request updates attachment to claimed state when mentor is found."""
        action = make_claim_mentee_action(mentor_id="U123MENTOR")
        slack_mock = MagicMock()
        airtable_mock = MagicMock()
        airtable_mock.update_request = AsyncMock(return_value={"ok": True})

        claim = MentorRequestClaim(action, slack_mock, airtable_mock)
        await claim.claim_request("recMENTOR001")

        assert "claimed by" in claim.attachment["text"].lower() or ":100:" in claim.attachment["text"]
        assert claim.should_update is True

    @pytest.mark.asyncio
    async def test_claim_request_shows_error_when_mentor_not_found(self):
        """claim_request shows error when mentor record is not found."""
        action = make_claim_mentee_action(mentor_id="U123MENTOR")
        slack_mock = MagicMock()
        airtable_mock = MagicMock()
        airtable_mock.update_request = AsyncMock(return_value={"ok": True})

        claim = MentorRequestClaim(action, slack_mock, airtable_mock)
        await claim.claim_request(None)

        assert ":warning:" in claim.attachment["text"]
        assert "not found" in claim.attachment["text"].lower() or "email" in claim.attachment["text"].lower()
        assert claim.should_update is False

    @pytest.mark.asyncio
    async def test_unclaim_request_updates_attachment(self):
        """unclaim_request updates attachment to unclaimed state."""
        action = make_claim_mentee_action(is_claim=False, mentor_id="U123MENTOR")
        slack_mock = MagicMock()
        airtable_mock = MagicMock()
        airtable_mock.update_request = AsyncMock(return_value={"ok": True})

        claim = MentorRequestClaim(action, slack_mock, airtable_mock)
        await claim.unclaim_request()

        # Should show a reset message and have Claim button
        assert "Reset" in claim.attachment["text"] or "reset" in claim.attachment["text"].lower()
        assert any(a.get("value") == "mentee_claimed" for a in claim.attachment.get("actions", []))

    def test_mentee_claimed_attachment_includes_clicker(self):
        """Claimed attachment includes the clicker's user ID."""
        action = make_claim_mentee_action(mentor_id="U123MENTOR", record_id="recABC")
        slack_mock = MagicMock()
        airtable_mock = MagicMock()

        claim = MentorRequestClaim(action, slack_mock, airtable_mock)
        attachment = claim.mentee_claimed_attachment()

        assert "<@U123MENTOR>" in attachment["text"]

    def test_mentee_unclaimed_attachment_has_claim_button(self):
        """Unclaimed attachment has a Claim button."""
        action = make_claim_mentee_action(record_id="recABC")
        slack_mock = MagicMock()
        airtable_mock = MagicMock()

        claim = MentorRequestClaim(action, slack_mock, airtable_mock)
        attachment = claim.mentee_unclaimed_attachment()

        assert len(attachment["actions"]) > 0
        assert attachment["actions"][0]["value"] == "mentee_claimed"
