"""Airtable table for scheduled messages."""
import logging
from typing import Any

from pydantic import ValidationError

from modules.airtable.shared_table import BaseAirtableTable
from modules.models.scheduled_message_models import ScheduledMessageInfo
from modules.utils import snake_case

logger = logging.getLogger(__name__)


class ScheduledMessagesTable(BaseAirtableTable):
    """Airtable table for scheduled messages."""

    def __init__(self: "ScheduledMessagesTable") -> None:
        """Initialize the scheduled messages table."""
        super().__init__("Scheduled Messages")

    @property
    def all_valid_scheduled_messages(self: "ScheduledMessagesTable") -> list[ScheduledMessageInfo]:
        """Return all valid scheduled messages."""
        return [self.parse_scheduled_message_row(row) for row in self.all(view="Valid")]

    @staticmethod
    def parse_scheduled_message_row(row: dict[str, Any]) -> ScheduledMessageInfo:
        """Return a parsed scheduled message row.

        :param row: The row to parse.
        :return: A parsed scheduled message row.
        """
        fields = {snake_case(k): v for k, v in row["fields"].items()}
        try:
            return ScheduledMessageInfo(
                **fields,
                airtable_id=row["id"],
                created_at=row["createdTime"],
            )

        except ValidationError:
            logger.exception("Unable to parse scheduled message row.", extra={"row": row})
            raise
