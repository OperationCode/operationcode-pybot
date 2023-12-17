"""Airtable tables for the mentorship program."""
import logging
from functools import cached_property
from itertools import chain
from typing import Any

from pydantic import ValidationError

from modules.airtable.shared_table import BaseAirtableTable
from modules.models.mentorship_models import (
    Mentor,
    MentorshipAffiliation,
    MentorshipRequest,
    MentorshipService,
    MentorshipSkillset,
)
from modules.utils import snake_case

logger = logging.getLogger(__name__)


class MentorshipAffiliationsTable(BaseAirtableTable):
    """Airtable table for the mentorship affiliations table."""

    def __init__(self: "MentorshipAffiliationsTable") -> None:
        """Initialize the mentorship affiliations table."""
        super().__init__("Affiliations")

    @cached_property
    def valid_affiliations(self: "MentorshipAffiliationsTable") -> list[MentorshipAffiliation]:
        """Return the valid affiliations from the table.

        :return: A list of valid affiliations.
        """
        return [self.parse_affiliation_row(row) for row in self.all(view="Valid")]

    @staticmethod
    def parse_affiliation_row(row: dict[str, Any]) -> MentorshipAffiliation:
        """Parse an affiliation row.

        :param row: The row to parse.
        :return: The parsed affiliation row.
        """
        fields = {snake_case(k): v for k, v in row["fields"].items()}
        try:
            return MentorshipAffiliation(
                **fields,
                airtable_id=row["id"],
                created_at=row["createdTime"],
            )
        except ValidationError:
            logger.exception("Error parsing affiliation row", extra={"row": row})
            raise


class MentorshipMentorsTable(BaseAirtableTable):
    """Table containing the mentors who have signed up to mentor others."""

    def __init__(self: "MentorshipMentorsTable") -> None:
        """Initialize the mentorship mentors table."""
        super().__init__("Mentors")

    @cached_property
    def valid_mentors(self: "MentorshipMentorsTable") -> list[Mentor]:
        """Returns the mentors from the table sorted by row ID.

        :return: list of mentors
        """
        try:
            return [self.parse_mentor_row(row) for row in self.all(view="Valid")]
        except ValidationError:
            logger.exception("Unable to retrieve the list of mentors")
            raise

    @staticmethod
    def parse_mentor_row(row: dict[str, Any]) -> Mentor:
        """Parse a mentor row.

        :param row: The row to parse.
        :return: The parsed row.
        """
        fields = {snake_case(k): v for k, v in row["fields"].items()}
        try:
            return Mentor(
                **fields,
                airtable_id=row["id"],
                created_at=row["createdTime"],
            )
        except ValidationError:
            logger.exception("Unable to parse mentor row.", extra={"row": row})
            raise


class MentorshipSkillsetsTable(BaseAirtableTable):
    """Airtable table for the mentorship skillsets table."""

    def __init__(self: "MentorshipSkillsetsTable") -> None:
        """Initialize the mentorship skillsets table."""
        super().__init__("Skillsets")

    @cached_property
    def valid_skillsets(self: "MentorshipSkillsetsTable") -> list[MentorshipSkillset]:
        """Returns the skillsets from the table.

        :return: The list of skillsets.
        """
        try:
            return [self.parse_skillset_row(row) for row in self.all(view="Valid")]
        except ValidationError:
            logger.exception("Unable to retrieve the list of skillsets")
            raise

    @cached_property
    def mentors_by_skillsets(self: "MentorshipSkillsetsTable") -> dict[str, str]:
        """Returns the mentors by skillset.

        :return: The mentors by skillset.
        """
        try:
            mentors_by_skillset = {}
            for row in self.all(fields=["Name", "Mentors"], view="Valid"):
                mentors_by_skillset[row["Name"]] = row["Mentors"]
            return mentors_by_skillset  # noqa: TRY300
        except Exception:
            logger.exception("Issue retrieving mentor IDs by skillset")
            raise

    @staticmethod
    def parse_skillset_row(row: dict[str, Any]) -> MentorshipSkillset:
        """Parse a skillset row.

        :param row: The row to parse.
        :return: The parsed row.
        """
        fields = {snake_case(k): v for k, v in row["fields"].items()}
        try:
            return MentorshipSkillset(
                **fields,
                airtable_id=row["id"],
                created_at=row["createdTime"],
            )
        except ValidationError:
            logger.exception("Unable to parse skillset row.", extra={"row": row})
            raise

    def mentors_by_skillset(self: "MentorshipSkillsetsTable", skillsets_to_search: list[str]) -> set[str]:
        """Retrieve mentor IDs by skillset.

        :param skillsets_to_search: The skillsets to search for.
        :return: The mentor IDs that have the skillsets.
        """
        logger.info("STAGE: Returning mentors by skillset...")
        try:
            mentors = []
            formula = [f"{{Name}} = '{skillset}'," for skillset in skillsets_to_search]
            for row in self.all(
                fields=["Name", "Mentors"],
                view="Valid",
                formula=("OR(" + "".join(formula)[:-1] + ")"),
            ):
                try:
                    mentors.append(
                        row["fields"]["Mentors"] if row["fields"]["Mentors"] else [],
                    )
                except KeyError:
                    logger.exception("Key error intercepted retrieving mentors by skillset", extra={"row": row})
                    pass

            # Flatten the array and get unique values
            return set(chain(*mentors))
        except Exception:
            logger.exception(
                "Issue retrieving mentor IDs with particular skillsets",
                extra={"skillsets": skillsets_to_search},
            )
            raise


class MentorshipServicesTable(BaseAirtableTable):
    """Airtable table for the mentorship services table."""

    def __init__(self: "MentorshipServicesTable") -> None:
        """Initialize the mentorship services table."""
        super().__init__("Services")

    @cached_property
    def valid_services(self: "MentorshipServicesTable") -> list[MentorshipService]:
        """Returns the services from the table.

        :return: The list of services from the table.
        """
        try:
            return [self.parse_service_row(row) for row in self.all(view="Valid")]
        except ValidationError:
            logger.exception("Unable to retrieve the list of services")
            raise

    @staticmethod
    def parse_service_row(row: dict[str, Any]) -> MentorshipService:
        """Parse a service row.

        :param row: The row to parse.
        :return: The parsed row.
        """
        fields = {snake_case(k): v for k, v in row["fields"].items()}
        try:
            return MentorshipService(
                **fields,
                airtable_id=row["id"],
                created_at=row["createdTime"],
            )
        except ValidationError:
            logger.exception("Unable to parse service row.", extra={"row": row})
            raise


class MentorshipRequestsTable(BaseAirtableTable):
    """Airtable table for the mentorship requests table."""

    def __init__(self: "MentorshipRequestsTable") -> None:
        """Initialize the mentorship requests table."""
        super().__init__("Mentor Requests")

    @cached_property
    def valid_services(self: "MentorshipRequestsTable") -> list[MentorshipRequest]:
        """Returns the services from the table.

        :return: list of services from the table
        """
        try:
            return [self.parse_request_row(row) for row in self.all(view="Valid")]
        except ValidationError:
            logger.exception("Unable to retrieve the list of requests")
            raise

    @staticmethod
    def parse_request_row(row: dict[str, Any]) -> MentorshipRequest:
        """Parse a request row.

        :param row: The row to parse.
        :return: The parsed row.
        """
        fields = {snake_case(k): v for k, v in row["fields"].items()}
        try:
            return MentorshipRequest(
                **fields,
                airtable_id=row["id"],
                created_at=row["createdTime"],
            )
        except ValidationError:
            logger.exception("Unable to parse request row.", extra={"row": row})
            raise

    def return_record_by_slack_message_ts(self: "MentorshipRequestsTable", timestamp: str) -> MentorshipRequest:
        """Return a specific record by the recorded timestamp.

        :param timestamp: The timestamp to use to find the record.
        :return: The mentorship request found with the timestamp.
        """
        logger.info("Returning record using timestamp", extra={"timestamp": timestamp})
        row = self.first(formula=f"{{Slack Message TS}} = '{timestamp}'")
        if not row:
            logger.error("Unable to find record", extra={"timestamp": timestamp})
            error_message = f"Unable to find record with timestamp {timestamp}"
            raise ValueError(error_message)
        logger.info("Found record", extra={"row": row})
        return self.parse_request_row(row)
