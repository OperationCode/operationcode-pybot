from typing import Any
from pydantic.error_wrappers import ValidationError

from modules.airtable.shared_table import BaseAirtableTable
from modules.models.scheduled_message_models import ScheduledMessageInfo
from modules.utils import snake_case


class ScheduledMessagesTable(BaseAirtableTable):
    def __init__(self):
        super().__init__("Scheduled Messages")

    @property
    def all_valid_scheduled_messages(self) -> list[ScheduledMessageInfo]:
        return [self.parse_scheduled_message_row(row) for row in self.all(view="Valid")]

    @staticmethod
    def parse_scheduled_message_row(row: dict[str, Any]) -> ScheduledMessageInfo:
        fields = {snake_case(k): v for k, v in row["fields"].items()}
        try:
            return ScheduledMessageInfo(
                **fields, airtable_id=row["id"], created_at=row["createdTime"]
            )
        except ValidationError as valid_e:
            raise valid_e
