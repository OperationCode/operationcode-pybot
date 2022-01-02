import pytest

from modules.airtable import (
    mentor_table,
    mentorship_services_table,
    mentorship_skillsets_table,
    mentorship_affiliations_table,
    mentorship_requests_table,
    scheduled_message_table,
    message_text_table,
    daily_programmer_table,
)


@pytest.mark.vcr()
class TestMentorTableBasic:
    def setup(self):
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
        for field in self.airtable_fields:
            assert field in self.desired_fields

    def test_mentor_table_has_correct_number_of_fields(self) -> None:
        assert len(self.airtable_fields) == len(self.desired_fields)


@pytest.mark.vcr()
class TestMentorshipServicesTableBasic:
    def setup(self):
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
        for field in self.airtable_fields:
            assert field in self.desired_fields

    def test_mentorship_services_table_has_correct_number_of_fields(self) -> None:
        assert len(self.airtable_fields) == len(self.desired_fields)


@pytest.mark.vcr()
class TestMentorshipSkillsetsTableBasic:
    def setup(self):
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
        for field in self.airtable_fields:
            assert field in self.desired_fields

    def test_mentorship_skillsets_table_has_correct_number_of_fields(self) -> None:
        assert len(self.airtable_fields) == len(self.desired_fields)


@pytest.mark.vcr()
class TestMentorshipAffiliationTableBasic:
    def setup(self):
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
        for field in self.airtable_fields:
            assert field in self.desired_fields

    def test_mentorship_affiliation_table_has_correct_number_of_fields(self) -> None:
        assert len(self.airtable_fields) == len(self.desired_fields)


@pytest.mark.vcr()
class TestMentorshipRequestsTableBasic:
    def setup(self):
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
        for field in self.airtable_fields:
            assert field in self.desired_fields

    def test_mentorship_affiliation_table_has_correct_number_of_fields(self) -> None:
        assert len(self.airtable_fields) == len(self.desired_fields)


@pytest.mark.vcr()
class TestScheduledMessagesTableBasic:
    def setup(self):
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

    def test_mentorship_affiliation_table_has_all_desired_fields(self) -> None:
        for field in self.airtable_fields:
            assert field in self.desired_fields

    def test_mentorship_affiliation_table_has_correct_number_of_fields(self) -> None:
        assert len(self.airtable_fields) == len(self.desired_fields)


@pytest.mark.vcr()
class TestMessageTextTableBasic:
    def setup(self):
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

    def test_mentorship_affiliation_table_has_all_desired_fields(self) -> None:
        for field in self.airtable_fields:
            assert field in self.desired_fields

    def test_mentorship_affiliation_table_has_correct_number_of_fields(self) -> None:
        assert len(self.airtable_fields) == len(self.desired_fields)


@pytest.mark.vcr()
class TestDailyProgrammerTableBasic:
    def setup(self):
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

    def test_mentorship_affiliation_table_has_all_desired_fields(self) -> None:
        for field in self.airtable_fields:
            assert field in self.desired_fields

    def test_mentorship_affiliation_table_has_correct_number_of_fields(self) -> None:
        assert len(self.airtable_fields) == len(self.desired_fields)
