import logging  # noqa: D100
from typing import Any

from pydantic import ValidationError

from modules.airtable.shared_table import BaseAirtableTable
from modules.models.message_text_models import MessageTextInfo
from modules.utils import snake_case

logger = logging.getLogger(__name__)


class MessageTextTable(BaseAirtableTable):  # noqa: D101
    def __init__(self):  # noqa: ANN101, ANN204, D107
        super().__init__("Message Text")

    @staticmethod
    def parse_message_text_row(row: dict[str, Any]) -> MessageTextInfo:  # noqa: D102
        fields = {snake_case(k): v for k, v in row["fields"].items()}
        try:
            return MessageTextInfo(
                **fields,
                airtable_id=row["id"],
                created_at=row["createdTime"],
            )
        except ValidationError as valid_e:
            raise valid_e  # noqa: TRY201

    def retrieve_valid_message_row(self, message_slug: str) -> MessageTextInfo:  # noqa: ANN101, D102
        return self.parse_message_text_row(
            self.first(
                formula=f"{{Slug}} = '{message_slug}'",
                view="Valid",
            ),
        )

    def retrieve_valid_messages_by_view(  # noqa: D102
        self,  # noqa: ANN101
        view_name: str,
    ) -> dict[str, MessageTextInfo]:
        logger.info("STAGE: Retrieving valid messages by view")
        logger.debug(f"With view_name: {view_name}")  # noqa: G004
        messages = {}
        for row in self.all(view=view_name):
            parsed_row = self.parse_message_text_row(row)
            messages[parsed_row.slug] = parsed_row
        return messages
