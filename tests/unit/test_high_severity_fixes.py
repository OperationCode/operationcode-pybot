"""
Unit tests for high severity bug fixes.

These tests cover the edge cases identified in CLAUDE_CODE_REVIEW.md that could
cause crashes or stacktraces in production.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from pybot.endpoints.slack.utils.slash_lunch import LunchCommand
from pybot.plugins.airtable.api import AirtableAPI


class TestLunchCommandEmptyBusinesses:
    """Test Issue #1: Empty businesses array crash in slash_lunch.py"""

    def test_select_random_lunch_with_empty_businesses(self):
        """When Yelp returns no businesses, should return None instead of crashing."""
        cmd = LunchCommand("C123", "U456", "90210", "testuser")

        # Empty businesses array
        response = {"businesses": []}
        result = cmd.select_random_lunch(response)

        assert result is None

    def test_select_random_lunch_with_missing_businesses_key(self):
        """When Yelp response has no businesses key, should return None."""
        cmd = LunchCommand("C123", "U456", "90210", "testuser")

        # Missing businesses key entirely
        response = {}
        result = cmd.select_random_lunch(response)

        assert result is None

    def test_select_random_lunch_with_valid_businesses(self):
        """Normal case with businesses should work."""
        cmd = LunchCommand("C123", "U456", "90210", "testuser")

        response = {
            "businesses": [
                {
                    "name": "Test Restaurant",
                    "location": {"display_address": ["123 Main St", "City, ST 12345"]},
                }
            ]
        }
        result = cmd.select_random_lunch(response)

        assert result is not None
        assert "Test Restaurant" in result["text"]


class TestAirtableAPIEmptyFields:
    """Test Issue #5: Airtable API response key errors in api.py"""

    @pytest.fixture
    def mock_session(self):
        """Create a mock aiohttp session."""
        session = MagicMock()
        return session

    @pytest.fixture
    def airtable_api(self, mock_session):
        """Create an AirtableAPI instance with mocked session."""
        return AirtableAPI(mock_session, "test_api_key", "test_base_key")

    @pytest.mark.asyncio
    async def test_get_all_records_skips_empty_fields(self, airtable_api):
        """Records with empty Name field should be skipped, not crash."""
        # Mock the get method to return records with some missing Name fields
        mock_response = {
            "records": [
                {"id": "rec1", "fields": {"Name": "Service 1"}},
                {"id": "rec2", "fields": {}},  # Empty fields (like row 6 in Services)
                {"id": "rec3", "fields": {"Name": "Service 3"}},
            ]
        }

        with patch.object(airtable_api, "get", return_value=mock_response):
            result = await airtable_api.get_all_records("Services", "Name")

        # Should only return records that have the Name field
        assert result == ["Service 1", "Service 3"]
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_all_records_handles_error_response(self, airtable_api):
        """Error response from Airtable should raise ValueError with helpful message."""
        mock_response = {
            "error": {
                "type": "AUTHENTICATION_REQUIRED",
                "message": "Authentication required",
            }
        }

        with patch.object(airtable_api, "get", return_value=mock_response):
            with pytest.raises(ValueError) as exc_info:
                await airtable_api.get_all_records("Services", "Name")

        assert "AUTHENTICATION_REQUIRED" in str(exc_info.value)
        assert "Personal Access Token" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_name_from_record_id_skips_empty_names(self, airtable_api):
        """Records with empty Name field should be skipped in the cache."""
        mock_response = {
            "records": [
                {"id": "rec1", "fields": {"Name": "Service 1"}},
                {"id": "rec2", "fields": {}},  # No Name field
            ]
        }

        with patch.object(airtable_api, "get", return_value=mock_response):
            # Request a record that exists
            result = await airtable_api.get_name_from_record_id("Services", "rec1")
            assert result == "Service 1"

            # Request a record that doesn't have a Name
            result = await airtable_api.get_name_from_record_id("Services", "rec2")
            assert result is None

    @pytest.mark.asyncio
    async def test_depaginate_records_handles_error(self, airtable_api):
        """Pagination should stop gracefully on error."""
        # First call succeeds, second call returns error
        call_count = 0

        async def mock_get(url, params=None):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return {"records": [{"id": "rec1"}], "offset": "next_page"}
            else:
                return {"error": {"message": "Rate limited"}}

        with patch.object(airtable_api, "get", side_effect=mock_get):
            result = await airtable_api._depaginate_records(
                "http://test", {}, "initial_offset"
            )

        # Should return the records from the first page only
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_row_from_record_id_handles_error_response(self, airtable_api):
        """Error response should return empty dict, not crash."""
        mock_response = {"error": {"message": "Record not found"}}

        with patch.object(airtable_api, "get", return_value=mock_response):
            result = await airtable_api.get_row_from_record_id("Mentors", "rec123")

        assert result == {}

    @pytest.mark.asyncio
    async def test_find_records_handles_error_response(self, airtable_api):
        """Error response should return empty list, not crash."""
        mock_response = {"error": {"message": "Invalid formula"}}

        with patch.object(airtable_api, "get", return_value=mock_response):
            result = await airtable_api.find_records("Services", "Name", "test")

        assert result == []


class TestMentorRequestEmptyService:
    """Test Issue #4: Empty service records IndexError"""

    @pytest.mark.asyncio
    async def test_submit_request_handles_empty_service_records(self):
        """When service is not found in Airtable, should return error dict."""
        from pybot.endpoints.slack.message_templates.mentor_request import MentorRequest

        # Create a mock action with minimal required structure
        mock_action = {
            "message": {"blocks": [{}, {}, {}, {}, {}, {}, {}, {}, {}], "ts": "123"},
            "channel": {"id": "C123"},
        }

        # Mock the blocks to have required structure
        mock_action["message"]["blocks"][2] = {
            "accessory": {"initial_option": {"value": "NonexistentService"}}
        }
        mock_action["message"]["blocks"][4] = {}
        mock_action["message"]["blocks"][5] = {"fields": [{"text": "test details"}]}
        mock_action["message"]["blocks"][6] = {
            "accessory": {"initial_option": {"value": "veteran"}}
        }

        request = MentorRequest(mock_action)

        # Mock airtable that returns empty records
        mock_airtable = AsyncMock()
        mock_airtable.find_records.return_value = []

        result = await request.submit_request("testuser", "test@example.com", mock_airtable)

        assert "error" in result
        assert result["error"]["type"] == "SERVICE_NOT_FOUND"


class TestEmptyMentorDict:
    """Test Issue #6: Empty mentor dict KeyError in airtable/utils.py"""

    @pytest.mark.asyncio
    async def test_get_requested_mentor_handles_empty_mentor(self):
        """When mentor record is empty dict, should return None."""
        from pybot.endpoints.airtable.utils import _get_requested_mentor

        mock_slack = AsyncMock()
        mock_airtable = AsyncMock()
        mock_airtable.get_row_from_record_id.return_value = {}  # Empty dict

        result = await _get_requested_mentor("rec123", mock_slack, mock_airtable)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_requested_mentor_handles_missing_email(self):
        """When mentor record has no Email field, should return None."""
        from pybot.endpoints.airtable.utils import _get_requested_mentor

        mock_slack = AsyncMock()
        mock_airtable = AsyncMock()
        mock_airtable.get_row_from_record_id.return_value = {
            "Name": "John Doe"
        }  # No Email field

        result = await _get_requested_mentor("rec123", mock_slack, mock_airtable)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_matching_skillset_mentors_handles_missing_email(self):
        """Mentors without email should fall back to Slack Name."""
        from pybot.endpoints.airtable.utils import _get_matching_skillset_mentors

        mock_slack = AsyncMock()
        mock_airtable = AsyncMock()
        mock_airtable.find_mentors_with_matching_skillsets.return_value = [
            {"Slack Name": "johndoe"},  # No Email
            {"Email": "jane@example.com", "Slack Name": "janedoe"},
        ]
        mock_slack.query.return_value = {"user": {"id": "U123"}}

        result = await _get_matching_skillset_mentors("python", mock_slack, mock_airtable)

        # Should include both mentors
        assert len(result) == 2
        assert "<@johndoe>" in result  # Used Slack Name as fallback
        assert "<@U123>" in result  # Used email lookup


class TestMissingEmailKeyError:
    """Test Issue #3: Missing email KeyError in multiple locations"""

    @pytest.mark.asyncio
    async def test_link_backend_user_handles_missing_email(self):
        """When user has no email in profile, should return early without error."""
        from pybot.endpoints.slack.utils.event_utils import link_backend_user

        mock_slack_api = AsyncMock()
        mock_slack_api.query.return_value = {
            "user": {"profile": {}}  # No email field
        }
        mock_session = AsyncMock()

        # Should not raise, should return early
        await link_backend_user("U123", {}, mock_slack_api, mock_session)

        # Session.patch should not have been called
        mock_session.patch.assert_not_called()
