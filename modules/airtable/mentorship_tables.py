import logging
from pydantic.error_wrappers import ValidationError
from typing import Any
from functools import cached_property
from itertools import chain

from modules.airtable.shared_table import BaseAirtableTable
from modules.utils import snake_case
from modules.models.mentorship_models import (
    MentorshipService,
    MentorshipSkillset,
    Mentor,
    MentorshipAffiliation,
    MentorshipRequest,
)

logger = logging.getLogger(__name__)


class MentorshipAffiliationsTable(BaseAirtableTable):
    def __init__(self):
        super().__init__("Affiliations")

    @cached_property
    def valid_affiliations(self) -> list[MentorshipAffiliation]:
        return [self.parse_affiliation_row(row) for row in self.all(view="Valid")]

    @staticmethod
    def parse_affiliation_row(row: dict[str, Any]) -> MentorshipAffiliation:
        fields = {snake_case(k): v for k, v in row["fields"].items()}
        try:
            return MentorshipAffiliation(
                **fields, airtable_id=row["id"], created_at=row["createdTime"]
            )
        except ValidationError as valid_e:
            raise valid_e


class MentorshipMentorsTable(BaseAirtableTable):
    def __init__(self):
        super().__init__("Mentors")

    @cached_property
    def valid_mentors(self) -> list[Mentor]:
        """Returns the mentors from the table sorted by row ID

        :return: list of mentors
        :rtype: list[Mentor]
        """
        try:
            return [self.parse_mentor_row(row) for row in self.all(view="Valid")]
        except ValidationError as valid_e:
            raise valid_e

    @staticmethod
    def parse_mentor_row(row: dict[str, Any]) -> Mentor:
        fields = {snake_case(k): v for k, v in row["fields"].items()}
        try:
            return Mentor(
                **fields, airtable_id=row["id"], created_at=row["createdTime"]
            )
        except ValidationError as valid_e:
            raise valid_e


class MentorshipSkillsetsTable(BaseAirtableTable):
    def __init__(self):
        super().__init__("Skillsets")

    @cached_property
    def valid_skillsets(self) -> list[MentorshipSkillset]:
        """Returns the skillsets from the table

        :return: list of skillsets
        :rtype: list[MentorshipSkillset]
        """
        try:
            return [self.parse_skillset_row(row) for row in self.all(view="Valid")]
        except ValidationError as valid_e:
            raise valid_e

    @cached_property
    def mentors_by_skillsets(self) -> dict[str, str]:
        try:
            mentors_by_skillset = {}
            for row in self.all(fields=["Name", "Mentors"], view="Valid"):
                mentors_by_skillset[row["Name"]] = row["Mentors"]
            return mentors_by_skillset
        except Exception as e:
            logger.warning(f"Issue retrieving mentor IDs by skillset: {e}")
            raise e

    @staticmethod
    def parse_skillset_row(row: dict[str, Any]) -> MentorshipSkillset:
        fields = {snake_case(k): v for k, v in row["fields"].items()}
        try:
            return MentorshipSkillset(
                **fields, airtable_id=row["id"], created_at=row["createdTime"]
            )
        except ValidationError as valid_e:
            raise valid_e

    def mentors_by_skillset(self, skillsets_to_search: list[str]) -> set[str]:
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
                        row["fields"]["Mentors"] if row["fields"]["Mentors"] else []
                    )
                except KeyError as key_e:
                    logger.warning(f"Key error intercepted: {key_e}")
                    pass

            # Flatten the array and get unique values
            return set(chain(*mentors))
        except Exception as e:
            logger.warning(
                f"Issue retrieving mentor IDs with particular skillsets: {skillsets_to_search}, error: {e}"
            )


class MentorshipServicesTable(BaseAirtableTable):
    def __init__(self):
        super().__init__("Services")

    @cached_property
    def valid_services(self) -> list[MentorshipService]:
        """Returns the services from the table

        :return: list of services from the table
        :rtype: list[MentorshipService]
        """
        try:
            return [self.parse_service_row(row) for row in self.all(view="Valid")]
        except ValidationError as valid_e:
            raise valid_e

    @staticmethod
    def parse_service_row(row: dict[str, Any]) -> MentorshipService:
        fields = {snake_case(k): v for k, v in row["fields"].items()}
        try:
            return MentorshipService(
                **fields, airtable_id=row["id"], created_at=row["createdTime"]
            )
        except ValidationError as valid_e:
            raise valid_e


class MentorshipRequestsTable(BaseAirtableTable):
    def __init__(self):
        super().__init__("Mentor Requests")

    @cached_property
    def valid_services(self) -> list[MentorshipRequest]:
        """Returns the services from the table

        :return: list of services from the table
        :rtype: list[MentorshipService]
        """
        try:
            return [self.parse_request_row(row) for row in self.all(view="Valid")]
        except ValidationError as valid_e:
            raise valid_e

    @staticmethod
    def parse_request_row(row: dict[str, Any]) -> MentorshipRequest:
        fields = {snake_case(k): v for k, v in row["fields"].items()}
        try:
            return MentorshipRequest(
                **fields, airtable_id=row["id"], created_at=row["createdTime"]
            )
        except ValidationError as valid_e:
            raise valid_e

    def return_record_by_slack_message_ts(self, timestamp: str) -> MentorshipRequest:
        row = self.first(formula=f"{{Slack Message TS}} = '{timestamp}'")
        logger.debug(f"Returned row: {row}")
        return self.parse_request_row(row)
