"""Tests for the Airtable module."""
import pytest

from modules.airtable import (
    daily_programmer_table,
    mentor_table,
    mentorship_affiliations_table,
    mentorship_requests_table,
    mentorship_services_table,
    mentorship_skillsets_table,
    message_text_table,
    scheduled_message_table,
)


@pytest.mark.vcr()
class TestMentorTableBasic:
    """Tests for the mentor table in Airtable."""

    def setup(self) -> None:
        """Set up for the tests."""
        self.desired_fields = {
            "row_id",
            "valid",
            "slack_name",
            "last_modified",
            "last_modified_by",
            "full_name",
            "email",
            "active",
            "skills",
            "max_mentees",
            "bio",
            "notes",
            "time_zone",
            "desired_mentorship_hours_per_week",
            "mentees_worked_with",
            "code_of_conduct_accepted",
            "guidebook_read",
        }
        self.airtable_fields = mentor_table.table_fields

    def test_mentor_table_has_all_desired_fields(self) -> None:
        """Test that the mentor table has all the desired fields."""
        for field in self.airtable_fields:
            assert field in self.desired_fields

    def test_mentor_table_has_correct_number_of_fields(self) -> None:
        """Test that the mentor table has the correct number of fields."""
        assert len(self.airtable_fields) == len(self.desired_fields)


@pytest.mark.vcr()
class TestMentorshipServicesTableBasic:
    """Tests for the mentorship services table in Airtable."""

    def setup(self) -> None:
        """Set up for the tests."""
        self.desired_fields = {
            "name",
            "slug",
            "description",
            "last_modified",
            "last_modified_by",
            "valid",
        }
        self.airtable_fields = mentorship_services_table.table_fields

    def test_mentorship_services_table_has_all_desired_fields(self) -> None:
        """Test that the mentorship services table has all the desired fields."""
        for field in self.airtable_fields:
            assert field in self.desired_fields

    def test_mentorship_services_table_has_correct_number_of_fields(self) -> None:
        """Test that the mentorship services table has the correct number of fields."""
        assert len(self.airtable_fields) == len(self.desired_fields)


@pytest.mark.vcr()
class TestMentorshipSkillsetsTableBasic:
    """Tests for the mentorship skillsets table in Airtable."""

    def setup(self) -> None:
        """Set up for the tests."""
        self.desired_fields = {
            "name",
            "slug",
            "mentors",
            "mentor_requests",
            "last_modified",
            "last_modified_by",
            "valid",
        }
        self.airtable_fields = mentorship_skillsets_table.table_fields

    def test_mentorship_skillsets_table_has_all_desired_fields(self) -> None:
        """Test that the mentorship skillsets table has all the desired fields."""
        for field in self.airtable_fields:
            assert field in self.desired_fields

    def test_mentorship_skillsets_table_has_correct_number_of_fields(self) -> None:
        """Test that the mentorship skillsets table has the correct number of fields."""
        assert len(self.airtable_fields) == len(self.desired_fields)


@pytest.mark.vcr()
class TestMentorshipAffiliationTableBasic:
    """Tests for the mentorship affiliation table in Airtable."""

    def setup(self) -> None:
        """Set up for the tests."""
        self.desired_fields = {
            "name",
            "slug",
            "description",
            "last_modified",
            "last_modified_by",
            "valid",
            "mentor_requests",
        }
        self.airtable_fields = mentorship_affiliations_table.table_fields

    def test_mentorship_affiliation_table_has_all_desired_fields(self) -> None:
        """Test that the mentorship affiliation table has all the desired fields."""
        for field in self.airtable_fields:
            assert field in self.desired_fields

    def test_mentorship_affiliation_table_has_correct_number_of_fields(self) -> None:
        """Test that the mentorship affiliation table has the correct number of fields."""
        assert len(self.airtable_fields) == len(self.desired_fields)


@pytest.mark.vcr()
class TestMentorshipRequestsTableBasic:
    """Tests for the mentorship requests table in Airtable."""

    def setup(self) -> None:
        """Set up for the tests."""
        self.desired_fields = {
            "slack_name",
            "email",
            "service",
            "affiliation",
            "additional_details",
            "skillsets_requested",
            "slack_message_ts",
            "claimed",
            "claimed_by",
            "claimed_on",
            "reset_by",
            "reset_on",
            "reset_count",
            "last_modified",
            "last_modified_by",
            "row_id",
        }
        self.airtable_fields = mentorship_requests_table.table_fields

    def test_mentorship_affiliation_table_has_all_desired_fields(self) -> None:
        """Test that the mentorship affiliation table has all the desired fields."""
        for field in self.airtable_fields:
            assert field in self.desired_fields

    def test_mentorship_affiliation_table_has_correct_number_of_fields(self) -> None:
        """Test that the mentorship affiliation table has the correct number of fields."""
        assert len(self.airtable_fields) == len(self.desired_fields)


@pytest.mark.vcr()
class TestScheduledMessagesTableBasic:
    """Test the scheduled messages table."""

    def setup(self) -> None:
        """Set up the test."""
        self.desired_fields = {
            "name",
            "slug",
            "channel",
            "message_text",
            "initial_date_time_to_send",
            "frequency",
            "last_sent",
            "when_to_send",
            "last_modified",
            "last_modified_by",
            "valid",
        }
        self.airtable_fields = scheduled_message_table.table_fields

    def test_scheduled_message_table_has_all_desired_fields(self) -> None:
        """Ensure that the scheduled message table has the desired fields."""
        for field in self.airtable_fields:
            assert field in self.desired_fields

    def test_scheduled_message_table_has_correct_number_of_fields(self) -> None:
        """Ensure that the scheduled message table has the correct number of fields."""
        assert len(self.airtable_fields) == len(self.desired_fields)


@pytest.mark.vcr()
class TestMessageTextTableBasic:
    """Test the message text table."""

    def setup(self) -> None:
        """Set up the test."""
        self.desired_fields = {
            "name",
            "slug",
            "text",
            "category",
            "last_modified",
            "last_modified_by",
            "valid",
        }
        self.airtable_fields = message_text_table.table_fields

    def test_message_text_table_has_all_desired_fields(self) -> None:
        """Ensure that the message text table has the desired fields."""
        for field in self.airtable_fields:
            assert field in self.desired_fields

    def test_message_test_table_has_correct_number_of_fields(self) -> None:
        """Ensure that the message text table has the desired fields."""
        assert len(self.airtable_fields) == len(self.desired_fields)


@pytest.mark.vcr()
class TestDailyProgrammerTableBasic:
    """Test the Daily Programmer table."""

    def setup(self) -> None:
        """Set up the test class."""
        self.desired_fields = {
            "name",
            "slug",
            "text",
            "category",
            "initial_slack_ts",
            "blocks",
            "initially_posted_on",
            "last_posted_on",
            "posted_count",
            "last_modified",
            "last_modified_by",
            "valid",
        }
        self.airtable_fields = daily_programmer_table.table_fields

    def test_daily_programmer_table_has_all_desired_fields(self) -> None:
        """Ensure that the affiliation table has the desired fields."""
        for field in self.airtable_fields:
            assert field in self.desired_fields

    def test_daily_programmer_table_has_correct_number_of_fields(self) -> None:
        """Ensure that the number of fields in the Airtable matches the number of fields in the desired fields set."""
        assert len(self.airtable_fields) == len(self.desired_fields)
