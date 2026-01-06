"""
Integration tests for Airtable API READ operations.

These tests use the real Airtable API with production credentials.
Run with: direnv exec /path/to/parent poetry run pytest tests/integration/test_airtable_read.py -v

Environment variables required:
- AIRTABLE_API_KEY: Personal Access Token (starts with 'pat...')
- AIRTABLE_BASE_KEY or AIRTABLE_BASE: Airtable base ID
"""

import os
import pytest
import aiohttp

from pybot.plugins.airtable.api import AirtableAPI


def get_airtable_base_key():
    """Get Airtable base key from env, supporting both var names."""
    return os.environ.get("AIRTABLE_BASE_KEY") or os.environ.get("AIRTABLE_BASE", "")


# Skip all tests if environment variables are not set
pytestmark = pytest.mark.skipif(
    not os.environ.get("AIRTABLE_API_KEY") or not get_airtable_base_key(),
    reason="AIRTABLE_API_KEY and AIRTABLE_BASE_KEY (or AIRTABLE_BASE) must be set for integration tests",
)


@pytest.fixture
async def airtable_api():
    """Create a real AirtableAPI instance with production credentials."""
    async with aiohttp.ClientSession() as session:
        api = AirtableAPI(
            session=session,
            api_key=os.environ.get("AIRTABLE_API_KEY", ""),
            base_key=get_airtable_base_key(),
        )
        yield api


class TestAirtableReadServices:
    """Integration tests for reading from the Services table."""

    @pytest.mark.asyncio
    async def test_get_all_services(self, airtable_api):
        """Verify we can read all services and handle empty Name fields."""
        services = await airtable_api.get_all_records("Services", "Name")

        # Should return a list
        assert isinstance(services, list)

        # Should have at least some services (based on screenshot: 5+ services)
        assert len(services) >= 5

        # All returned items should be non-empty strings
        for service in services:
            assert isinstance(service, str)
            assert len(service) > 0

        # Verify known services exist (from screenshot)
        expected_services = [
            "General Guidance - Voice Chat",
            "General Guidance - Slack Chat",
            "Pair Programming",
            "Code Review",
            "Resume Review",
        ]
        for expected in expected_services:
            assert expected in services, f"Expected service '{expected}' not found"

    @pytest.mark.asyncio
    async def test_get_all_services_raw_records(self, airtable_api):
        """Get raw records to inspect structure."""
        records = await airtable_api.get_all_records("Services")

        assert isinstance(records, list)
        assert len(records) >= 5

        # Each record should have id and fields
        for record in records:
            assert "id" in record
            assert "fields" in record
            # Note: fields may be empty for some records (like row 6)


class TestAirtableReadSkillsets:
    """Integration tests for reading from the Skillsets table."""

    @pytest.mark.asyncio
    async def test_get_all_skillsets(self, airtable_api):
        """Verify we can read all skillsets."""
        skillsets = await airtable_api.get_all_records("Skillsets", "Name")

        # Should return a list
        assert isinstance(skillsets, list)

        # Should have skillsets
        assert len(skillsets) > 0

        # All returned items should be non-empty strings
        for skillset in skillsets:
            assert isinstance(skillset, str)
            assert len(skillset) > 0


class TestAirtableReadMentors:
    """Integration tests for reading from the Mentors table."""

    @pytest.mark.asyncio
    async def test_find_mentors_with_skillsets(self, airtable_api):
        """Verify mentor skillset matching works."""
        # This may return empty list if no mentors match, which is fine
        mentors = await airtable_api.find_mentors_with_matching_skillsets("python")

        assert isinstance(mentors, list)

        # If mentors are returned, verify they have expected fields
        for mentor in mentors:
            assert isinstance(mentor, dict)
            # Should have at least Skillsets field (may not have Email)
            # Note: We now handle missing Email gracefully

    @pytest.mark.asyncio
    async def test_find_records_in_services(self, airtable_api):
        """Verify find_records works for Services table."""
        records = await airtable_api.find_records("Services", "Name", "Code Review")

        assert isinstance(records, list)

        # Should find at least one record (Code Review exists)
        assert len(records) >= 1

        # Verify structure
        for record in records:
            assert "id" in record
            assert "fields" in record


class TestAirtableApiErrorHandling:
    """Integration tests for error handling."""

    @pytest.mark.asyncio
    async def test_invalid_table_name(self, airtable_api):
        """Querying non-existent table should raise ValueError with helpful message."""
        with pytest.raises(ValueError) as exc_info:
            await airtable_api.get_all_records("NonExistentTable12345", "Name")

        # Should include helpful error information
        error_msg = str(exc_info.value)
        assert "Airtable API error" in error_msg

    @pytest.mark.asyncio
    async def test_get_row_nonexistent_record(self, airtable_api):
        """Getting a non-existent record should return empty dict."""
        result = await airtable_api.get_row_from_record_id("Services", "recNONEXISTENT123")

        # Should return empty dict, not crash
        assert result == {}

    @pytest.mark.asyncio
    async def test_find_records_no_matches(self, airtable_api):
        """Finding records with no matches should return empty list."""
        records = await airtable_api.find_records(
            "Services", "Name", "ThisServiceDefinitelyDoesNotExist12345"
        )

        assert isinstance(records, list)
        assert len(records) == 0


class TestAirtableCredentials:
    """Tests to verify API credentials are properly configured."""

    @pytest.mark.asyncio
    async def test_api_key_is_pat(self, airtable_api):
        """Verify the API key is a Personal Access Token (starts with 'pat')."""
        api_key = os.environ.get("AIRTABLE_API_KEY", "")

        assert api_key.startswith("pat"), (
            "AIRTABLE_API_KEY should be a Personal Access Token starting with 'pat...'. "
            "Legacy API keys were deprecated in February 2024."
        )

    @pytest.mark.asyncio
    async def test_can_authenticate(self, airtable_api):
        """Verify we can authenticate and read from Airtable."""
        # Simple authentication test - try to read Services
        try:
            services = await airtable_api.get_all_records("Services", "Name")
            assert isinstance(services, list)
        except ValueError as e:
            if "AUTHENTICATION_REQUIRED" in str(e):
                pytest.fail(
                    "Authentication failed. Ensure AIRTABLE_API_KEY is a valid PAT "
                    "with data.records:read scope and access to the base."
                )
            raise
