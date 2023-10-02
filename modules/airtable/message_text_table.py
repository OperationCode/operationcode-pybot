"""Defines the message text table in Airtable."""
import logging
from typing import Any

from pydantic import ValidationError

from modules.airtable.shared_table import BaseAirtableTable
from modules.models.message_text_models import MessageTextInfo
from modules.utils import snake_case

logger = logging.getLogger(__name__)


class MessageTextTable(BaseAirtableTable):
    """The message text table contains the various messages we send out periodically in the OC Slack workspace."""

    def __init__(self: "MessageTextTable") -> None:
        """Initialize the message text table."""
        super().__init__("Message Text")

    @staticmethod
    def parse_message_text_row(row: dict[str, Any]) -> MessageTextInfo:
        """Parse a message text row.

        :param row: The row to parse.
        :return: The parsed message text row.
        """
        fields = {snake_case(k): v for k, v in row["fields"].items()}
        try:
            return MessageTextInfo(
                **fields,
                airtable_id=row["id"],
                created_at=row["createdTime"],
            )
        except ValidationError:
            logger.exception("Unable to parse message text row.", extra={"row": row})
            raise

    def retrieve_valid_message_row(self: "MessageTextTable", message_slug: str) -> MessageTextInfo:
        """Retrieve all valid messages that match the given slug.

        :param message_slug: The message slug to match.
        :return: The parsed message text row.
        """
        return self.parse_message_text_row(
            self.first(
                formula=f"{{Slug}} = '{message_slug}'",
                view="Valid",
            ),
        )

    def retrieve_valid_messages_by_view(
        self: "MessageTextTable",
        view_name: str,
    ) -> dict[str, MessageTextInfo]:
        """Retrieve a dictionary of all valid messages by view.

        :param view_name: The view name to retrieve messages from.
        :return: The dictionary of messages.
        """
        logger.info("STAGE: Retrieving valid messages by view")
        logger.info("With view_name", extra={"view_name": view_name})
        messages = {}
        for row in self.all(view=view_name):
            parsed_row = self.parse_message_text_row(row)
            messages[parsed_row.slug] = parsed_row
        return messages
