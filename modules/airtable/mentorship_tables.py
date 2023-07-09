"""This module contains the Airtable tables for the mentorship program."""  # noqa: D404
import logging
from functools import cached_property
from itertools import chain
from typing import Any

from pydantic.error_wrappers import ValidationError

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

    def __init__(self) -> None:  # noqa: ANN101, D107
        super().__init__("Affiliations")

    @cached_property
    def valid_affiliations(self) -> list[MentorshipAffiliation]:  # noqa: ANN101
        """Return the valid affiliations from the table.

        :return: A list of valid affiliations.
        """
        return [self.parse_affiliation_row(row) for row in self.all(view="Valid")]

    @staticmethod
    def parse_affiliation_row(row: dict[str, Any]) -> MentorshipAffiliation:  # noqa: D102
        fields = {snake_case(k): v for k, v in row["fields"].items()}
        try:
            return MentorshipAffiliation(
                **fields,
                airtable_id=row["id"],
                created_at=row["createdTime"],
            )
        except ValidationError as validation_exception:
            logger.exception("Error parsing affiliation row", extra={"row": row})
            raise validation_exception from validation_exception


class MentorshipMentorsTable(BaseAirtableTable):  # noqa: D101
    def __init__(self):  # noqa: ANN101, ANN204, D107
        super().__init__("Mentors")

    @cached_property
    def valid_mentors(self) -> list[Mentor]:  # noqa: ANN101
        """Returns the mentors from the table sorted by row ID.

        :return: list of mentors
        :rtype: list[Mentor]
        """
        try:
            return [self.parse_mentor_row(row) for row in self.all(view="Valid")]
        except ValidationError as valid_e:
            raise valid_e  # noqa: TRY201

    @staticmethod
    def parse_mentor_row(row: dict[str, Any]) -> Mentor:  # noqa: D102
        fields = {snake_case(k): v for k, v in row["fields"].items()}
        try:
            return Mentor(
                **fields,
                airtable_id=row["id"],
                created_at=row["createdTime"],
            )
        except ValidationError as valid_e:
            raise valid_e  # noqa: TRY201


class MentorshipSkillsetsTable(BaseAirtableTable):  # noqa: D101
    def __init__(self):  # noqa: ANN101, ANN204, D107
        super().__init__("Skillsets")

    @cached_property
    def valid_skillsets(self) -> list[MentorshipSkillset]:  # noqa: ANN101
        """Returns the skillsets from the table.

        :return: list of skillsets
        :rtype: list[MentorshipSkillset]
        """
        try:
            return [self.parse_skillset_row(row) for row in self.all(view="Valid")]
        except ValidationError as valid_e:
            raise valid_e  # noqa: TRY201

    @cached_property
    def mentors_by_skillsets(self) -> dict[str, str]:  # noqa: ANN101, D102
        try:
            mentors_by_skillset = {}
            for row in self.all(fields=["Name", "Mentors"], view="Valid"):
                mentors_by_skillset[row["Name"]] = row["Mentors"]
            return mentors_by_skillset  # noqa: TRY300
        except Exception as e:
            logger.warning(f"Issue retrieving mentor IDs by skillset: {e}")  # noqa: G004
            raise e  # noqa: TRY201

    @staticmethod
    def parse_skillset_row(row: dict[str, Any]) -> MentorshipSkillset:  # noqa: D102
        fields = {snake_case(k): v for k, v in row["fields"].items()}
        try:
            return MentorshipSkillset(
                **fields,
                airtable_id=row["id"],
                created_at=row["createdTime"],
            )
        except ValidationError as valid_e:
            raise valid_e  # noqa: TRY201

    def mentors_by_skillset(self, skillsets_to_search: list[str]) -> set[str]:  # noqa: ANN101
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
                except KeyError as key_e:
                    logger.warning(f"Key error intercepted: {key_e}")  # noqa: G004
                    pass

            # Flatten the array and get unique values
            return set(chain(*mentors))
        except Exception as e:
            logger.exception(
                "Issue retrieving mentor IDs with particular skillsets",
                extra={"error": e, "skillsets": skillsets_to_search},
            )
            raise e from e


class MentorshipServicesTable(BaseAirtableTable):  # noqa: D101
    def __init__(self):  # noqa: ANN101, ANN204, D107
        super().__init__("Services")

    @cached_property
    def valid_services(self) -> list[MentorshipService]:  # noqa: ANN101
        """Returns the services from the table.

        :return: list of services from the table
        :rtype: list[MentorshipService]
        """
        try:
            return [self.parse_service_row(row) for row in self.all(view="Valid")]
        except ValidationError as valid_e:
            raise valid_e  # noqa: TRY201

    @staticmethod
    def parse_service_row(row: dict[str, Any]) -> MentorshipService:  # noqa: D102
        fields = {snake_case(k): v for k, v in row["fields"].items()}
        try:
            return MentorshipService(
                **fields,
                airtable_id=row["id"],
                created_at=row["createdTime"],
            )
        except ValidationError as valid_e:
            raise valid_e  # noqa: TRY201


class MentorshipRequestsTable(BaseAirtableTable):  # noqa: D101
    def __init__(self):  # noqa: ANN101, ANN204, D107
        super().__init__("Mentor Requests")

    @cached_property
    def valid_services(self) -> list[MentorshipRequest]:  # noqa: ANN101
        """Returns the services from the table.

        :return: list of services from the table
        :rtype: list[MentorshipService]
        """
        try:
            return [self.parse_request_row(row) for row in self.all(view="Valid")]
        except ValidationError as valid_e:
            raise valid_e  # noqa: TRY201

    @staticmethod
    def parse_request_row(row: dict[str, Any]) -> MentorshipRequest:  # noqa: D102
        fields = {snake_case(k): v for k, v in row["fields"].items()}
        try:
            return MentorshipRequest(
                **fields,
                airtable_id=row["id"],
                created_at=row["createdTime"],
            )
        except ValidationError as valid_e:
            raise valid_e  # noqa: TRY201

    def return_record_by_slack_message_ts(self, timestamp: str) -> MentorshipRequest:  # noqa: ANN101, D102
        row = self.first(formula=f"{{Slack Message TS}} = '{timestamp}'")
        logger.debug(f"Returned row: {row}")  # noqa: G004
        return self.parse_request_row(row)
