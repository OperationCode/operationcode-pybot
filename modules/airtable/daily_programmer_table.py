import logging  # noqa: D100
from typing import Any

from pydantic import ValidationError

from modules.airtable.shared_table import BaseAirtableTable
from modules.models.daily_programmer_models import DailyProgrammerInfo
from modules.utils import snake_case

logger = logging.getLogger(__name__)


class DailyProgrammerTable(BaseAirtableTable):
    """Airtable table for the daily programmer channel."""

    def __init__(self: "DailyProgrammerTable") -> None:
        """Initialize the daily programmer table."""
        super().__init__("Daily Programmer")

    @staticmethod
    def parse_daily_programmer_row(row: dict[str, Any]) -> DailyProgrammerInfo:
        """Parse a daily programmer row.

        :param row: The row to parse.
        :return: The parsed row.
        """
        fields = {snake_case(k): v for k, v in row["fields"].items()}
        try:
            return DailyProgrammerInfo(
                **fields,
                airtable_id=row["id"],
                created_at=row["createdTime"],
            )
        except ValidationError:
            logger.exception("Unable to parse daily programmer row.", extra={"row": row})
            raise

    def retrieve_valid_daily_programmer_row_by_slug(
        self: "DailyProgrammerTable",
        slug: str,
    ) -> DailyProgrammerInfo:
        """Retrieve a valid daily programmer row by slug.

        :param slug: The slug to match.
        :return: The parsed row.
        """
        return self.parse_daily_programmer_row(
            self.first(
                formula=f"{{Slug}} = '{slug}'",
                view="Valid",
            ),
        )

    def retrieve_valid_daily_programmer_by_view(
        self: "DailyProgrammerTable",
        view_name: str,
    ) -> dict[str, DailyProgrammerInfo]:
        """Retrieve all valid daily programmer rows by view.

        :param view_name: The view name to retrieve messages from.
        :return: The dictionary of messages.
        """
        logger.info("STAGE: Retrieving daily programmer rows by view")
        logger.info("With view_name", extra={"view_name": view_name})
        messages = {}
        for row in self.all(view=view_name):
            parsed_row = self.parse_daily_programmer_row(row)
            messages[parsed_row.slug] = parsed_row
        return messages
